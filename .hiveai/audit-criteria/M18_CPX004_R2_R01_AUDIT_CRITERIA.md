# M18 + CPX-004 R01 — STRICT RE-AUDIT CRITERIA

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Audit independently from source, tests and committed evidence.

## A. Release ledger fail-closed
PASS only if:
- missing ledger is distinguishable from invalid/unavailable ledger;
- corrupt JSON/event/chain never becomes `()` clean history;
- first-publication local empty history cannot overwrite an existing invalid control ledger;
- transient read failure blocks publication;
- exact invalid remote bytes remain unchanged;
- no staging/production mutation occurs after failed release-history preflight.

## B. Production promotion idempotency
PASS only if:
- absent target creates conditionally;
- exact existing destination returns idempotent success without rewrite;
- different destination fails hard and preserves bytes;
- transient read/write does not overwrite;
- no delete capability is added;
- retry after partial promotion can continue when already-promoted objects are exact.

## C. CPX-004 implementation
PASS implementation-only if:
- owner-facing/service handoff exists;
- headless/operator equivalent exists;
- only owner-accepted + release-eligible content can pass;
- READY-only content is rejected;
- canonical M14 one-command publisher is used;
- no UI/controller direct cloud SDK mutation;
- preflight is mutation-free and contains exact identities/hashes/current game SHA/target;
- CPX-002 current-main replay remains required;
- real production requires exact owner approval bound to manifest SHA/content_version;
- no phone/game-repo write;
- receipt is secret-free;
- deterministic tests prove GUI/service/headless parity.

A real owner release batch is NOT required for implementation-only PASS, but no live publication may be claimed without one.

## D. R2 live proof
If no secure write credential exists:
- CP07-006 live state remains pending;
- no live PASS may be claimed;
- no credential may appear anywhere.

If live proof is claimed, independently verify real STAGING object readback/hash evidence.

## E. Regression
Require:
- all R01 focused tests green;
- CP07 suite green except truthful live-secret skip;
- M11-M14 regressions green;
- relevant Factory/Release Pool/CampaignBuilder tests green;
- safe full pytest green or independently proven unrelated baseline;
- compileall/JSON/schema/diff checks green;
- secret scan green;
- root TASKS.md untouched by Codex;
- no `.hiveai/audits/**` builder writes.

## Re-audit outcome
- If A/B/C/regression PASS and only external live credentials/content/approval remain, R01 can receive **TECHNICAL PASS / EXTERNAL LIVE GATES PENDING**.
- Do not close M18 live publication or CP07-006 until real R2 evidence exists.
