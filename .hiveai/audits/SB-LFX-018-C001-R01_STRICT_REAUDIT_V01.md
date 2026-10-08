# SB-LFX-018-C001-R01 — ChatGPT Strict Re-audit V01

Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation:
`4fbe66b445e39d87c18af2a8f59b2784058a262c`

Builder evidence:
- `dcde53a54b37d0e1ece3315f408952e9114ced46`
- closeout `5d1462c60a675e40a63385f904025eb68086aace`

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R01_FUNCTIONAL_OWNER_PAGES_CODEX_LOG.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R01_FUNCTIONAL_OWNER_PAGES_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R02**

R01 materially improves the product and most functional composition is accepted for retention.

R02 is narrow. Do not redesign the accepted eight-page shell.

## A — Canonical owner-page projection: PASS / RETAIN

Accepted:

- `owner_pages_snapshot()` is a read-only projection;
- it reports `read_only=true`, `mutated=false`;
- it reads canonical batch, pipeline, candidate, library, failure and Release Pool records;
- UI mutation controls delegate to existing launcher operations;
- no independent owner-review, solver, batch or release truth store was added.

Retain this architecture.

## B — Eight-page owner shell and identity: PASS / RETAIN

Retain exactly:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

Also retain:

- `ScrubBots Factory Studio` owner title;
- compact footer;
- collapsed Technical details;
- large preview region;
- contextual legacy tools;
- existing explicit review authority;
- simple dark visual hierarchy.

## C — HOME / BATCH / SOLVE / REVIEW functional composition: SUBSTANTIAL PASS / RETAIN

R01 now adds:

- canonical batch/candidate counts;
- Continue Batch;
- Retry eligible failures;
- Resume/Recover;
- candidate + 3/4/5 supply selection;
- canonical pipeline solve/re-solve;
- readiness/difficulty projection;
- direct ACCEPT / REJECT delegating to canonical owner-review.

These are retained.

R02 only needs the visual/item composition and evidence consistency fixes below.

## D — LIBRARY functional composition: PARTIAL

Search/filter actions and canonical discovery calls exist.

Blocking visual/product gap:

the owner page renders results mainly as RichText lines. Product contract requires a thumbnail/grid or compact item list where visual identity matters.

R02 must render canonical source/candidate result items as real compact visual rows/cards with thumbnail when available, identity and status. History/Revisions/Reproduce stay contextual.

## E — HOME/BATCH visual item presentation: PARTIAL

HOME and BATCH currently render item evidence as text bullets inside `OwnerLiveDetails`.

Product contract requires:

- HOME thumbnail grid when artifacts exist;
- BATCH per-item thumbnail/status.

R02 must add compact canonical item cards/rows using existing artwork/source paths. Do not create or cache a second authoritative catalog.

## F — PUBLISH: BLOCKING

The simple PUBLISH page visibly describes:

`Accepted Levels -> Campaign Order -> Preflight -> STAGING -> Production Approval`

but its direct owner interaction row exposes only:

`Campaign order / preflight / STAGING`

which opens the legacy Release surface.

The R01 criterion and product contract require the simple owner page to expose separately:

- Preflight;
- Publish to STAGING;
- Production Approval.

R02 must provide visibly separate controls/states on PUBLISH.

Important safety boundary:

- STAGING and Production Approval remain separate;
- production action must never infer approval;
- if the canonical production-promotion handoff is not yet runnable because no verified STAGING receipt / exact approval authority / R2 credentials exist, the Production Approval control must be visibly disabled or blocked with the truthful first reason;
- do not duplicate M14/R2/promotion logic in GDScript;
- delegate to existing trusted content-pipeline authority only.

Do not confuse Route A `APPROVE and Open Release PR` with remote-content production promotion.

## G — SETTINGS: PARTIAL

Provider/core/cost/recovery/diagnostics are present.

R02 should also show the active durable runtime/project path or its concise resolved status, as required by the Settings contract.

Unknown provider/cost values remain unknown.

