# Probe the New Container Over Loopback

During a rolling deployment, a readiness check against the public hostname can hit the old container. A successful response then proves that the service is available, not that the new instance is ready.

When a startup script needs to verify the container currently starting, probe it over loopback:

```sh
#!/bin/sh
set -e

port="${PORT:-3000}"
health_url="http://127.0.0.1:${port}/health"

until curl --fail --silent --show-error "$health_url" >/dev/null; do
  sleep 1
done

echo "This container is ready"
```

Treat non-2xx responses as failures and keep polling until the local process is actually ready. Use the public hostname for external availability checks, where load balancer routing is part of what you want to test.

The distinction is instance identity: loopback answers "is this new container ready?" while the public URL answers "can some healthy container serve traffic?"
