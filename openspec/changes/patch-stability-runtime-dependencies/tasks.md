## Implementation
- [x] Update the three vulnerable libraries and required yarl dependency and candidate packaging.
- [x] Synchronize the compatibility constraint and rationale.

## Verification
- [x] Run affected HTTP/WebSocket tests against the updated dependency set.
- [ ] Build and qualify the updated image and satisfy the required image scan.

## Native and remaining Python gate repairs
- [x] Update brotli/certifi and the audited native dependency versions.
- [ ] Rebuild the unchanged native source with the repaired lock.
- [ ] Run native unit/wire regressions and requalify the candidate artifact.
