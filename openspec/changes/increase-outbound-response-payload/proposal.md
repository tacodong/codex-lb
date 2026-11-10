# Increase outbound Responses payload budget

## Why
A Desktop conversation with screenshots was rejected locally after historical slimming: 19810947 bytes exceeded the 15MiB outbound guard, despite fitting the 128MiB ingress budget. The guard incorrectly treats the receive-event limit as an outbound limit.

## What Changes
Use the existing 128MiB Responses ingress constant for serialized outbound response.create requests. Keep received SSE/WebSocket events at 16MiB and retain slimming/error handling above the request budget. Include the changed module in the downstream stability image. No new settings or credential changes.

## Impact
Responses WebSocket forwarding and downstream image packaging. Larger requests can consume more transient memory and remain subject to upstream/model limits.
