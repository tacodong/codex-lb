## Why

An interrupted native HTTP stream can raise from the public response normalizer
without closing the nested service generators. Their finalizers own transport
cleanup and account-lease release (upstream issue #2470).

## What Changes

- Cascade stream closure through response normalization and error conversion.
- Preserve native/public error envelopes, cancellation and existing settlement ownership.
- Test synthetic transport failure, early consumer close and cancellation without network calls.
- Carry the deployed account-neutral native socket classification and Desktop
  encrypted-output include compatibility in the application artifact.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: prompt finalization of interrupted response streams.

## Impact

Application stream adapters and regression tests only. No schema, settings,
account-selection, retry, replay or upstream protocol changes. The candidate
image layers only the qualified application files on the pinned deployed runtime.
