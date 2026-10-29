# Verification

- Base: deployed beta.9 source `69f128afcbc616d9f8e924ca6583f7031d75cf82`.
- Cleanup regressions failed before the repair and pass afterward.
- 222 affected-path tests passed, including native/public response routes, native
  burst buffering, WebSocket adapters, fallback and Desktop compatibility.
- Architecture, cancellation safety, timing seams, setting tiers and migration
  topology checks passed. Ruff and full Python type checking passed.
- Canonical OpenSpec and both changes pass strict validation.
- Queue implementation is backported from upstream PR #2635 commits
  `cc29e632e1f2d69a170121d1060da46e44379eb7` and
  `09357247d7e9c2e9e99f94259fdbb8874f10a2d4`.
- HTTP closure is independently scoped to the three adapters using the existing
  close helper; unrelated error remapping from upstream PR #2472 is excluded.
- Pending: immutable image qualification and native-helper wire regression.
  No production rollout or long-running client stability is claimed.
