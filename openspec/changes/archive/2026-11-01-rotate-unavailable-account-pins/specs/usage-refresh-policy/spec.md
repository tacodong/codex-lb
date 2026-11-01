## REMOVED Requirements

### Requirement: Permanent refresh failure preserves request eligibility
**Reason**: A persisted authentication failure must yield to healthy accounts.
**Migration**: Native status/custody is preserved; no schema migration.

## ADDED Requirements

### Requirement: Permanent refresh failure yields request eligibility to healthy accounts

Permanent refresh credential or session errors MUST mark the account `reauth_required`. This requirement refines existing refresh-failure requirements: any instruction to remove that status from request routing, tear down affinity, or add a process-local unavailable overlay MUST defer to the canonical status matrix in `account-routing`. Proactive and background refresh MUST continue to skip known-bad refresh material.

A separate upstream account-deactivation signal MUST continue to mark the account `deactivated` and apply existing hard-unavailable behavior.

#### Scenario: Refresh failure separates access and refresh eligibility

- **WHEN** refresh-token exchange fails permanently without an account-deactivation signal
- **THEN** the account becomes `reauth_required`
- **AND** proactive refresh stops
- **AND** ordinary requests exclude the pending-auth account until native reauthentication restores Active status

#### Scenario: Account deactivation remains hard-unavailable

- **WHEN** upstream reports that the account itself is deactivated
- **THEN** the account becomes `deactivated`
- **AND** it is removed from request routing and affinity

