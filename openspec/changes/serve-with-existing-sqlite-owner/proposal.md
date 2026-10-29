## Why

A full second startup cannot share the primary SQLite lifetime lock. Replacing
the primary would interrupt active listeners. A serving-only replica is needed
to roll out the qualified stream repair while retaining the current database
lifecycle and singleton-job owner.

## What Changes

- Add explicit native serving factories using an existing, actively owned SQLite
  store. They do not migrate, bootstrap, purge global startup history or start
  singleton jobs, and never write the primary's clean-shutdown marker.
- Reuse the native cache bus, model registry, bridge membership, account selection,
  transport, request persistence and process-local usage/key flush mechanisms.
- Preserve both existing authentication policies: native global policy for the
  main listener and mandatory keys for the keyed listener, without changing the
  shared dashboard setting.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: non-disruptive serving process lifecycle.

## Constraints

This mode requires the same local SQLite store and an active lifecycle owner. It
is an explicit serving role, not an automatic takeover or a database migration.
The controller must keep the primary online and assign a unique bridge identity.
