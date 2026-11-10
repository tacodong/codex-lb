## ADDED Requirements

### Requirement: Outbound Responses payload budget is independent of received events
The service MUST accept serialized outbound response.create payloads up to the existing 128MiB Responses ingress budget without applying the 16MiB received-event limit to them. Received SSE and WebSocket events MUST retain their 16MiB budget. Historical slimming and local 400 payload_too_large errors MUST continue to apply only when the serialized request exceeds the outbound request budget.

#### Scenario: Screenshot-heavy current turn exceeds the old request budget
- **WHEN** a 24MiB request is sent through /v1/responses or /backend-api/codex/responses over WebSocket
- **THEN** its current-user input is forwarded without byte-budget slimming or local payload_too_large rejection
- **AND** the received-event budget remains 16MiB
