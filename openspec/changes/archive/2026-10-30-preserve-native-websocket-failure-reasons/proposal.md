# Preserve native WebSocket failure reasons

## Why

The October 30 recurrence includes upstream receive failures that persisted only a generic message. Existing phase and account-neutral handling cannot distinguish a TCP reset, EOF, TLS failure or protocol failure. This change supplies bounded evidence without changing recovery decisions or replaying requests.

## What Changes

- Add an optional fixed native WebSocket failure reason to the helper wire event.
- Validate the reason in Python and retain it with a fixed phase in existing receive/send error text.
- Keep old helpers compatible and keep arbitrary exceptions, URLs, headers and bodies out of the new diagnostic.

## Impact

Native protocol, native WebSocket emitter, Python decoder/relay and focused wire/relay tests. No database migration, setting, dependency, timeout, retry, account-selection or lifecycle change. Any deployment must preserve all existing listeners using another parallel generation.
