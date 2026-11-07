## ADDED Requirements

### Requirement: Consume outcomes accurately distinguish resets from no-ops

The shared reset-credit client MUST accept an explicitly null `credit` on a consume response while requiring `code`, `credit` and `windows_reset` fields. The serialized redemption helper MUST log the upstream code and reset-window count for every parsed consume result. A non-reset or zero-window outcome MUST be logged at warning level. A no-op response MUST NOT be reported as consuming a credit. Reported availability MUST be decremented only for a `reset` response when the fresh pre-consume snapshot listed the selected credit as available.

All consume outcomes, including `nothing_to_reset`, MUST preserve the existing request-to-credit binding and automatic duplicate-consume guard. A later retry using the same request id MUST NOT select a different credit because a prior result was a no-op.

#### Scenario: No-credit response is valid
- **WHEN** upstream returns HTTP 200 with `code = "no_credit"`, `credit = null` and zero windows
- **THEN** the client and dashboard return that outcome without a malformed-payload error
- **AND** no credit consumption is inferred

#### Scenario: Upstream declines to reset an available credit
- **WHEN** upstream returns `nothing_to_reset`, zero windows and the selected credit still available
- **THEN** the outcome is logged as a warning with its code and window count
- **AND** reported availability is unchanged
- **AND** the durable request binding and automatic duplicate-consume guard remain intact

#### Scenario: Successful retry does not double-count availability
- **GIVEN** a retry is durably pinned to a previously consumed credit
- **WHEN** the fresh pre-consume snapshot no longer lists that credit as available
- **THEN** the response does not subtract another credit from that snapshot's reported availability
