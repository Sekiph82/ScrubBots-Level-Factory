# MAINT-SUPPLY-MASTER-C001 — Independent Strict Audit

Date: 2026-10-01
Auditor: ChatGPT
Verdict: **CHANGES_REQUIRED**

## Scope

Cross-repository master package:
1. `MAINT-SUPPLY-UNCAPPED-C001` in `Sekiph82/Scrubbots`
2. `MAINT-SUPPLY-PIPELINE-V01` in `Sekiph82/ScrubBots-Level-Factory`

Builder logs:
- `Sekiph82/Scrubbots/coordination/sessions/MAINT-SUPPLY-UNCAPPED-C001/MAINT-SUPPLY-UNCAPPED-C001_CODEX_LOG.md`
- `.hiveai/codex-logs/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_CODEX_LOG.md`
- `.hiveai/codex-logs/MAINT-SUPPLY-MASTER-C001_UNCAPPED_GAME_AND_PRIMARY_PIPELINE_MASTER_CODEX_LOG.md`

Primary implementation commits:
- Game: `e1a36d317ef79d2e877aa1402d7bbca3f00606b1`
- Level Factory: `146edf6a5119c2bd372d9101ada692b0950288ca`

Current published heads at audit:
- Game main: `a85a4c6ffbd739160e7359f30dd8f7d57a4f4674`
- Level Factory main: `e1aaf606d0bb6f5e1fb0d2374b480a8a686253e9`

## Executive result

### MAINT-SUPPLY-UNCAPPED-C001 — PASS / CLOSED

Independent code inspection confirms:
- the global `MAX_ROBOTS_PER_BATCH := 30` constant was removed from shipping `SupplyPlanLoader`;
- `maxRobotsPerBatch` is retained only as positive per-plan metadata;
- individual batches remain positive exact integers and must fit that plan-local declared bound;
- exact per-color and grand-total conservation remains enforced;
- three shipping columns and preview depth 3 remain unchanged;
- tests explicitly exercise conserved 31-robot and 120-robot batches;
- existing owner plans remain unchanged.

Builder evidence records:
- relevant M23/M24/M25/M27/M52 focused gates PASS;
- full game suite `5323 checks / 0 failures`;
- Godot headless editor gate PASS.

No independent code contradiction was found.

### MAINT-SUPPLY-PIPELINE-V01 — CHANGES_REQUIRED

The owner ZIP-derived architecture was substantially and recognizably ported and the core authority separation is partially correct:
- Python `ScreeningSimulator` is used for ranking;
- current game `SolvabilitySolver.solve` is invoked through headless Godot;
- current game `SolvabilitySolver.replay` is invoked;
- current game `LevelDifficultyAnalyzerV1` can provide official Difficulty V1;
- positive uncapped per-plan batch metadata is used;
- dynamic supply depth exists;
- NumPy/Pillow are bounded offline dependencies;
- 20x20 authentic solver/replay evidence passed;
- orange-cat/butterfly screening-to-game differential replay coverage exists;
- deliberate deadlock coverage exists.

However the strict product acceptance contract is not yet closed.

## Blocking findings

### F01 — Production runtime WON gate is missing

Required:
`solve -> replay -> real production runtime/click replay -> Difficulty V1 -> acceptance`.

Actual bridge:
`src/scrubbots_pixel_factory/supply_pipeline/godot/solver_bridge.gd`

It imports:
- LevelData
- BatchSupplyEngine
- ColorBatch
- ProofState
- SolvabilitySolver
- SupplyPlanLoader
- LevelDifficultyAnalyzerV1

It does **not** instantiate or drive `ProductionGameplayHost` or another accepted shipping runtime seam.

A candidate can therefore become `READY` after proof-kernel solve/replay without the separately required real shipping runtime click-sequence reaching WON.

This is especially material because current game `ProofKernel` documentation explicitly distinguishes canonical proof timing from production runtime admission.

**Disposition: BLOCKER.**

### F02 — Shipping LevelLoader + SupplyPlanLoader load-check is not part of READY admission

`godot/load_check.gd` exists, but:
- `SupplyExporter.export()` only writes files;
- `run_primary_supply_pipeline()` returns `READY` immediately after export;
- `verify_exported_supply()` invokes the solver bridge but does not invoke `load_check.gd`.

Thus an exported result can claim `READY` without proving the exact emitted LevelData + supply plan load through the current shipping loaders.

**Disposition: BLOCKER.**

### F03 — Official Difficulty V1 is not mandatory for READY

`DifficultyModel.final()` falls back to:
`PROVISIONAL image+solver blend`
when official Difficulty V1 is absent.

`run_primary_supply_pipeline()` can still return `READY`.

For transparent/non-production input, `SupplyExporter` correctly withholds production level/supply files, but the top-level primary pipeline can still report `READY`.

