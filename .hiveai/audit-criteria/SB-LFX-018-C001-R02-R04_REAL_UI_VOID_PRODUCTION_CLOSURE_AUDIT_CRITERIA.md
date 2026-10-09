# SB-LFX-018-C001-R02-R04 — Real UI + VOID Authority + Production Publish Closure — Audit Criteria

Parent strict audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R03_STRICT_REAUDIT_V01.md`

Owner functional workflow:
`docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`

Control bindings:
`docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`

## A. Preserve accepted work

Do not restart or discard R02/R03.

Retain unless a specific audit finding requires adaptation:

- three visual masters;
- exact PIXEL ART V04 bytes;
- R03 Alpix adapter/job persistence;
- provider routing boundaries;
- READY auto-pool;
- Reject exclude / Accept restore;
- durable installer/shortcut;
- existing useful focused tests.

No destructive sync.

## B. Production UI is real controls, not a screenshot application

PASS only if the production screens are composed from real Godot UI controls.

The master images may be used as:

- design/reference authority;
- audit comparison assets;
- development-only overlay if disabled in production.

They must not remain the production background carrying baked fixture state.

Reject if runtime still depends on a full master screenshot plus transparent hotspots for normal operation.

All visible dynamic values must come from real current state.

## C. PIXEL ART live state

Require real controls/data for:

- Single / Batch mode;
- Prompt;
- Size;
- Provider;
- Generate;
- Batch CSV path/action;
- batch progress;
- provider status;
- actual artwork thumbnails;
- Artwork Details;
- actual selected PNG preview.

Provider minimum:

`ALPIX (Claude) | MAGNIFIC | PIXELLAB`

## D. LEVEL FACTORY live state

Require real controls/data for:

- selected artwork queue;
- Auto/manual level number state;
- supply columns 3/4/5;
- background intent;
- pipeline stage states;
- actual solver result;
- replay result;
- official Difficulty V1;
- actual supply plan;
- variations/results;
- Accept restore/include;
- Reject exclude;
- selected PNG preview.

## E. RELEASE POOL live state

Require real canonical projection for:

- READY count/list;
- real thumbnails;
- search;
- difficulty/column filters;
- selection;
- selected-for-release cards;
- level details;
- STAGING/PRODUCTION target;
- preflight stage state;
- manifest preview;
- Upload/Publish.

No baked fixture rows/counts/statuses.

## F. Production publish is connected

The PRODUCTION path must use existing audited authorities, not a new shadow flow:

1. exact verified STAGING receipt/download;
2. CPX-002 current-main replay;
3. transient exact owner approval bound to:
   - manifest SHA-256;
   - content version;
   - PRODUCTION target;
4. CP03-008 production pack promotion;
5. CP03-009 versioned production manifest activation;
6. exact provider/readback/history evidence.

Wrong/missing approval must mutate nothing.

The owner confirmation must be a real transient UI action.

No hard-coded content version.

## G. Current-game VOID authority

Use exact current `Sekiph82/Scrubbots main`.

Current main already contains audited VOID commit:
`7d0d148b8609ec04852fdee02f6b8ef37598c616`.

A shallow local history may not be misreported as "main does not contain VOID".

PASS only if capability proof correctly opens on current main while preserving:

- canonical origin;
- clean checkout;
- HEAD == origin/main;
- audited-commit ancestry/contract evidence.

A history-incomplete checkout must either be completed safely or reported distinctly as incomplete history.

## H. LF19 regression

All seven previously failing `test_sb_lfx_019_void_game_parity.py` cases must pass.

No skip, xfail, alternate branch, stale fixture or assertion weakening.

## I. External PNG batch / identity / ordering

Permanent tests must prove:

- one external PNG;
- multiple external PNGs;
- CSV/batch PNG intake;
- each source keeps immutable source hash -> LevelData -> supply -> solver/replay -> Difficulty -> metadata identity;
- cross-binding a derived artifact to the wrong PNG rejects;
- failed/unsolved item consumes no final production order;
- successful source order remains deterministic;
- CampaignBuilder resolves a contiguous final sequence against current catalog/history;
- retry/resume does not reshuffle stable successful identities.

## J. READY auto-pool / no auto-publish

Require permanent proof:

- READY enters Release Pool without ACCEPT;
- Reject excludes;
- Accept restores;
- none of these triggers publish;
- Publish remains explicit owner action.

## K. Alpix live capability

Adapter/unit tests remain required.

Additionally:

If a real enabled Claude Alpix plugin/MCP exists locally:
- perform one real no-API-key Claude-subscription generation;
- validate exact PNG dimensions;
- record only non-secret plugin/tool identity and output hash.

If no exact Alpix plugin/MCP is installed:
- do not fake or silently substitute;
- all job state remains preserved;
- final state is `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED` after all non-Alpix technical closure is green.

## L. Final visual evidence

From durable runtime capture:

- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`

all exactly 1536x1024.

Independent review must show the masters' visual structure while all visible values are produced by live controls/state.

## M. Full regression / governance

Require:

- focused R04 tests;
- exact-master geometry tests;
- provider/resume tests;
- LF19 VOID parity;
- production-publish adversarial tests;
- external-PNG/identity/order tests;
- launcher/runtime tests;
- Godot parse/import;
- complete repository pytest with zero unresolved code/test failures;
- compileall;
- diff check;
- secret scan.

Builder never edits root `TASKS.md` or `.hiveai/audits/**`.

Implementation commit and evidence/log commit remain separate.

Normal fast-forward push only.

## Outcome

If all code/runtime gates pass and Alpix is installed:

`TECHNICAL PASS / OWNER VISUAL REVIEW`

If all code/runtime gates pass but Claude Alpix is not installed:

`TECHNICAL PASS / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED / OWNER VISUAL REVIEW`

Any code/test/UI/VOID/production-publish defect:

`CHANGES_REQUIRED`.
