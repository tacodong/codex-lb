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
- Immutable ARM64 candidate qualified with the bundled native helper: 20 persistent
  turns, 5120 ordered frames, send acknowledgements progress while receive queues
  are full. Raw and interpreted modes pass. Native/public cleanup each finalizes
  once while preserving its error contract. Network disabled; no production mounts.
- Image ID: `sha256:3789fb4103aa022082dd7a97b8aa477c3160bffaff9d29118fc752f1b4864dac`.
- No production rollout or long-running client stability is claimed.
