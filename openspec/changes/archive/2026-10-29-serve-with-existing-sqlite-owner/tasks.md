## Implementation
- [x] Fence replica startup on an existing live SQLite owner and explicit identity.
- [x] Separate primary-only startup work from native serving and cache lifecycle.
- [x] Support native and mandatory-key factories with unchanged inference routes.

## Verification
- [x] Verify ownership fencing and per-listener HTTP/WebSocket authentication.
- [x] Verify serving startup/teardown preserves primary ownership and singleton jobs.
- [x] Exercise two real processes on isolated state before live activation.