## H — Visual evidence: BLOCKING / internally inconsistent fixture state

All eight durable Release screenshots were inspected independently.

The layout remains substantially cleaner than the original engineering UI and is retained.

However the fixture layer only replaces the RichText block. It does not update the rest of the page, causing contradictory evidence:

- HOME says `Imported 8 / Solved 5`, while cards say Not selected / Waiting / Not run and the right panel says `No batch selected`;
- BATCH says `Progress 6/8`, while cards say No items / Waiting;
- SOLVE says `Supply columns: 4 / Solver SOLVED`, while the visible selector says `3 columns` and cards say Not run;
- REVIEW says READY/SOLVED while cards say Not run / No decision;
- LIBRARY says six fixture records while canonical cards say 0 sources / 0 candidates.

This does not satisfy page-specific visual evidence.

R02 must make the deterministic visual fixture internally coherent across:

- counts/cards;
- list/grid;
- selected controls;
- preview;
- Next Step state;
- action enablement;
- labels.

Fixture truth must stay unmistakably labeled as fixture/demo-only and must never mutate canonical evidence.

Prefer a single presentation-fixture projection consumed by the same render path rather than post-render text replacement.

## I — Full regression: BLOCKING

R01 final monolithic result:

`1739 passed, 6 skipped, 8 failed`

and the full suite was not rerun after the final small UI/runtime correction.

Seven failures were classified by the builder as:

`Current ScrubBots main does not contain the audited VOID implementation`

Independent GitHub verification disproves that classification.

Facts verified on canonical `Sekiph82/Scrubbots`:

- audited VOID commit: `7d0d148b8609ec04852fdee02f6b8ef37598c616`;
- builder-tested game head: `861d6a8a7d4a572ae7a35a9b65a55677a8e071b5`;
- GitHub compare reports `7d0d148...` as the merge base and `861d6a8...` **27 commits ahead / 0 behind**;
- current main is also descended from `7d0d148...`;
- current `scripts/data/level_data.gd` contains `FORMAT_VERSION_VOID := 2` and `VOID_CELL := -1`;
- current Level Data spec documents Version 2 VOID;
- current `tests/void_cells_c001.gd` remains present.

Root cause of the false CLOSED gate is the R01 test authority checkout being described as a **shallow clone**. The capability gate performs:

`git merge-base --is-ancestor 7d0d148... HEAD`

A shallow checkout that does not contain that historical commit cannot prove ancestry and correctly fails closed.

Therefore this is not an external game-authority loss.

R02 regression requirement:

- use an exact-current clean canonical Scrubbots checkout with sufficient history to prove the audited VOID ancestor, or explicitly deepen/fetch the audited commit and ancestry;
- do not weaken the already-audited VOID gate merely to accommodate an insufficient shallow test checkout;
- rerun the seven VOID parity nodes;
- rerun the exact Route A node;
- rerun the complete LF repository pytest after final R02 code;
- zero unresolved failures.

If a failure remains with a history-complete exact-current authority, then investigate it as a real code regression.

## J — Route A isolated classification: PASS / RETAIN

Exact Route A integration passed independently:

`1 passed in 377.03s`

Retain.

## K — Focused/runtime verification: PASS / RETAIN

Accepted:

- focused owner-page/workspace/boundary tests;
- Factory Studio runtime suite;
- compileall;
- durable Release capture;
- normal fast-forward publication;
- no builder TASKS/audit writes.

## R02 scope

R02 is limited to:

1. HOME/BATCH/LIBRARY compact thumbnail/card/list presentation;
2. direct, separately visible PUBLISH Preflight / STAGING / Production Approval controls with fail-closed canonical delegation;
3. compact SETTINGS runtime/path state;
4. internally coherent eight-page visual fixture/evidence;
5. history-complete exact-current Scrubbots authority for regression;
6. full zero-failure repository regression after final changes.

Do not start M17.

## FINAL

**CHANGES_REQUIRED / R02**
