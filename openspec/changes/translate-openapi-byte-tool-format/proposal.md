# Translate OpenAPI byte-format tools for Codex

Some OpenAPI-derived MCP tools use `format: byte` to describe base64 data.
Codex rejects that format when compiling a Chat Completions function tool
converted to Responses, even when the tool is never invoked.

Translate the OpenAPI annotation to a plain-language encoding description in
non-strict chat tools converted to Responses. Keep tool availability and
schema shape, and retain strict and native Responses validation.
