## ADDED Requirements

### Requirement: Dedicated serving replicas use backend-specific startup checks

The dedicated serving factories MUST start against an initialized PostgreSQL
database without requiring a SQLite lifecycle sentinel. They MUST continue to
verify the replica identity, shared encryption key, and required bridge schema.
The SQLite lifecycle guard MUST continue to reject a missing owner when the
effective backend is SQLite.

#### Scenario: Replace an initialized PostgreSQL serving replica

- **GIVEN** the replacement has a unique replica identity and the existing PostgreSQL binding
- **WHEN** the dedicated serving factory starts
- **THEN** it validates the shared state and becomes ready without a SQLite sentinel
- **AND** it does not start primary-only schedulers

#### Scenario: SQLite store has no lifecycle owner

- **GIVEN** the effective backend is SQLite and no owner holds its sentinel
- **WHEN** the dedicated serving factory starts
- **THEN** startup fails before readiness
