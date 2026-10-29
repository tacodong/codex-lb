## MODIFIED Requirements

### Requirement: Candidate artifacts preserve deployed Desktop compatibility
Native socket I/O failures MUST remain terminal and account-neutral without
exposing private exception details. Responses validation MUST accept and forward
`output.encrypted_content` while rejecting unknown include values. The immutable
candidate MUST preserve the deployed OS, dashboard, schema and native protocol
contracts. Dependency updates MUST be limited to locked fixes required by the
release security gates and their necessary dependency updates. The native helper
MUST be rebuilt from the same application source against the repaired lock and
MUST pass the native transport wire regressions before deployment.

#### Scenario: Native receive fails after dispatch
- **WHEN** the native helper reports a socket transport failure
- **THEN** the adapter reports an account-neutral terminal failure
- **AND** no private exception text reaches the client

#### Scenario: Desktop requests encrypted output
- **WHEN** a valid request includes `output.encrypted_content`
- **THEN** validation preserves that exact include
- **AND** unknown include values remain rejected
