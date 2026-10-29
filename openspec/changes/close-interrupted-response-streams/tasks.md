## Implementation
- [x] Reproduce incomplete stream cleanup at the native response normalization path.
- [x] Close nested response streams on terminal conversion, early close and cancellation.
- [x] Preserve settlement ownership, exception envelopes and no-replay behavior.

## Verification
- [x] Run cleanup, response-surface and existing native transport regressions.
- [x] Validate and synchronize the scoped OpenSpec requirements.
- [ ] Qualify the immutable image before any parallel serving test.