Owner contract requires production difficulty authority to be current game `LevelDifficultyAnalyzerV1`, and full production acceptance must fail closed when it is unavailable.

**Disposition: BLOCKER.**

### F04 — Canonical Factory candidate/logical-grid path is not the new primary route

The new route is image-path driven:
- CLI `supply-optimize --image ...`;
- Factory Studio adds a separate `PrimarySupplyImage` control;
- `run_pipeline()` takes the new path only when `image_path` / `primary_image_path` is supplied.

Existing canonical `source_id` / `candidate_id` pipeline flow still reaches legacy:
- `SOLVE = NOT_AVAILABLE — Gameplay solver pending M03`;
- `DIFFICULTY = NOT_AVAILABLE — Measured difficulty pending M04`.

The owner requirement was to make the ZIP architecture the **primary product pipeline**, integrating existing exact Factory logical-grid/candidate identity rather than requiring PNG roundtrip/new parallel UI path.

**Disposition: BLOCKER.**

### F05 — FactoryCoreGateway capability surface still claims Solve/Analyze are unavailable

`level_factory/scripts/factory_core_gateway.gd` remains unchanged by the product commit and still hard-codes:
- `Solve = UNAVAILABLE`
- `Analyze = UNAVAILABLE`
- messages claiming M03/M04 are pending.

This conflicts with the implemented game bridge and the explicit requirement:
when authenticated local Scrubbots bridge is present, Solve and Analyze must report AVAILABLE.

**Disposition: BLOCKER.**

### F06 — Dirty/incompatible game authority is not fail-closed

`GameRules._authority_identity()` records `git rev-parse HEAD`, but does not verify:
- relevant game authority files are clean;
- local checkout corresponds to the recorded HEAD for solver/loader/difficulty/runtime authority;
- relevant source hashes or equivalent authority fingerprint.

A locally modified solver/loader/runtime script can therefore execute while evidence reports the clean commit HEAD.

Strict criteria requires dirty/incompatible authority to return UNAVAILABLE/ERROR rather than production ACCEPT.

**Disposition: BLOCKER.**

### F07 — Bridge still retypes current game constants in engine construction

Bridge response reads:
- `SupplyPlanLoader.COLUMN_COUNT`
- `SupplyPlanLoader.VISIBLE_PREVIEW_DEPTH`

but `_engine()` still constructs and validates using literal `3, 3`.

This is a smaller authority-drift seam and should use the imported authoritative constants.

**Disposition: REQUIRED REMEDIATION.**

### F08 — 37x37 and 59x59 authentic full-pipeline gates did not complete

Strict criteria required successful full end-to-end:
- 20x20
- 37x37
- 59x59

Builder evidence:
- 20x20 full real pipeline PASS;
- dynamic planning-only 20/37/59 PASS;
- the authentic 37/59 test remained CPU-active for >20 minutes and was interrupted.

An interrupted run is not a PASS.

**Disposition: BLOCKER.**

### F09 — The complete adapted 12-test ZIP suite did not pass as a complete suite

Builder reported:
- `11 passed, 1 deselected`;
- the deselected slow case is the missing 37/59 full pipeline test.

Therefore “port/adapt all 12 tests and green” is not satisfied yet.

**Disposition: BLOCKER.**

### F10 — Full Level Factory pytest is not green at builder handoff

Builder reported:
- initial full regression: `1120 passed, 3 skipped, 2 failed`;
- one new secret-scan failure was corrected;
- one active-task/TASKS contract failure remained.

The protected tracker mismatch is auditor-owned, not builder product code, but strict closure still requires a final green full regression after tracker/remediation state is synchronized.

**Disposition: REVERIFY IN R01.**

## Non-blocking positives retained

- No evidence of Python screening being used as final solver authority in the core optimizer.
- Deliberate unsolvable candidate requires real game solver and is rejected.
- Supply conservation verifier is explicit and fail-closed.
- Dynamic row computation is not fixed at 18.
- Global batch count cap 30 is absent from the new optimizer path.
- Current game HEAD is recorded in result authority metadata.
- NumPy/Pillow dependency ranges are bounded.
- Offline/no-cloud boundary remains intact.
- Root `TASKS.md` and audit paths were not modified by builder implementation.
- No new branch/Desktop sibling worktree was reported.

## Master verdict

`MAINT-SUPPLY-UNCAPPED-C001 = PASS/CLOSED`

`MAINT-SUPPLY-PIPELINE-V01 = CHANGES_REQUIRED`

`MAINT-SUPPLY-MASTER-C001 = CHANGES_REQUIRED`

The existing ZIP-derived core is retained. R01 must close the product-authority and full-size evidence gaps without replacing the optimizer architecture.
