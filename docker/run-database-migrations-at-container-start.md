# Run Database Migrations at Container Start, Not Image Build

A Docker image build should not need production database access or runtime secrets. Requiring either couples an immutable build artifact to one environment and makes builds fail outside the production network.

For a single-replica service, run blocking migrations in the entrypoint before starting the application:

```sh
#!/bin/sh
set -e

case "${DATABASE_URL:-}" in
  postgres://*|postgresql://*)
    npm run migrate
    ;;
esac

exec "$@"
```

`set -e` makes migration failure stop the deployment instead of starting incompatible application code. The final `exec` replaces the shell with the application process so signals reach it correctly.

This pattern assumes one replica starts at a time. With multiple replicas, concurrent migrations can race. Run migrations as a serialized pre-deploy job instead, protected by the deployment system or a database lock.

Build the image without the database. Supply runtime credentials only when the container starts inside the correct network.
