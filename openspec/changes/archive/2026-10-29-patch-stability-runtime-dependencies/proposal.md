## Why

Required release audits reject the beta.9 dependency locks for fixed HTTP, DNS,
decompression, certificate-trust, TLS and async I/O vulnerabilities. The stream
repairs need a releasable artifact without bypassing those gates.

## What Changes

- Update aiohttp, dnspython, urllib3, brotli and certifi, plus yarl required by aiohttp.
- Apply scoped native TLS, async I/O and decompression dependency updates, following
  upstream rustls #2622 and its crypto-provider prerequisite where applicable.
- Rebuild the same native source against the repaired lock. Preserve the native
  protocol, replay/routing behavior, dashboard, OS distribution/runtime ABI and database schema.
- Apply only the fixed pcre2/OpenSSL packages required by the candidate image scan.
- Publish a scanned ARM64 candidate from trusted stability branches with a
  source-SHA tag and a per-job package-write token. Publication does not deploy.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: qualified runtime dependency and artifact boundary.

## Verification

Requalify the rebuilt native helper and candidate before serving production
requests. The original helper-preservation constraint no longer applies because
the required audits identify fixed vulnerabilities in its bundled dependencies.
