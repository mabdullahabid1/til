# Force Dynamic Next.js Routes After Database-Less Builds

A dynamic App Router route can fail only after deployment when the build cannot access its database.

Consider a route that pre-renders known slugs:

```typescript
export async function generateStaticParams() {
  if (!process.env.DATABASE_URL) return [];

  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```

If the build returns no parameters, the first request may trigger an ISR render. That render fails with `DYNAMIC_SERVER_USAGE` when the route or a parent layout reads request-only state such as `cookies()`.

For a route that is inherently request-dependent, make that rendering contract explicit:

```typescript
export const dynamic = "force-dynamic";

export default async function Page() {
  // Request-time APIs such as cookies() are now expected here.
}
```

Do not apply `force-dynamic` to every route. Static routes should remain static. Use it when a route genuinely depends on per-request state and a database-less build means `generateStaticParams()` cannot pre-render its paths.
