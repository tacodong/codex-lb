## ADDED Requirements

### Requirement: Serving replicas preserve the existing SQLite lifecycle owner
An explicitly selected serving-replica factory MUST require an existing SQLite
store with a live lifecycle lock owner and an explicit unique bridge identity.
It MUST NOT initialize or migrate the store, bootstrap credentials, purge shared
startup history, start singleton scheduled jobs, or write a clean-shutdown marker.
It MUST retain native inference routes, cache invalidation, model metadata,
request settlement, process-local usage ingestion and key last-used flushing.

#### Scenario: Primary remains active
- **WHEN** a serving replica starts or stops beside an active primary
- **THEN** the primary retains its lifetime lock and serves existing connections
- **AND** only the replica's local bridge and process resources are retired

#### Scenario: Primary ownership is absent
- **WHEN** the store or an active lifecycle owner is absent
- **THEN** replica startup fails without creating or initializing a store

### Requirement: Per-listener key enforcement preserves native validation
A mandatory-key serving factory MUST require a valid native API key for both
HTTP and WebSocket inference regardless of the shared global auth setting. The
ordinary serving factory MUST retain native global authentication behavior.
Neither factory MAY change shared authentication settings or restrict models,
accounts or supported request capabilities.

#### Scenario: Global key authentication is disabled
- **WHEN** a client omits a valid key on the mandatory-key listener
- **THEN** both HTTP and WebSocket inference are denied
- **AND** the ordinary listener retains its native global policy
