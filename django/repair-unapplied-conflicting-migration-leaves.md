# Repair Unapplied Conflicting Django Migration Leaves Safely

Parallel branches can create Django migrations with the same number and parent. After both branches merge, the app has two leaf migrations and Django reports a conflict.

Before renaming anything, check what the affected environment has already applied:

```bash
python manage.py showmigrations billing
```

If one leaf is applied and the other is not, the unapplied migration can be moved after the applied one:

1. Rename the unapplied migration to the next available number.
2. Change its dependency to the applied sibling.
3. Keep its operations unchanged.

```python
dependencies = [
    ("billing", "0117_existing_change"),
]
```

Then verify the repaired chain:

```bash
python manage.py showmigrations billing
python manage.py makemigrations --check
python manage.py migrate
```

Also run `migrate` against an empty database in CI. That proves a fresh install can traverse the whole graph.

If both conflicting leaves have been applied anywhere, do not rewrite migration history. Create a merge migration instead.
