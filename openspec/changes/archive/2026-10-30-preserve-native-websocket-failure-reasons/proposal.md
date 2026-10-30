# Preserve native WebSocket failure reasons

## Why

The October 30 recurrence includes upstream receive failures that persisted only a generic message. Existing phase and account-neutral handling cannot distinguish a TCP reset, EOF, TLS failure or protocol failure. This change supplies bounded evidence and routes typed abrupt closures through the existing account-neutral terminal path, preventing transparent replay of ambiguous sends.

## What Changes

- Add an optional fixed native WebSocket failure reason to the helper wire event.
- Validate the reason in Python and retain it with a fixed phase in existing receive/send error text.
- Keep old helpers compatible and keep arbitrary exceptions, URLs, headers and bodies out of the new diagnostic.

## Impact

Native protocol, native WebSocket emitter, Python decoder/relay and focused wire/relay tests. No database migration, setting, dependency, timeout or lifecycle change. Only typed missing-handshake/already-closed failures change health/replay classification. Any deployment must preserve all existing listeners using another parallel generation.

## Evidence-backed correction

Immutable-image qualification reproduced a real peer EOF as native protocol/close_without_handshake. Source inspection then proved this was account-penalizing and eligible for transparent replay after an ambiguous send. Classify only missing-handshake and already-closed transport reasons as account neutral, using the existing terminal/no-replay path. Other protocol failures retain their policy.
