# Let Rate-Limit Clients Own the Cooldown

Do not replace an API client's rate-limit-aware backoff with a short fixed retry delay. If the provider asks clients to wait 60 seconds and every retry fires after two seconds, every attempt can land inside the same cooldown window.

For example, avoid overriding an SDK that already handles `429 Too Many Requests` responses:

```typescript
const client = new APIClient({
  // Avoid a fixed retry delay unless it honors Retry-After.
  // retryDelay: 2_000,
});
```

Prefer the SDK's default policy, or calculate the delay from the provider's `Retry-After` header and add jitter. Also make partial fetches fail visibly. A build that succeeds with missing records is worse than a build that stops with a useful error.

This surfaced in an abd.dev build where a fixed two-second retry kept requests inside a 60-75 second cooldown and silently omitted 17 posts. Removing the override allowed the client to wait and recover.

Source: [abd.dev PR #16](https://github.com/mabdullahabid/abd.dev/pull/16)
