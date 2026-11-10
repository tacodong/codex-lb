## Implementation
- [x] Separate outbound 128MiB request budget from 16MiB received-event budget.
- [x] Cover 24MiB current-user input through both public WebSocket routes without slimming.
- [x] Keep over-budget rejection tests and update specifications/image packaging.
- [ ] Run affected tests and required CI/review; publish and integrate.
- [ ] Qualify immutable image and deploy connection-preserving serving generation; verify affected path.
