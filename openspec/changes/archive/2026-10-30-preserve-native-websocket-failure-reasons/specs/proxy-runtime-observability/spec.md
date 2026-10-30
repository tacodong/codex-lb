## ADDED Requirements

### Requirement: Native WebSocket errors retain bounded transport provenance
The native helper MUST emit an optional fixed failure reason for WebSocket errors. The Python boundary MUST accept absent reasons from older helpers and MUST discard unknown or non-string reasons. For recognized reasons, the relay's existing send/receive error message MUST retain the reason and a fixed recognized phase. The new diagnostic MUST exclude raw exceptions, URLs, headers, credentials and provider bodies. Classification of other failures MUST remain unchanged.

#### Scenario: Unexpected upstream termination
- **WHEN** a native WebSocket fails with a connection reset, unexpected EOF, missing close handshake, TLS failure, liveness timeout or protocol failure
- **THEN** the helper emits a bounded reason and the relay preserves it in the error evidence
- **AND** the original account-neutral classification and retry semantics remain unchanged

#### Scenario: Older or untrusted helper metadata
- **WHEN** a WebSocket error omits the reason or supplies an unknown or non-string reason
- **THEN** Python preserves the previous generic error behavior without exposing that metadata


### Requirement: Abrupt native WebSocket closure is account neutral
Native missing-close-handshake and already-closed transport failures MUST use the existing account-neutral terminal path. The gateway MUST release the request reservation without penalizing the selected account or transparently replaying an ambiguously sent request. Other protocol failures MUST retain their existing classification.

#### Scenario: Native peer EOF after response create was sent
- **WHEN** the helper reports `close_without_handshake` or `connection_closed` in the protocol phase
- **THEN** the relay preserves its safe evidence and uses account-neutral terminal handling
- **AND** the pending request is finalized once, its reservation released, and no replay or account-health penalty occurs
