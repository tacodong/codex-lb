## Implementation

- [x] Emit bounded native failure reasons without raw error strings.
- [x] Validate optional reasons and preserve them in the existing relay error evidence.
- [x] Verify backward compatibility, redaction, native wire propagation and unchanged classification.
- [x] Validate and synchronize the OpenSpec requirement.

Immutable-image qualification and any no-downtime rollout remain separate operational gates in the existing outcome6; source tests do not establish live stability.
