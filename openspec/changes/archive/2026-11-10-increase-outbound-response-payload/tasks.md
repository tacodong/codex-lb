## Implementation
- [x] Separate outbound 128MiB request budget from 16MiB received-event budget.
- [x] Cover 24MiB current-user input through both public WebSocket routes without slimming.
- [x] Keep over-budget rejection tests and update specifications/image packaging.
- [x] Run affected tests and required CI/review; publish and integrate.
- [x] Qualify immutable image and deploy connection-preserving serving generation; verify affected path.

## Accepted verification
219 route/client tests, seven packaging tests, lint/types and strict change plus
65 canonical-spec checks passed. Current-head CI42914243124 passed; PR8 merged
as11dcb9da13ce288535c4f83554a69c25dca33429. Runtime artifact source85b22e83
was qualified/scanned and deployed; later source changes were tests only. Both
ordinary/keyed listeners and the configured Mac tunnel completed24MiB requests
and continuations. Six retained listener lifecycles were preserved. Operational
receipt: tacodong/homelabPR2237, merged0f749dc291a3733861ea5cda758cb7320bff5ba0.
Full128MiB inference and reboot remain untested; the existing parent boot guard
was preserved.
