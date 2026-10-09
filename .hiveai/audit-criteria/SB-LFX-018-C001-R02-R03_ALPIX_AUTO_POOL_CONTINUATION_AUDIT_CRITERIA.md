# SB-LFX-018-C001-R02-R03 — Alpix + Auto Pool Continuation — Audit Criteria

Current visual masters remain unchanged.

Owner workflow:
`docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`

Control bindings:
`docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`

## A. Prior work preservation

PASS only if builder proves it did not restart the two-hour R02-R02 implementation from scratch.

Baseline implementation commit:
`8b2f7eb95e804a739d631dd3c2f052f4b51983d9`

Retain all still-valid work, including:
- repaired exact PIXEL ART V04 master;
- runtime copies/imports of all three masters;
- three-screen scene/shell integration;
- existing exact-master tests/evidence harness;
- any additional useful uncommitted/current-worktree R02-R02 work found at start.

Before mutation, log a KEEP / ADAPT / ADD matrix.

Do not redo a completed valid step just to satisfy the new prompt.

Do not discard/reset useful uncommitted work.

## B. Legacy EXE port evidence

Builder must inspect/reuse the owner EXE behavior, not invent a new job engine.

Require evidence that the implementation ports or directly reuses equivalents of:
- Claude discovery/subscription subprocess path;
- CSV SHA-256 persistent ArtJob;
- PENDING/DRAWN/VALIDATED/IMPORTED states;
- LIMIT pause;
- Resume from first incomplete step;
- completed artifact preservation;
- per-row retry/redraw only when needed.

## C. ALPIX (Claude) real provider

PASS only if:
- provider option exists and is selectable;
- actual local Claude Code subscription session is used;
- actual installed Alpix plugin/MCP/tool identity is discovered from local Claude configuration;
- no Anthropic API key or paid fallback is used;
- single request creates one PNG at requested size;
- no fake success or decorative provider label.

If local Alpix is unavailable, capability must fail closed while preserving jobs. Never substitute another provider silently.

## D. ALPIX CSV resume

Require deterministic fixture/integration coverage:
- rows processed in CSV order;
- completed rows persist;
- simulated usage limit stops with LIMIT, not FAILED;
- Resume continues first incomplete row;
- completed rows not repeated;
- restart/reopen resumes same CSV-SHA job;
- same CSV does not create a duplicate job;
- changed CSV creates a different identity.

## E. Magnific / PixelLab selection

Provider dropdown includes MAGNIFIC and PIXELLAB.

They must delegate to existing semantic provider adapters/current truthful execution contracts.

No duplicate provider implementation and no fake direct capability.

## F. External PNG Level Factory batch

Require 1, multi-PNG and CSV/batch intake through the same canonical pipeline.

Every successful source has immutable matching between:
PNG + LevelData + supply + solver proof + replay + Difficulty V1 + metadata + hashes.

Cross-binding artifacts between PNGs must fail closed.

## G. Automatic numbering/order

Default batch numbering is automatic.

Successful READY candidates preserve source order.

Failed/unsolved candidates consume no final production level number.

Final release plan is contiguous from canonical current catalog/history.

Retry/resume is idempotent.

## H. READY -> Release Pool automatic

A canonical READY candidate enters Release Pool without owner ACCEPT.

Fresh READY defaults included.

Reject excludes/quarantines.

Accept Level idempotently includes/restores.

Neither action publishes.

Tests must replace old "ACCEPT alone creates eligibility" assumptions.

## I. Publish remains owner gate

Nothing auto-publishes.

Release Pool Publish/Upload remains explicit owner action.

STAGING, verification, exact production approval and R2 controls remain fail-closed.

No hard-coded content version.

## J. Visual preservation

All three production screens still match the existing masters.

No extra production page/panel.

Resume behavior reuses the master-defined batch action location.

Real selected PNG replaces fixture owl in runtime preview when data exists.

## K. Regression

Run focused delta tests first, then one final full regression after implementation.

Do not waste time running the full suite repeatedly before the functional delta is complete.

Final requires:
- exact-master UI tests;
- provider/batch/resume tests;
- external PNG batch/identity tests;
- auto-pool/order tests;
- VOID parity;
- publisher tests;
- launcher/durable runtime;
- Godot parse/import;
- complete pytest zero unresolved failures;
- compileall;
- diff check;
- secret scan.

## Outcome

`AWAITING_GPT_SB_LFX_018_C001_R02_R03_STRICT_REAUDIT`
