# SB-LFX-018-C001-R02-R03 — Preserve R02-R02 Work, Add Alpix Production + READY Auto Pool

Document role: CODEX CONTINUATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_AUDIT_CRITERIA.md`

Owner workflow:
`docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`

Owner decision:
`docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md`

Functional bindings:
`docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`

Legacy EXE reference:
`docs/product/FACTORY_STUDIO_LEGACY_EXE_PIXEL_ART_BEHAVIOR_V01.md`

## CRITICAL: DO NOT RESTART THE LAST TWO HOURS OF WORK

The exact-three-master implementation already reached GitHub in commit:

`8b2f7eb95e804a739d631dd3c2f052f4b51983d9`
(`Implement exact three-master Factory Studio UI`)

That commit is useful baseline work and must be retained unless a specific new owner decision contradicts a piece of it.

It already contains, among other things:
- exact PIXEL ART V04 master repair;
- runtime master assets/imports;
- three-screen MasterUI integration;
- `factory_studio_exact_ui.gd`;
- scene/shell wiring;
- exact-master visual evidence harness;
- runtime tests;
- exact-three-master unit test.

Do not rebuild those from zero.

The current Codex session/worktree may also contain additional useful uncommitted R02-R02 changes made after that commit. Preserve them too.

## FIRST OPERATION — PRESERVE CURRENT WORK

1. Record current:
   - worktree path;
   - HEAD;
   - origin/main;
   - `git status --short`;
   - `git diff --stat`;
   - changed/untracked files.
2. If useful R02-R02 changes are uncommitted, DO NOT reset/clean/restore/discard them.
3. Make a safe local checkpoint/snapshot before reconciliation if needed.
4. Fetch origin/main.
5. Reconcile non-destructively.
6. Continue from the existing implementation, not a fresh rewrite.
7. In the builder log, create a concise matrix:
   - KEEP = already correct, no redo;
   - ADAPT = existing code changed only where new owner decision requires;
   - ADD = genuinely missing capability.
8. Do not run the expensive full suite before implementing the delta. Reuse previous green evidence where code is unchanged; run focused tests during work and one full suite at the end.

Never edit root `TASKS.md`.
Never write `.hiveai/audits/**`.

Builder log target:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_CODEX_LOG.md`

## 1. OWNER CORRECTION — PIXEL ART GENERATION MODEL

Do NOT have Factory Studio invent prompts, sizes, or a batch plan.

### Single mode

The owner:
- types Prompt;
- chooses Size;
- chooses Provider;
- presses Generate.

Generate produces exactly one PNG through the selected real provider.

Minimum provider choices:
- `ALPIX (Claude)`
- `MAGNIFIC`
- `PIXELLAB`

The visible provider must equal the actual executor.

### ALPIX (Claude)

This is the owner's preferred no-extra-cost path.

Use the locally authenticated Claude Code subscription session.

Do not use Anthropic API billing.

Do not use `ANTHROPIC_API_KEY` as a fallback.

Do not automate the Claude web UI.

Discover the actually installed Alpix plugin/MCP/tool from the local Claude configuration/CLI. Do not guess MCP/tool names.

Use Claude + that Alpix tool to create the requested PNG at the requested size.

If the capability is unavailable, fail closed with a short status. Do not silently use another provider.

## 2. DIRECTLY REUSE THE EARLIER EXE'S PROVEN JOB/RESUME ARCHITECTURE

The owner-supplied `ScrubBots Level Factory(3).exe` has already been inspected.

Its embedded Python 3.12 application contains `pixelart_app.py` and `art_producer.py` with the exact useful architecture:

- `find_claude()`;
- `claude_draw(...)`;
- `ArtJob.open_or_create(...)`;
- `ArtProducer.run()`;
- `read_rows(...)`;
- CSV SHA-256 job identity;
- row states `PENDING -> DRAWN -> VALIDATED -> IMPORTED`;
- `LIMIT` usage-limit pause;
- Start/Continue, Pause, Resume, Stop and per-row redo;
- restart/resume at first incomplete step;
- preservation of valid completed artifacts.

Port/reuse this logic.

Do not design another batch-state machine if the old one already solves the problem.

For ALPIX, keep the same Claude-subscription/job/resume architecture but make the drawing call use the installed Alpix plugin/MCP.

## 3. ALPIX CSV BEHAVIOR

When Provider = ALPIX and the owner selects a CSV:

- the CSV itself is the request list;
- process it row-by-row in CSV order;
- use each row's existing prompt/request;
- use row size/reference when present, otherwise the existing legacy default-size rule;
- generate one PNG;
- validate/persist it;
- advance only after durable row state is written.

Factory Studio does NOT generate the CSV.
Factory Studio does NOT rewrite all rows into a new batch plan.
Factory Studio does NOT regenerate completed rows.

### Limit

If Claude subscription usage limit is reached:

- persist state = `LIMIT`;
- stop cleanly;
- do not mark row FAILED because of quota;
- keep all prior successful PNGs;
- keep first incomplete row resumable.

When the owner later presses the batch primary action in its Resume state:

- continue the same CSV-SHA job;
- start at first incomplete row;
- do not repeat completed rows.

Reuse the existing master-defined batch action location. Do not add another production panel.

## 4. MAGNIFIC / PIXELLAB

Keep and reuse the existing provider registry/adapters.

Do not rewrite those systems.

Provider selection must route to them truthfully.

If Magnific's existing adapter is prepare/import-only, preserve that truthful contract rather than pretending an API call occurred.

If PixelLab direct execution is configured, reuse its existing official adapter and secret handling.

## 5. LEVEL FACTORY — GENERATED OR EXTERNAL PNGS

Inputs:
- PIXEL ART output;
- one external PNG;
- many external PNGs;
- existing CSV/batch referencing PNGs.

All must use the same canonical Level Factory pipeline.

For each PNG:

`PNG -> alpha/VOID QA -> supply -> official solver -> replay -> Difficulty V1 -> load/QA -> immutable bundle`

The bundle must cryptographically/immutably match:
- source PNG;
- LevelData;
- supply;
- solver proof;
- replay;
- difficulty;
- metadata;
- artwork/VOID counts;
- publication identity.

Never let derived files from one PNG bind to another PNG.

Reuse the already-closed LF19 VOID implementation.

## 6. AUTOMATIC LEVEL ORDER

Batch mode must not require the owner to type every level number.

Default is Auto.

Reuse existing canonical CampaignBuilder/release-order authority rather than creating a parallel allocator.

Rules:
- only successful READY candidates consume final publication order;
- failed/unsolved candidates consume no final level number;
- successful relative order follows input order;
- final publish plan is contiguous after the current ScrubBots catalog/history;
- retries/resume are idempotent;
- excluding a level before publish does not create a production gap.

The LEVEL FACTORY Level Number field may show the current projected/reserved next order; manual single override may remain only if already safely supported.

## 7. OWNER DECISION — READY AUTOMATICALLY ENTERS RELEASE POOL

Supersede the old rule that owner ACCEPT is required for pool eligibility.

When the canonical pipeline returns true READY:

- automatically include the candidate in Release Pool;
- do not publish it;
- continue batch processing.

The owner's human approval is the final Publish action in RELEASE POOL.

### Existing master Accept / Reject controls

Do not change master appearance.

Use them as:
- `Accept Level`: idempotently include/restore this READY candidate in Release Pool;
- `Reject`: exclude/quarantine this candidate from Release Pool.

Fresh READY defaults included.

Update release-pool eligibility/tests accordingly.

Do not require ACCEPT for publication eligibility anymore.

## 8. RELEASE POOL

Show only canonical READY, non-excluded level bundles.

Real thumbnails and canvas come from each level's actual source PNG.

Owner may select one or many.

Publish remains explicit:

`Release Pool -> ScrubPack -> preflight -> STAGING -> verification -> exact Production approval -> R2 -> ScrubBots`

No automatic publish.

No direct UI -> R2 bypass.

No hard-coded content version.

## 9. VISUALS — KEEP THE THREE MASTERS

Do not redesign the UI.

Do not undo the existing three-master work.

Keep:
`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No extra production page/panel/explanation.

At runtime, fixture owl is replaced by the real selected image when data exists.

Limit/Resume must reuse a master-defined batch control location.

## 10. TEST DELTA

Add focused permanent tests for:

1. provider selector actually changes executor;
2. ALPIX single passes owner prompt + size through Claude subscription/Alpix path;
3. no Anthropic API-key fallback;
4. legacy CSV compatibility;
5. CSV SHA job identity;
6. LIMIT is resumable, not FAILED;
7. Resume continues first incomplete row;
8. completed rows do not rerun;
9. restart resumes same job;
10. Magnific/PixelLab delegate existing adapters;
11. multi-PNG external intake;
12. immutable PNG-to-artifact matching;
13. failed PNG consumes no final production order;
14. READY auto-enters Release Pool without ACCEPT;
15. Reject excludes;
16. Accept restores;
17. no READY auto-publish;
18. final release numbering contiguous;
19. visuals remain exact three-master topology.

Run focused delta tests first.

Run the complete regression once after the delta is stable.

## 11. DURABLE RUNTIME

Keep/install final runtime at:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Desktop shortcut must launch it directly.

Preserve useful previous launcher/install work; do not rebuild it unnecessarily.

## 12. PUBLICATION / HANDOFF

Commit functional delta separately from evidence/log.

Normal fast-forward push only.

Do not force.

Final execution worktree clean and 0/0 with origin/main.

Final state:
`AWAITING_GPT_SB_LFX_018_C001_R02_R03_STRICT_REAUDIT`

Final response:
return only the GitHub builder-log URL.
