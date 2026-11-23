# Support PostgreSQL on dedicated serving replicas

Dedicated serving factories currently require a local SQLite owner sentinel
before checking their shared bridge schema. The sentinel verifies SQLite
lifecycle ownership and has no equivalent in the supported PostgreSQL topology.
Replacing a replica already serving against PostgreSQL therefore requires a
container-local override.

Recognize PostgreSQL in the startup guard. Keep the existing SQLite guard and
the shared encryption, identity, and bridge schema checks.
