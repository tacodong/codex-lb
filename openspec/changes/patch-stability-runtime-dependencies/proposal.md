## Why

The required image scan rejects the beta.9 lock for fixed denial-of-service
vulnerabilities in aiohttp, dnspython and urllib3. The stability artifact must
include the minimum fixed dependencies rather than bypassing that gate.

## What Changes

Update only those three libraries plus the yarl version required by aiohttp and install those exact versions on
the pinned runtime base. Native helper, schema and application repairs remain
unchanged.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: qualified runtime dependency boundary.
