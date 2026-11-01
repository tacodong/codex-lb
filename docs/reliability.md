# Reliable account failover and streaming upgrades

This guide describes the **downstream beta.9 stability branch** in
[`tacodong/codex-lb`](https://github.com/tacodong/codex-lb/tree/codex/stability-beta9-base).
It is not a claim that an upstream release already includes these changes.
The implementation is in [PR 1](https://github.com/tacodong/codex-lb/pull/1),
[PR 2](https://github.com/tacodong/codex-lb/pull/2), and
[PR 3](https://github.com/tacodong/codex-lb/pull/3).

Owning specifications:
[account routing](https://github.com/tacodong/codex-lb/blob/codex/stability-beta9-base/openspec/specs/account-routing/spec.md),
[runtime observability](https://github.com/tacodong/codex-lb/blob/codex/stability-beta9-base/openspec/specs/proxy-runtime-observability/spec.md),
[Responses compatibility](https://github.com/tacodong/codex-lb/blob/codex/stability-beta9-base/openspec/specs/responses-api-compat/spec.md),
and [replica operations](https://github.com/tacodong/codex-lb/blob/codex/stability-beta9-base/openspec/specs/replica-operations/spec.md).

## Catalogue of the shipped stability fixes

This catalogue covers our October 20–November 1 stability work, including the
older compatibility hooks subsequently moved into the application image. The
qualified pin-rotation artifact listed below contains the preceding application
repairs too. Use one qualified cumulative image; do not layer the historical
host-mounted Python amendments over it.

| Repair | Original symptom | Corrected behavior | Implementation |
| --- | --- | --- | --- |
| Native WebSocket burst buffering | A short consumer delay could abort a healthy stream after 64 decoded messages | Bound the decoded queue by both 4,096 events and 32 MiB, with acknowledgement progress and isolated overflow | [PR 1](https://github.com/tacodong/codex-lb/pull/1) |
| Interrupted HTTP stream cleanup | An outer adapter could fail or close without finalizing its nested service generator | Cascade closure through the three response adapters so the owning service finalizers can release transport and leases | [PR 1](https://github.com/tacodong/codex-lb/pull/1) |
| Desktop encrypted-output compatibility | Codex 0.165's `output.encrypted_content` include was rejected before inference | Accept and forward that exact include while continuing to reject unknown values | [PR 1](https://github.com/tacodong/codex-lb/pull/1) |
| Account-neutral socket failure handling | Generic transport errors could penalize a healthy account or enter unsafe replay handling | Preserve transport provenance and terminate ambiguous failures without an account penalty or transparent replay | [PR 1](https://github.com/tacodong/codex-lb/pull/1), extended by [PR 2](https://github.com/tacodong/codex-lb/pull/2) |
| Safe native failure reasons | A generic receive-failed message hid resets, EOF and missing close handshakes | Carry fixed validated phase/reason codes through Rust, Python and existing request-error evidence | [PR 2](https://github.com/tacodong/codex-lb/pull/2) |
| Scoped dependency hardening | Required audits rejected fixed vulnerabilities in the deployed beta.9 dependency set | Repair Python/Rust locks and required OS packages, rebuild the helper and qualify/scan the resulting image | [PR 1](https://github.com/tacodong/codex-lb/pull/1) |
| SQLite serving-only replicas and keyed authentication | A second full startup could conflict with the primary SQLite lifecycle; replacing the primary would interrupt work | Start explicit ordinary/keyed serving factories beside the retained lifecycle owner, without primary-only startup work | [PR 1](https://github.com/tacodong/codex-lb/pull/1) |
| Connection-preserving activation and rollback | Unqualified NAT rules could capture old flows, and deleting the last hook could retire translations | Route only new SYNs, replace rules atomically, retain earlier processes/hooks and advance boot ownership | [Host controller](https://github.com/tacodong/homelab/blob/main/scripts/fleet/codex_lb_serving.py) and [PR 2065](https://github.com/tacodong/homelab/pull/2065) |
| Pending-auth pin rotation and peer-cache propagation | Revoked credentials could be selected repeatedly until their JWT expiry, including through stale bridge snapshots | Exclude pending-auth accounts, persist healthy movable-pin replacements and apply the policy to cache, warmup and capacity handling | [PR 3](https://github.com/tacodong/codex-lb/pull/3) |

### Bounded buffering without blocking acknowledgements

The native helper multiplexes responses and send acknowledgements. The repair
uses the existing byte-counted queue for **decoded WebSocket messages**, not
just the helper's outer event queue. Its 4,096-event and 32 MiB payload limits
bound different kinds of pressure: many small frames and a few large frames.
The pump must keep handling acknowledgements while received data is buffered;
waiting on a full decoded queue would stall control-plane progress.

A real overflow remains a bounded local `consumer_backpressure` failure,
reported as `upstream_consumer_backpressure` to the relay. It is account-neutral,
does not automatically replay, and does not abort an unrelated peer connection.
Increasing an idle timeout would not repair this queue failure.

Regression coverage is in `tests/unit/test_native_websocket_bursts.py`, including
ordered small bursts, byte limits, acknowledgement progress, pending-send
failure and peer isolation. Historical exact-image qualification delivered
5,120 ordered frames across 20 persistent turns in raw and interpreted modes.
That result is a bounded burst test, not a sustained-load or lifetime guarantee.
The owning change is
[bound-native-websocket-bursts](https://github.com/tacodong/codex-lb/tree/codex/stability-beta9-base/openspec/changes/archive/2026-10-29-bound-native-websocket-bursts).

### Close the owned stream when an adapter exits

The repaired adapters are public Responses normalization, reasoning-summary
normalization and response-error conversion. A `finally`-owned close propagates
transport failure, early consumer close and cancellation to the nested service
stream. The service retains ownership of reservation settlement and lease
release; the adapters do not introduce a second settlement authority.

Public and Codex-native error behavior remains distinct. Tests verify the
existing error contract as well as prompt finalization; hiding an error behind
an HTTP 200 response would not be a valid cleanup fix. A client acceptance test
must consume the stream through its completed terminal event.

`tests/unit/test_responses_stream_cleanup.py` exercises the three adapters,
including cancellation preservation. The
[verification record](https://github.com/tacodong/codex-lb/blob/codex/stability-beta9-base/openspec/changes/archive/2026-10-29-close-interrupted-response-streams/verification.md)
records the initial 222 affected-path checks and exact-image cleanup evidence.
These were historical qualification results; documentation updates do not rerun
live inference or replay an interrupted user's turn.

### Accept the exact Desktop include, not arbitrary values

The baseline beta.9 validator rejected `output.encrypted_content` requested by
Codex 0.165 with an invalid-payload/include error before inference. The fix adds
that literal to the allowed include values and forwards it unchanged alongside
`reasoning.encrypted_content`. It does not decrypt output, rewrite conversation
history, alter model selection or relax validation for unknown include values.

`tests/unit/test_desktop_transport_compatibility.py` checks both preservation of
the accepted values and rejection of an unknown value. Verify a real Desktop
reply and continuation after deploying the image: schema acceptance alone does
not prove that the affected client can finish its turn.

### Keep socket failures separate from account failures

The earlier native adapter reduced socket-I/O failures to a generic upstream
error, losing the information the relay needed to avoid an account-health
penalty and unsafe replay. The application-owned fix preserves that
account-neutral classification through send and receive handling. Its network
classification says where the failure was observed; it does not prove that the
whole server lost connectivity. These send/receive classification repairs cover
the native WebSocket path; HTTP body failures retain their client-specific
handling.

The later native helper change adds optional fixed reasons such as
`connection_reset`, `unexpected_eof`, `broken_pipe`, `pong_timeout` and
`close_without_handshake`. Python validates an allowlist. Missing or unknown
reasons from an older helper retain generic behavior; the new diagnostic never
appends raw exceptions, URLs, credentials, headers or provider bodies.

A real abrupt peer EOF reproduced `protocol/close_without_handshake`. That
specific reason, plus `connection_closed`, now uses the existing terminal,
account-neutral no-replay path. Other protocol failures retain their existing
classification. The regression reproduced a replay count of one before the
correction, then verified zero replay, no health penalty and reservation release
through the service path afterward.

Relevant coverage includes `tests/unit/test_desktop_transport_compatibility.py`,
`tests/unit/test_native_websocket_bursts.py`, the relay regressions in
`tests/unit/test_proxy_utils.py`, and
`crates/codex-lb-egress-worker/tests/websocket_protocol.rs`. The helper tests cover
actual peer termination, missing pong, wire compatibility and credential-safe
reason emission. The owning change is
[preserve-native-websocket-failure-reasons](https://github.com/tacodong/codex-lb/tree/codex/stability-beta9-base/openspec/changes/archive/2026-10-30-preserve-native-websocket-failure-reasons).

### Rebuild and scan the dependency boundary

The stability release repaired Python HTTP, DNS, decompression and certificate
packages (`aiohttp`, `yarl`, `dnspython`, `urllib3`, `brotli` and `certifi`), scoped
Rust TLS/async-I/O/decompression dependencies, and required pcre2/OpenSSL OS
packages. The locks and `scripts/Dockerfile.stability` own the exact versions.
This was scoped hardening of the qualified beta.9 runtime, rather than an
unrelated application, dashboard or database-schema upgrade.

The native binary must be rebuilt against its repaired lock. Merely editing a
lock while copying an old binary into the image would leave that dependency
boundary unqualified. The trusted stability workflow builds ARM64, scans fixed
High/Critical findings and publishes a source-SHA artifact; publication itself
does not deploy. A passed scan describes the artifact, scanner database and
policy at that time, not a permanent security guarantee.

Use the
[dependency repair record](https://github.com/tacodong/codex-lb/tree/codex/stability-beta9-base/openspec/changes/archive/2026-10-29-patch-stability-runtime-dependencies)
and the reproducible-artifact steps below. Preserve failed audit gates rather
than making a candidate pass by disabling them.

### Retain one SQLite lifecycle owner

The explicit factories are `app.main:create_serving_replica_app` and
`app.main:create_keyed_serving_replica_app`. They require an existing, actively
owned local SQLite store. They do not run migrations, bootstrap an empty store,
purge shared startup history, start singleton jobs or write the primary's
clean-shutdown marker. They retain native serving, cache invalidation,
persistence and process-local flush/settlement work.

The ordinary factory follows the native global authentication policy. The keyed
factory requires a key for both HTTP and WebSocket without flipping that shared
global setting. Give each serving replica its own bridge identity and distinct
port through the native controller. Keep the primary alive; a serving replica
is neither automatic primary takeover nor a new-install bootstrap command.

Coverage lives in `tests/unit/test_serving_replica.py` and
`tests/integration/test_serving_replica.py`. Historical two-process qualification
kept the primary's connection, lifecycle marker and owner lock intact while a
replica stopped, and verified a conversation across the old/new process boundary.
The owning change is
[serve-with-existing-sqlite-owner](https://github.com/tacodong/codex-lb/tree/codex/stability-beta9-base/openspec/changes/archive/2026-10-29-serve-with-existing-sqlite-owner).
Use the upgrade and rollback procedure below for the separate network-routing
boundary; do not replace the primary to activate this serving role.

## Start with the failing request

A client's “Reconnecting” or “error decoding response body” message is a symptom,
not a root cause. Separate client-to-LB transport from LB-to-upstream transport.
Correlate the exact chat, request time and native account status with gateway
records before changing a timeout, account pin or proxy route.

| Evidence | What it establishes | Useful next step |
| --- | --- | --- |
| `token_revoked` followed by preferred-owner errors | Authentication was rejected and the request cannot use its selected owner | Inspect native account status and whether the pin is movable |
| `previous_response_owner_unavailable` | The request still requires an unavailable owner | Check full-history recovery eligibility and file/stored-response ownership |
| `native phase=protocol reason=close_without_handshake` | The upstream peer closed without a WebSocket close handshake | Correlate the route and timing; this does not identify the responsible network hop |
| A client reports body decoding failure | The received stream could not be decoded or completed | Inspect both transport legs; healthy containers alone do not rule out interruption |

Read bounded recent records or an indexed exact-conversation query rather than
scanning an entire large request database. Keep prompts, raw response IDs,
cookies, OAuth callbacks, headers, provider bodies and raw exception strings out
of shared logs. Use fixed low-cardinality transport reasons for diagnostics.

## Which pins can move?

**Soft cache and thread pins** preserve locality and warm prompt caches. In this
branch, an account requiring reauthentication is excluded immediately, even when
its JWT claims a future expiry. An eligible replacement serves the request and
becomes the persisted soft-pin owner. Warmup and live bridge reuse obey the same
policy. Freeing concurrency cannot repair authentication, so an all-pending pool
reports reauthentication rather than a capacity wait.

Example: a cache pin points to account A, whose credentials have been rejected.
Account B is Active and satisfies the request's model, quota, security and API-key
scope. New movable requests use B and retain their conversation context. A stays
pending until native reauthentication succeeds; failover never changes A's badge
to Active or edits its stored credentials.

**Hard ownership** is different. A stored `previous_response_id`, explicit
account-owned continuation, uploaded file or other hosted object cannot simply
be presented with another account's credentials. Existing recovery can move a
request only when its complete-history and account-neutrality proofs hold. A
delta-only request does not contain enough context to reconstruct the turn.
Turning off sticky threads or bulk-deleting mappings does not make that state
portable.

Preserve these boundaries:

- Keep the requested model, effort, API-key scope and security policy.
- Require the retained context proof, including prior assistant/tool output,
  before rebuilding an anchored request without its owner.
- Do not replay ambiguously accepted work after a transport failure; a second
  dispatch could duplicate billing, tool execution or another side effect.
- Keep file/stored-object ownership intact when no verified rebuild exists.

The replica routing cache matters too. A bridge may retain an Active snapshot
after another replica persists `reauth_required`. The committed routing snapshot
and guarded local unavailable marker now block that stale bridge. A committed
native reauthentication clears the block across replicas without restarting them.

## Repair authentication through the native account flow

Use the affected account's **Re-authenticate** action, not a generic replacement
account. Confirm the returned principal matches the targeted account; this branch
rejects a mismatched seat without replacing the intended account's credentials.
Complete MFA or passkey steps in the intended browser. Never paste credentials
or callback URLs into a chat or repository.

For a remote PKCE callback that lands on the browser's own localhost, use the
native dialog's callback-URL field and Submit control. Let codex-lb validate the
state, exchange the code and check identity. Do not implement a second OAuth
client or copy authentication stores between machines.

After a handoff, inspect the current flow/account state before starting anything
again. If sign-in already succeeded, verify that same account is Active with
fresh usage and a **completed, account-attributed reply**. Native Force probe's
HTTP status alone does not prove that its response stream completed. Reuse a
fresh completed receipt rather than spending quota on duplicate probes.

An owner can leave authentication pending. Movable requests should use the
remaining eligible pool; an unrebuildable hard-owned continuation may still need
that account repaired.

## Choose a reproducible artifact

Use a digest-pinned image and retain its source revision. The artifact used for
the pin-rotation acceptance was built for **Linux ARM64**:

```text
ghcr.io/tacodong/codex-lb@sha256:27a41be2d70010561333d93bb52ec2085f404ce20f164291c820e77d6d8a491a
source: d387c1ffb6c118e0c70a9a802d87fe8d42a4768c
```

Use the normal [Docker deployment procedure](deployment/docker.md) for a new
installation, with the artifact qualified for your architecture. ARM64 acceptance
does not establish another architecture's build/runtime acceptance.

The stability Dockerfile retains the qualified beta.9 OS/dashboard and rebuilds
the native helper from locked source. Its explicit COPY list must include every
changed Python module: a source test passing in a checkout does not prove an
image contains the fix. This repair includes routing cache, auth-manager,
warmup and cap-selection paths as well as the core selector.

Representative source checks include:

```bash
uv sync --frozen --dev
uv run pytest -q tests/unit/test_proxy_account_eligibility.py tests/unit/test_select_with_stickiness.py
uv run pytest -q tests/integration/test_cache_invalidation_bus.py
make lint
uv run ty check
```

Also complete the repository's required current-head CI/review gates and scan
the exact image. The source change, immutable image, running process and affected
client are four separate acceptance gates.

## Upgrade without replacing active listeners

For an existing installation, use its native deployment controller. The tested
host adapter is maintained separately in
[Homelab](https://github.com/tacodong/homelab/blob/main/scripts/fleet/codex_lb_serving.py);
it is an example of host integration, not an upstream codex-lb setting.

1. Capture current container identities, start times, restart counts, image
   digests, routing rules and boot ownership. Acquire the existing maintenance
   slot; do not break another backup/deployment owner's lock.
2. Start a **new generation** with distinct resource names and internal ports.
   Retain the primary SQLite lifecycle owner. Native serving-replica factories
   skip primary-only migrations/startup work and require that existing owner;
   they are not a replacement bootstrap procedure.
3. Preserve native authentication, state mounts, resource limits and network
   controls. Keep credentials in the existing protected host-local custody.
   Do not mount edited application source over a live process.
4. Test the new ordinary and mandatory-key endpoints with HTTP and persistent
   WebSocket reply/continuation pairs. Verify missing-key denial independently.
5. Hold an old WebSocket open. Route **new TCP SYNs only** to the qualified
   generation, then complete its next turn on that same old socket.
6. Read back the exact image/rules and all prior lifecycles. Update the boot
   routing source/receipt without restarting listeners. Verify the affected
   computer through its actual native provider and a two-turn context check.

On the tested namespace-NAT design, use atomic rule replacement for activation
and rollback. **Deleting the last NAT hook can retire existing translations**,
including sockets served by an earlier generation. Do not flush conntrack or
firewall chains. Roll back new-flow routing to the preceding serving generation
while keeping both processes running. Do not restore an old shared database to
roll back code.

Retain earlier generations and their receipts while affected sockets can remain.
A health endpoint or one surviving held socket does not establish that every
chat was uninterrupted. The separate
[deployment record](https://github.com/tacodong/homelab/pull/2090) includes a brief
cross-client interruption whose cause was not established; do not convert that
uncertainty into a zero-downtime claim.

## Verify pin rotation without revoking an account

First test with synthetic states in an isolated copy of the exact published
image. Exercise the production selector and sticky persistence, a future/unknown
JWT expiry on a pending-auth account, a stale Active bridge snapshot, warmup
exclusion and authentication-versus-capacity classification.

For an authorized live check, use a unique **test-owned** soft pin referencing an
already-pending account and a short-lived model-scoped diagnostic key. Require
two completed replies with a remembered marker, a persisted replacement owned
by an eligible account and unchanged status on the pending account. Delete and
read back only those test pins/key. Never revoke a healthy token, edit real chat
history or overwrite a user's pin to manufacture a failure.

These fixes prevent the reproduced account-penalty, selection and replay
failures. They do not guarantee that a remote peer, residential route or network
will never interrupt a stream. Keep any new transport occurrence distinct from
authentication recovery and diagnose it from its preserved safe provenance.
