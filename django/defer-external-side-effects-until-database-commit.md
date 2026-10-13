# Defer External Side Effects Until the Database Commits

Queuing an external side effect inside a database transaction can create split-brain state.

If the task is queued immediately and the transaction later rolls back, the worker can change an external system even though the corresponding local change never committed.

Use Django's `transaction.on_commit()` to enqueue the work only after a successful commit:

```python
from django.db import transaction


def update_subscription(subscription):
    subscription.status = "active"
    subscription.save(update_fields=["status"])

    subscription_id = subscription.pk
    transaction.on_commit(
        lambda: sync_subscription.delay(subscription_id)
    )
```

Capture stable identifiers before registering the callback. Do not close over a mutable model instance whose fields may change before the callback runs.

Test both sides of the boundary:

- The task is not queued before commit.
- The task is queued after commit.
- The task is never queued after rollback.

This solves commit ordering. It does not solve duplicate or out-of-order task delivery, so the task should still be idempotent where possible.
