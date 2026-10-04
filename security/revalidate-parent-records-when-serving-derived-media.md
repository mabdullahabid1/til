# Revalidate Parent Records When Serving Derived Media

Checking approval only when derived media is created is insufficient. If the parent record is later revoked, deleted, or purged, stale OCR text, transcripts, thumbnails, or embeddings can remain available until a cleanup job runs.

Enforce the parent's current state at the read boundary:

```python
def get_derived_text(item):
    parent = item.parent
    if parent.deleted_at or parent.revoked_at or not parent.is_approved:
        raise PermissionError("source is no longer available")
    return item.text
```

Background reconciliation is still useful for cleanup, but it should not be the authorization boundary. The read path must fail closed using the parent's current state.
