# Increase outbound Responses payload budget

## Why
A Desktop conversation with screenshots was rejected locally after historical slimming: 19810947 bytes exceeded the 15MiB outbound guard, despite fitting the 128MiB ingress budget. The guard incorrectly treats the receive-event limit as an outbound limit.

## What Changes
Use the existing 128MiB Responses ingress constant for serialized outbound response.create requests. Keep received SSE/WebSocket events at 16MiB and retain slimming/error handling above the request budget. Include the changed module in the downstream stability image. No new settings or credential changes.

## Impact
Responses WebSocket forwarding and downstream image packaging. Larger requests can consume more transient memory and remain subject to upstream/model limits.

## Required release-gate repairs
The candidate and standard image scans require the fixed Debian zlib package.
The unchanged Rust audit gate now rejects Hyper1.8.1's unmaintained pin-utils
transitive dependency (RUSTSEC-2026-0441); Hyper1.9.0 is the first compatible
release inspected that removes it. Native Cargo updates only Hyper and removes
pin-utils. Keep the audit and scan gates enabled.
