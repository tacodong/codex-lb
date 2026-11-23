# Report effective SDK client version compatibility

Infrastructure readiness and model discovery can pass while the SDK fingerprint
used by a particular serving process is below the configured model's minimum.
Expose a loopback observation of the in-process version against that model's
metadata so operators can distinguish a stale replica from general availability.

This observation does not make an inference request or change readiness,
account routing, or model selection.
