# Prove a Simulator Matches Production with Parity Tests

A diagnostic simulator becomes dangerous when it independently reimplements production logic. Both versions can return plausible answers while quietly drifting apart.

Make production and the simulator call the same domain function:

```python
def calculate_quote(request):
    item = select_item(request)
    return {
        "item_id": item.id,
        "delivery_total": delivery_total(item, request),
        "pickup_total": pickup_total(item, request),
    }

def production_quote(request):
    return calculate_quote(request)

def simulator_quote(request):
    return calculate_quote(request)
```

Then add a parity test against the real production entry point:

```python
def test_simulator_matches_production(sample_request):
    expected = production_quote(sample_request)
    actual = simulator_quote(sample_request)

    assert actual["item_id"] == expected["item_id"]
    assert actual["delivery_total"] == expected["delivery_total"]
    assert actual["pickup_total"] == expected["pickup_total"]
```

Compare the decisions that matter, including ordering, the selected entity, and calculated outputs. Merely asserting that both paths return successfully will not catch a simulator using a different formula.

Explanatory breakdowns can remain simulator-specific, but any value presented as production-equivalent should be derived from or pinned against production behavior.
