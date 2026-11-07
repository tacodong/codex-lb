## 1. Implementation

- [x] 1.1 Accept valid null-credit consume responses and preserve required fields.
- [x] 1.2 Record actual upstream outcomes and correct no-op availability accounting.
- [x] 1.3 Preserve same-request/same-credit bindings and existing automatic replay protection.

## 2. Verification

- [ ] 2.1 Run parser, external API, helper, scheduler and replica regression coverage.
- [ ] 2.2 Validate OpenSpec and required repository checks; review the focused diff.
- [ ] 2.3 Publish and integrate through required gates; deploy reviewed source and verify the affected path, or record the exact blocker.
