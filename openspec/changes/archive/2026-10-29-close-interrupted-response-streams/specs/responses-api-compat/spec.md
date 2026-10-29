## ADDED Requirements

### Requirement: Response adapters finalize their owned inner streams
Response normalization and error-conversion adapters MUST close their owned inner
stream when a transport error interrupts iteration, the downstream consumer closes
early, or iteration is cancelled. Closing the outer native Responses adapter MUST
reach the service generator's finalizer before returning. Cleanup MUST preserve
the original public/native error contract and MUST NOT replay the request or
transfer reservation settlement ownership.

#### Scenario: Native synthetic transport failure
- **WHEN** a native Responses stream raises after a synthetic transport failure
- **THEN** its inner service finalizer runs before the outer adapter finishes
- **AND** the original native transport error remains unchanged

#### Scenario: Consumer closes after output
- **WHEN** a consumer closes its response stream before the upstream terminal event
- **THEN** the inner service stream is closed without another upstream attempt

#### Scenario: Cancellation during streaming
- **WHEN** iteration is cancelled while awaiting an upstream event
- **THEN** owned inner streams finalize and cancellation remains observable

### Requirement: Candidate artifacts preserve deployed Desktop compatibility
Native socket I/O failures MUST remain terminal and account-neutral without
exposing private exception details. Responses validation MUST accept and forward
`output.encrypted_content` while rejecting unknown include values. The immutable
candidate MUST preserve the deployed native runtime, dependency and schema base.

#### Scenario: Native receive fails after dispatch
- **WHEN** the native helper reports a socket transport failure
- **THEN** the adapter reports an account-neutral terminal failure
- **AND** no private exception text reaches the client

#### Scenario: Desktop requests encrypted output
- **WHEN** a valid request includes `output.encrypted_content`
- **THEN** validation preserves that exact include
- **AND** unknown include values remain rejected
