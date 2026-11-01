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
