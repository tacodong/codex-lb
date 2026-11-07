## Context

The native provider can return HTTP 200 `nothing_to_reset`, zero windows, and the selected credit still `available`, despite nonzero usage. HTTP 200 `no_credit` can carry `credit: null`; the shared parser rejects it. Automatic attempts otherwise leave only a durable request pin, which is not evidence of a successful reset.

## Goals / Non-Goals

Preserve the provider's actual outcome and exact account/credit ownership. Do not replay uncertain operations, discard request bindings, redeem another credit, or bypass provider eligibility.

## Decisions

Keep `credit` required but nullable. Log code and window count for every parsed consume result; use warning level for non-reset or zero-window outcomes. Decrement availability only for a `reset` result where the selected credit was in the fresh available list. Retain existing pins for all outcomes so a retry never retargets another credit.

## Risks / Trade-offs

Provider eligibility can still prevent a reset. Existing pins cannot prove whether a quota reset occurred. Releasing no-op pins was rejected because it permits the same request id to target another credit later. Retrying a no-op with the same id also cannot be assumed to change a provider-memoized result. Upstream must correct reset eligibility for affected weekly windows; this patch makes the boundary visible.

## Validation

Exercise both HTTP parsers, external dashboard no-op envelopes, correct no-op count/logging, and retained request binding across later retries. Existing serializer and scheduler guard tests remain applicable.
