# Load the shared Codex client version on serving replicas

Dedicated serving replicas skip the primary metadata and model schedulers. They
therefore ignore the current version already persisted by their primary and
send the configured fallback on SDK requests. Upstream can reject a model
available to a native Codex client when that fallback is too old.

Read the shared version snapshot before serving traffic and when reconciling a
catalogue update. Preserve the primary's scheduler ownership and keep I/O off
the inference path.

The release candidate also needs the fixed `dnspython` 2.9.2 lock entry for
CVE-2026-128089 and `url` 2.5.9 for RUSTSEC-2026-0592. The candidate scan and
Rust dependency audit remain required.
