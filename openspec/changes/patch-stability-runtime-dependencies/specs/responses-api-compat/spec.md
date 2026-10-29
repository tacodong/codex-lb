## MODIFIED Requirements

### Requirement: Candidate artifacts preserve deployed Desktop compatibility
Native socket I/O failures MUST remain terminal and account-neutral without
exposing private exception details. Responses validation MUST accept and forward
`output.encrypted_content` while rejecting unknown include values. The immutable
candidate MUST preserve the deployed native runtime, helper and schema base.
Dependency updates MUST be limited to the locked fixes required by the image
security gate and MUST pass the affected transport regressions.

#### Scenario: Native receive fails after dispatch
- **WHEN** the native helper reports a socket transport failure
- **THEN** the adapter reports an account-neutral terminal failure
- **AND** no private exception text reaches the client

#### Scenario: Desktop requests encrypted output
- **WHEN** a valid request includes `output.encrypted_content`
- **THEN** validation preserves that exact include
- **AND** unknown include values remain rejected
