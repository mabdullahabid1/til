"""
Embed every TIL with an Azure OpenAI embedding deployment, then store the
top related TILs for each one in the `similarities` table.

Needs AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY and
AZURE_OPENAI_EMBEDDING_DEPLOYMENT (AZURE_OPENAI_API_VERSION is optional).
"""

import hashlib
import math
import os
import pathlib
import struct
import time

import httpx
import sqlite_utils

root = pathlib.Path(__file__).parent.resolve()
API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
RELATED_COUNT = 10
# Embedding models accept ~8k tokens; ~4 characters per token keeps us under
MAX_CHARS = 24_000
# Keeps each request well under small tokens-per-minute quotas
BATCH_CHARS = 24_000
MAX_RETRIES = 8


def encode(values):
    return struct.pack("f" * len(values), *values)


def decode(blob):
    return struct.unpack("f" * (len(blob) // 4), blob)


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def fetch_embeddings(texts):
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    for attempt in range(MAX_RETRIES + 1):
        response = httpx.post(
            f"{endpoint}/openai/deployments/{deployment}/embeddings",
            params={"api-version": API_VERSION},
            headers={"api-key": os.environ["AZURE_OPENAI_API_KEY"]},
            json={"input": texts},
            timeout=120,
        )
        if response.status_code != 429 or attempt == MAX_RETRIES:
            break
        # Azure says how long to wait when the deployment's quota is used up
        wait = float(response.headers.get("retry-after", 2**attempt))
        print(f"Rate limited, retrying in {wait:.0f}s")
        time.sleep(min(wait, 90))
    response.raise_for_status()
    data = sorted(response.json()["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in data]


def build_embeddings(db):
    model = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    embeddings = db.table("embeddings", pk="id")
    existing = {}
    if embeddings.exists():
        columns = embeddings.columns_dict
        if "model" in columns and "content_hash" in columns:
            existing = {
                row["id"]: (row["model"], row["content_hash"])
                for row in embeddings.rows
            }

    todo = []
    for row in db["til"].rows:
        text = " ".join(
            [row["title"] or "", row["topic"] or "", row["body"] or ""]
        )[:MAX_CHARS]
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        # Vectors from different models can't be compared, so a model change
        # re-embeds everything
        if existing.get(row["path"]) != (model, content_hash):
            todo.append((row["path"], text, content_hash))

    batches, batch, size = [], [], 0
    for item in todo:
        if batch and (len(batch) == 16 or size + len(item[1]) > BATCH_CHARS):
            batches.append(batch)
            batch, size = [], 0
        batch.append(item)
        size += len(item[1])
    if batch:
        batches.append(batch)

    for batch in batches:
        vectors = fetch_embeddings([text for _, text, _ in batch])
        embeddings.upsert_all(
            [
                {
                    "id": path,
                    "embedding": encode(vector),
                    "model": model,
                    "content_hash": content_hash,
                }
                for (path, _, content_hash), vector in zip(batch, vectors)
            ],
            pk="id",
            alter=True,
        )
    print(f"Embedded {len(todo)} TILs with {model}")

    # Drop embeddings for deleted TILs or from another model
    paths = {row["path"] for row in db["til"].rows}
    for row in list(embeddings.rows):
        if row["id"] not in paths or row.get("model") != model:
            embeddings.delete(row["id"])


def build_similarities(db):
    vectors = [(row["id"], decode(row["embedding"])) for row in db["embeddings"].rows]
    rows = []
    for path, vector in vectors:
        scores = sorted(
            (
                (other_path, cosine_similarity(vector, other_vector))
                for other_path, other_vector in vectors
                if other_path != path
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        rows.extend(
            {"id": path, "other_id": other_path, "score": score}
            for other_path, score in scores[:RELATED_COUNT]
        )
    with db.conn:
        db["similarities"].drop(ignore=True)
        db["similarities"].insert_all(rows, pk=("id", "other_id"))
    print(f"Stored {len(rows)} similarities for {len(vectors)} TILs")


if __name__ == "__main__":
    db = sqlite_utils.Database(root / "tils.db")
    build_embeddings(db)
    build_similarities(db)
