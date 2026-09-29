# Initialize PostHog Before Next.js Hydration

If a page captures analytics in its first effect, initializing PostHog from a provider `useEffect` can be too late. In a Next.js App Router application, initialize PostHog in `instrumentation-client.ts`, which runs before the application hydrates.

```typescript
// instrumentation-client.ts
import posthog from "posthog-js";

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: "/ingest",
  capture_pageview: false,
});
```

This prevents the page's initial capture from running before `posthog.init()` and being silently discarded.
