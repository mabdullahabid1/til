# dict.get Defaults Only Apply to Missing Keys

The default passed to `dict.get()` is returned only when the key is absent. If the key exists with a value of `None`, the result is still `None`.

```python
item = {"subject": None}

assert item.get("subject", "") is None
assert (item.get("subject") or "") == ""
```

Use `item.get(key) or ""` when both a missing key and a null value should become an empty string. Use an explicit `is None` check when other falsey values such as `0`, `False`, or an empty list must be preserved.
