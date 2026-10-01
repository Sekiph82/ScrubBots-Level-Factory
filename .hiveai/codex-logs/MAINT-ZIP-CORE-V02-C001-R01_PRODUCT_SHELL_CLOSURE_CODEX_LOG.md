# MAINT-ZIP-CORE-V02-C001-R01 — Product Shell Closure

Document role: CODEX BUILDER LOG

## Start and synchronization preflight

- Start timestamp: 2026-10-02 (Europe/Istanbul client date).
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical local root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Active branch: `main`.
- Authoritative prompt: `.hiveai/prompts/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_PROMPT.md`.
- Initial local HEAD before preflight: `0feae1b6f2de0fe1aa297f3cb96a98a8a39a3796`.
- `git fetch origin --prune`: succeeded.
- Initial `origin/main`: `45ae81bc4d0eded26a37e3d7486f035f8c787173`; local main was behind by 5 commits with no tracked modifications.
- Initial tracked status: clean. Pre-existing untracked owner/workspace material, including sibling historical folders and Godot `.uid` files, was preserved.
- Stashes and worktree records were inspected and left unchanged.
- Safe synchronization: `git merge --ff-only origin/main` succeeded.
- Synchronized HEAD: `45ae81bc4d0eded26a37e3d7486f035f8c787173`.
- Post-sync divergence: `0/0` against `origin/main`.

## Authorized source set

- `AGENTS.md`.
- `GOVERNANCE.md`.
- Root `TASKS.md` as the sole current task-state authority.
- `.hiveai/prompts/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_PROMPT.md`.
- `.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_AUDIT_CRITERIA.md`.
- `.hiveai/audits/MAINT-ZIP-CORE-V02-C001-LF_ONLY_STRICT_AUDIT.md`.
- `.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CODEX_LOG.md`.
- `docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md`.
- The authoritative GitHub prompt URL supplied in the handoff was read before implementation.

## Builder boundary

- This log records implementation evidence only. It does not declare independent audit acceptance.
- Only the Level Factory repository is in scope. The Scrubbots checkout is read-only authority for solver, replay, Difficulty V1, progression/catalog inspection, and load validation; implementation tests may publish only to isolated `%TEMP%` fixtures.
- Root `TASKS.md`, `.hiveai/audits/**`, `.hiveai/HANDOFF.md`, and used prompts remain owner-controlled and are not edited.

## Implementation ledger

- Product implementation has not started at log creation.
- Subsequent commands, decisions, failures, corrections, files, tests, and publication results will be appended chronologically below.

## Chronological implementation and verification evidence

- Implemented the current difficulty-free artwork request schema (schema version 3) with explicit width, height, seed, generator mode, optional style/theme/palette/options, and explicit `BACKGROUND` or `TRANSPARENT` intent. Legacy difficulty-bearing request metadata remains available only through the explicit legacy schema path.
- Removed current CLI `--difficulty` arguments from `generate` and `batch`, removed gateway `--difficulty EASY` injection, removed the Studio difficulty control/readout, and migrated current request, preset, metadata, and evidence surfaces to the new schema/background contract.
- Added current dimension and palette-subset contracts. Current dimensions use the independent production envelope and stable seed selection; current quality validation does not accept requested difficulty. Added the missing inclusive `DimensionBand.span` helper discovered by the auto-dimension integration test.
- Added read-only canonical game capability probing and routed Studio Solve/Analyze through the same ZIP-derived supply/solve/Difficulty V1 route. Capability state is available only when Factory Core, canonical ZIP modules, the configured read-only game checkout, and Godot are available; otherwise it reports a truthful unavailable reason.
- Added external OWNER_UPLOAD derivation with immutable source lineage, exact logical artwork identity, candidate ID, and the same ZIP pipeline. Transparent uploads remain reviewable artwork but are non-publishable until a legitimate opaque full-canvas variant exists.
- Added shipping load-check gating after solve/replay/Difficulty V1/export and before publication eligibility. Readiness now includes the `LOAD_CHECK` gate and records authority and file evidence.
- Added `supply_pipeline/game_publisher.py`, a bounded transactional publisher targeting an explicit game project or `SCRUBBOTS_PROJECT`. It validates project identity, progression/config/catalog authority, immutable ID collisions, required output paths, metadata, and file digests; stages outputs transactionally and prevents partial or silent conflicting publication.
- Replaced global difficulty-score sorting with the current game progression cadence/target policy and documented deterministic tie-breaking and fail-closed placement behavior.
- Preserved the ZIP tuning invariants: candidates 300, original plus at most three mutations, screening/viability budgets 3000, game-default solver budget, scorer weights, mean-batch seed ranges, internal complexity/search-band heuristic, ranking-only screening, solve/replay/SolutionVerifier authority, and no global batch cap.
- Updated active tests and Studio integration fixtures for the current request/schema, background intent, dynamic capabilities, derived upload candidates, load-check readiness, transactional publication, and current UI truth separation. Historical reproduction tests remain explicit legacy coverage.

### Commands and corrections

