## ADDED Requirements

### Requirement: OpenAPI byte properties translate on the non-strict chat adapter

When converting a non-strict Chat Completions function tool to Responses, the
adapter MUST translate OpenAPI `format: byte` schema annotations into a
description of base64-encoded bytes. It MUST retain tool identity, the schema's
structure, other keywords, and instance data. Explicitly strict chat tools and
direct Responses requests MUST retain their established validation behavior.

#### Scenario: An MCP attachment schema uses OpenAPI byte format

- **WHEN** a non-strict chat function parameter defines an attachment using `format: byte`
- **THEN** the converted Responses tool retains the attachment and its base64 meaning
- **AND** the unsupported byte format keyword is absent from the converted schema position
