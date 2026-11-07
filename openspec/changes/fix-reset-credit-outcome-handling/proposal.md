## Why

Valid upstream no-credit responses with a null credit are incorrectly rejected as malformed. Automatic reset redemption discards the returned outcome, and audit accounting incorrectly reports that every response consumes a credit. Operators cannot distinguish a completed reset from a no-op.

## What Changes

- Accept explicit null credit values in upstream consume responses.
- Log actual reset and no-op outcomes without equating an attempt with success.
- Stop decrementing reported availability for no-op responses.
- Preserve all existing request-to-credit bindings and automatic replay protection.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rate-limit-reset-credits`: accurately handle and report upstream no-op outcomes.

## Impact

Shared upstream parser, serialized redemption helper, and client/API regression tests. No schema, settings, UI, credentials or routing changes. This cannot force an upstream provider to reset an ineligible window.
