# Circular Time Windows Need Sequence Order

Numeric `min()` and `max()` cannot describe a contiguous time window that crosses midnight.

For this ordered sequence:

```python
window_hours = [22, 23, 0, 1]
```

`min(window_hours)` is `0` and `max(window_hours)` is `23`, which looks like an all-day range. The actual window starts at 22:00 and ends at 02:00.

When the input is an ordered contiguous sequence, preserve that order:

```python
start_hour = window_hours[0]
end_hour = (window_hours[-1] + 1) % 24

assert start_hour == 22
assert end_hour == 2
```

The modulo operation maps the hour after `23` back to `0`.

This only works when the list is already ordered along the intended circular window. For an unordered set of active hours, there may be multiple gaps and no single unambiguous start or end. Normalize or validate the sequence before deriving its boundaries.
