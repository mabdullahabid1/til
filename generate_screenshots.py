import hashlib
import pathlib
import subprocess
import sqlite_utils
import tempfile

import httpx

root = pathlib.Path(__file__).parent.resolve()
TMP_PATH = pathlib.Path(tempfile.gettempdir())
# Screenshots ship inside the Datasette image and are served from /shots/
SHOTS_PATH = root / "shots"
LIVE_SHOTS_URL = "https://til.abd.dev/shots/{}"
SHOT_HASH_PATHS = [
    (root / "templates" / "pages" / "{topic}" / "{slug}.html"),
    (root / "templates" / "til_base.html"),
]


def jpeg_for_path(path):
    page_html = str(TMP_PATH / "generate-screenshots-page.html")
    # Use datasette to generate HTML
    proc = subprocess.run(["datasette", ".", "--get", path], capture_output=True)
    open(page_html, "wb").write(proc.stdout)
    # Now use shot-scraper to generate a PNG
    proc2 = subprocess.run(
        [
            "shot-scraper",
            "shot",
            page_html,
            "-w",
            "800",
            "-h",
            "400",
            "--retina",
            "--quality",
            "60",
            "-o",
            "-",
        ],
        capture_output=True,
    )
    return proc2.stdout


def download_live_shot(shot_filename):
    # Reuse the screenshot the live site already serves, if it has one
    try:
        response = httpx.get(LIVE_SHOTS_URL.format(shot_filename), timeout=30)
    except httpx.HTTPError:
        return None
    if response.status_code == 200 and response.content[:2] == b"\xff\xd8":
        return response.content
    return None


def generate_screenshots(root):
    db = sqlite_utils.Database(root / "tils.db")
    SHOTS_PATH.mkdir(exist_ok=True)

    # If the old 'shot' column exists, drop it
    if "shot" in db["til"].columns_dict:
        db["til"].transform(drop=["shot"])

    # shot_hash incorporates a hash of key templates
    shot_html_hash = hashlib.md5()
    for filepath in SHOT_HASH_PATHS:
        shot_html_hash.update(filepath.read_text().encode("utf-8"))
    shot_html_hash = shot_html_hash.hexdigest()

    for row in db["til"].rows:
        path = row["path"]
        html = row["html"]
        shot_hash = hashlib.md5((shot_html_hash + html).encode("utf-8")).hexdigest()
        shot_filename = "{}.jpg".format(shot_hash)
        shot_path = SHOTS_PATH / shot_filename
        jpeg = None if shot_path.exists() else download_live_shot(shot_filename)
        if jpeg:
            print("Downloaded {} from the live site".format(shot_filename))
        elif not shot_path.exists():
            jpeg = jpeg_for_path("/{}/{}".format(row["topic"], row["slug"]))
            print(
                "Generated {} byte JPEG for {} shot hash {}".format(
                    len(jpeg), path, shot_hash
                )
            )
        if jpeg:
            shot_path.write_bytes(jpeg)
        if shot_hash != row.get("shot_hash"):
            db["til"].update(path, {"shot_hash": shot_hash}, alter=True)


if __name__ == "__main__":
    generate_screenshots(root)
