## REMOVED Requirements

### Requirement: Re-authentication-required accounts remain request-routable
**Reason**: Pending authentication failures must no longer trap requests until JWT expiry.
**Migration**: Keep pending accounts and credentials; request selection changes without a schema migration.

## ADDED Requirements

### Requirement: Pending-auth account pins yield to eligible accounts
The system MUST exclude `reauth_required` accounts from new request selection and live HTTP-bridge reuse, including when a stored JWT has not expired. Native reauthentication MUST restore eligibility when the account becomes Active. A pending status MUST NOT be cleared by routing recovery or by rewriting credentials.

#### Scenario: Failed soft-pin owner has an unexpired JWT
- **GIVEN** a soft pin points to a `reauth_required` account and another eligible account exists
- **WHEN** a new request selects an account
- **THEN** the request selects an eligible replacement through the existing soft-affinity path
- **AND** the pending account receives no upstream request

#### Scenario: Account-owned state cannot be rebuilt
- **GIVEN** a request depends on an unavailable account's file or stored response
- **AND** the existing complete-history recovery proof does not hold
- **THEN** the system preserves the hard ownership boundary and fails without replaying the request on another account


#### Scenario: Repaired account returns to service
- **GIVEN** an account was excluded while reauthentication was pending
- **WHEN** native reauthentication makes the account Active
- **THEN** it is eligible under the unchanged model, quota and account-scope policy
