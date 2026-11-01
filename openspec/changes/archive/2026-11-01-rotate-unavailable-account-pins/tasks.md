## Source verification

- [x] Reproduce pending-auth selection/bridge-reuse/soft-thread-pin failures before the patch.
- [x] Exclude pending-auth accounts before JWT expiry and persist movable cache/thread replacements.
- [x] Preserve existing owner-retirement and replay-proof boundaries; 483 initial focused tests and435 follow-up routing/cache/warmup/capacity/refresh integration tests pass, three pre-existing skips in each slice.
- [x] Propagate guarded pending-auth status through the cross-replica routing cache; exclude warmup and report authentication before capacity.
- [x] Synchronize account-routing and refresh-policy requirements; validate and type/lint-check the source.

Current-head cloud checks, immutable-image qualification and the no-downtime native rollout remain separate operational gates in shared outcome6.
