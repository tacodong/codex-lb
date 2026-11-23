## ADDED Requirements

### Requirement: Dedicated serving replicas load the shared client version

Dedicated serving replicas that skip the primary schedulers MUST read the shared
Codex client version snapshot before accepting traffic and when reconciling a
model registry invalidation. A missing, invalid, or older snapshot MUST preserve
the last usable version or the configured fallback. Serving replicas MUST NOT
start primary schedulers or perform network or file reads on the inference path
to resolve the version.

#### Scenario: SDK request on a newly started serving replica

- **GIVEN** the primary has persisted a version newer than the configured fallback
- **WHEN** a dedicated serving replica starts and forwards an SDK request
- **THEN** it uses the persisted version in the outbound User-Agent and version headers

#### Scenario: New catalogue on an existing serving replica

- **GIVEN** the primary has persisted a newer client version
- **WHEN** the dedicated serving replica reconciles a model registry invalidation
- **THEN** subsequent SDK requests use the newer persisted version