- `python -m compileall -q src level_factory`: passed during implementation and at final gate.
- `godot_console.exe --headless --path level_factory --quit`: passed at final gate.
- `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_runtime_suite.gd`: passed with `SB-LF06-002-C001-R01 committed runtime suite PASS`.
- Early gateway headless parsing exposed an extra closing brace after the capability/action changes; removed only that syntax defect and reran the headless checks successfully.
- Current CLI checks passed for difficulty-free `generate` and `batch`, including explicit dimensions, schema 3 metadata, background intent, and no requested difficulty. Transparent procedural generation and transparent batch publication fail closed truthfully where the mode cannot provide opaque shipping artwork.
- The isolated OWNER_UPLOAD action was exercised through derived candidate creation, canonical solve/replay, official Difficulty V1, and shipping load-check. The source bytes remained unchanged and the derived candidate carried source lineage.
- The publisher was exercised against a unique `%TEMP%` Scrubbots fixture only. It wrote all five required artifacts transactionally, produced a progression placement from current cadence/target authority, and returned file digests. The live `C:\Users\sekip\Desktop\ScrubBots` checkout was not written.
- Initial focused runtime test failed because the test still looped over removed difficulty controls; migrated it to current width/height/background checks. The focused runtime gate then passed.
- Initial focused Studio action tests exposed stale puzzle-config and truth-separation assertions; migrated those assertions to current controls and reran them successfully. Dashboard, puzzle-config, truth-separation, and exact-reproduction headless integration markers all passed.
- Initial unit run reached `927 passed, 2 skipped, 2 failed`. One failure was the stale exact-reproduction integration contract and the other was the stale runtime difficulty loop; both were migrated and rerun successfully.
- `python -m pytest -q tests/unit`: final result `929 passed, 2 skipped` with only the documented unavailable canonical-game bridge skips.
- `python -m pytest -q tests/integration/test_maint_supply_pipeline_v01.py`: `12 passed, 1 skipped`; this includes deterministic planning and uncapped `>30` batch compatibility evidence.
- The first full `python -m pytest -q` exposed 56 stale M09 CLI integration calls still passing removed `--difficulty EASY`. Removed those superseded current arguments with `apply_patch`, then fixed the seven follow-on migration issues: current schema 3 assertions, current difficulty-free quality policy fixtures, inclusive auto-dimension span, and legacy-v1 batch template canonicalization.
- `python -m pytest -q tests/integration/test_m09_cli_integration.py`: final result `62 passed`.
- Final `python -m pytest -q`: `1132 passed, 3 skipped, 1 warning in 511.37s`. The three skips are truthful environment-capability skips: slow supply pipeline opt-in and unavailable canonical-game bridge cases. The warning was a Windows pytest cache permission warning and did not affect results.

### Live 3/4/5-column revalidation

- Read-only canonical game authority was inspected from `C:\Users\sekip\Desktop\ScrubBots`: repository `Sekiph82/Scrubbots`, branch `main`, authority HEAD `105401e8f549807014234c7c8e9ec250b322034c`, loader `scripts/gameplay/supply/supply_plan_loader.gd`, solver `scripts/gameplay/solver/solvability_solver.gd`, Difficulty V1 analyzer `scripts/difficulty/level_difficulty_analyzer_v1.gd`.
- The authority reported `MIN_COLUMNS=3`, `MAX_COLUMNS=5`, preview depth 3, and live verification available for 3, 4, and 5 columns.
- Against a generated 20x20 candidate and isolated `%TEMP%` output, `run_primary_supply_pipeline(..., candidates=300, column_count=3/4/5)` returned `READY`, solver `SOLVED`, replay `WIN`, and official Difficulty V1 for each selected count.
- `verify_exported_supply` independently load-checked the emitted level and supply for each count: all three returned `READY`, solver `SOLVED`, replay solved, `all_ok=True` exact conservation, and preserved selected column count. Preview depth was 3 and baseline slot count was read from the authority as 5.
- No ScrubBots source, data, catalog, progression, or live game output was mutated during these checks.

### Offline, safety, and dependency observations

- Current core generation and CLI regression checks ran without runtime network access; the network-blocked-boundary integration test passed.
- No cloud image generation, telemetry, remote runtime API, API key, or runtime HTTP dependency was added.
- No dependency or license changes were made.
- Publisher tests used only isolated temporary fixtures. Owner/local untracked folders and generated `.uid` material were not reset, cleaned, deleted, stashed, or staged.
- Root `TASKS.md`, `.hiveai/audits/**`, `.hiveai/HANDOFF.md`, and active prompt files remained untouched.
- `git diff --check`: passed; line-ending warnings are the repository's existing Windows normalization behavior.

### Files changed before publication

- Product/core: `src/scrubbots_pixel_factory/**` current contracts, request/result/output, CLI, owner upload, Studio extension bridge, progression, load-check, and new `supply_pipeline/game_publisher.py`.
- Studio shell: `level_factory/scripts/**` bounded gateway/launcher and current target, import, evidence, readiness, dashboard, editor, and revalidation surfaces; `level_factory/docs/**` implementation documentation.
- Verification: current Studio headless integration suites and migrated Python unit/integration tests, including `tests/integration/test_m09_cli_integration.py`.
- This builder log is the only `.hiveai` file created or modified for this task.
