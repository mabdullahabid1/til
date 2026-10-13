# A FileField Cannot Use an Auto Primary Key on First Save

Django resolves a `FileField`'s `upload_to` path before inserting a new model row. An auto-incrementing primary key does not exist yet, so `instance.pk` is `None` on the first save.

This looks reasonable but cannot produce a filename based on the new row's ID:

```python
def upload_to(instance, filename):
    extension = filename.rsplit(".", 1)[-1]
    return f"photos/{instance.pk}.{extension}"
```

For new objects, that path starts with `photos/None`.

Use a value available before the insert, such as a UUID:

```python
import os
import uuid


def upload_to(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    return f"photos/{uuid.uuid4().hex}{extension}"
```

If the filename must contain the database primary key, save the row first and attach the file in a second save. That adds another write, so a generated stable identifier is usually simpler.
