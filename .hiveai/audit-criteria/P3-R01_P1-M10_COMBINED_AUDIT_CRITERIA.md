# P3-R01 + P1-M10 — Combined Concurrent Workstream Audit Criteria

Document role: CHATGPT AUDIT CRITERIA

This combined cycle has two independent required workstreams.

## Workstream A — P3-R01

Authoritative prompt:
`.hiveai/prompts/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CRITERIA.md`

Parent owner prompt remains immutable:
`.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md`

Workstream A passes only if its own audit criteria pass.

## Workstream B — P1-M10 CampaignBuilder

Authoritative owner prompt:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Prompt SHA-256:
`09de3ed5f15edf47a56f0135299467abacda2560c1381ec9ec888ef2fbc0afe1`

Audit criteria:
`.hiveai/audit-criteria/P1_M10_CAMPAIGN_BUILDER_AUDIT_CRITERIA.md`

Owner decision:
`docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`

Workstream B passes only if its own audit criteria pass.

## Combined PASS rule

The combined cycle is PASS only if:
- P3-R01 passes;
- P1-M10 passes;
- full repository regression passes except truthful environment capability skips;
- neither workstream weakens the other;
- P1 owner decision superseding ACCEPT auto-publish is consistently reflected in current production behavior;
- P3 still terminates at Review Queue and never ACCEPTs/publishes;
- no Scrubbots game source is modified by this Level Factory cycle.

## Conflict rule

If an older Level Factory contract says owner ACCEPT immediately publishes, P1 owner decision is newer and authoritative:
- ACCEPT => Release Pool only;
- CampaignBuilder plan APPROVE => batch publication transaction.

P3 has no publication authority and is unaffected.

## P2 boundary

P2 is not present.
Do not invent P2 distribution implementation.

Report P2-dependent Route A automation as pending if it cannot be executed from P1 alone.
