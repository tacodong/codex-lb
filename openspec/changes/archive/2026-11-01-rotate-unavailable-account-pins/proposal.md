# Rotate unavailable account pins

## Why

DX repeatedly selected accounts whose native status already required reauthentication, then failed on their revoked credentials. Keeping those accounts eligible until JWT expiry prevents existing unavailable-owner recovery from acting promptly.

## What Changes

Reauthentication-required accounts become unavailable for new requests and bridge reuse. Existing soft-pin failover and proof-gated full-context owner retirement select healthy accounts. The account status and stored credentials remain unchanged until native reauthentication succeeds.

## Boundaries

Do not blindly reassign account-owned response IDs or files. Retain complete-history proof, account scopes, model/security policy, reservation settlement and no replay after ambiguous acceptance. Existing listeners remain running during any parallel rollout.
