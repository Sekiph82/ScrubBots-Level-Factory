# MAINT-SUPPLY-PIPELINE-V01 — Primary Supply / Solver / Difficulty Pipeline

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Owner decision:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V01.md

Strict audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_AUDIT_CRITERIA.md

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

Game authority:
https://github.com/Sekiph82/Scrubbots

Game-side uncapped owner decision:
https://github.com/Sekiph82/Scrubbots/blob/main/coordination/OWNER_UNCAPPED_BATCH_ROBOT_COUNT_DECISION_V01.md

## Mandatory local ↔ GitHub main sync preflight

Before any product edit:

1. Work only in:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity `Sekiph82/ScrubBots-Level-Factory` and branch `main`.
3. `git fetch origin --prune`.
4. Inspect HEAD/origin-main, dirty state, stashes, worktrees, ahead/behind.
5. Clean/behind => `git merge --ff-only origin/main`.
6. Legitimate local work => preserve non-destructively and normal-merge only when safe.
7. Never reset, rebase, stash, clean, force checkout, force push, discard owner work.
8. Never create a new branch or sibling Desktop clone/worktree.
9. Begin implementation only after local main is safely synchronized.
10. If safe sync cannot be completed, stop before product edits.

## Source intake

The owner-supplied ZIP must be provided to this Codex run.

Do not search Desktop sibling folders for it.

Accept the explicit attached/source path only.

Before extraction:
- compute SHA-256;
- require exact match:
  `c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`.

Extract only to:
`%TEMP%\ScrubBots-Level-Factory\owner-supply-v01\`

Never extract/create a sibling Desktop project directory.

Read in this order before coding:
1. ZIP `README.md`
2. ZIP `PORT_PROMPT_screening_simulator.md`
3. ZIP `godot/solver_bridge.gd`
4. all remaining ZIP modules/tests
5. repository owner decision + audit criteria
6. current Factory code/contracts
7. current Scrubbots authority scripts used by bridge

## Objective

Make the supplied ZIP architecture the primary product supply/solve/difficulty pipeline inside the Level Factory.

Do not implement it as a detached demo.

Port/adapt its algorithms into the canonical package and Factory Studio.

## Required module family

Preserve recognizable product modules under a canonical package such as:
`src/scrubbots_pixel_factory/supply_pipeline/`

Required concepts/modules:
- supply_optimizer.py
- candidate_generator.py
- scrubbots_solver.py
- supply_scorer.py
- solution_verifier.py
- supply_exporter.py
- screening.py
- batch_planner.py
- pixel_analyzer.py
- difficulty_model.py
- game_rules.py
- Godot solver/load bridges
- tests

You may adapt imports/types/contracts to existing Factory architecture, but do not replace the owner-proven optimizer with an unrelated implementation.

## Canonical pipeline

Implement:

```
canonical logical artwork/candidate
 -> PixelAnalyzer
 -> DifficultyModel search band/mean seed
 -> BatchPlanner
 -> SupplyCandidateGenerator + bounded mutations
 -> ScreeningSimulator ranking only
 -> SupplyScorer ranking
 -> authentic current Scrubbots Godot bridge
 -> SolvabilitySolver.solve
 -> SolvabilitySolver.replay
 -> production runtime/click replay
 -> LevelDifficultyAnalyzerV1
 -> SolutionVerifier
 -> SupplyExporter
 -> LevelLoader/SupplyPlanLoader load check
 -> existing Factory QA/review/handoff
```

## Critical trust rule

ScreeningSimulator is never acceptance authority.

Even if screening says SOLVED:
- no final ACCEPT without current-game `SolvabilitySolver.solve`;
- no final ACCEPT without replay completion;
- no final ACCEPT without production-runtime replay gate;
- no final difficulty without official `LevelDifficultyAnalyzerV1`;
- no export-ready state without shipping loader validation.

If authentic game capability is unavailable, return UNAVAILABLE/ERROR.

Never fall back to old Python solver/difficulty as production truth.

## Current-game compatibility

Resolve current Scrubbots main at runtime/preflight.

The bridge must consume the current shipping scripts rather than copy them:
- LevelData
- BatchSupplyEngine
- ColorBatch
- ProofState
- SolvabilitySolver
- ProofKernel / runtime seam as needed
- SupplyPlanLoader
- LevelDifficultyAnalyzerV1
- LevelLoader

Do not modify the game repository from this prompt.

The separate game-side maintenance must remove the stale global 30 cap.

Until that change is present, >30 load-check readiness must truthfully remain blocked.

## No global robot cap

The Level Factory optimizer is uncapped:
- positive integer batches only;
- no `30` ceiling;
- exact per-color and grand conservation.

Do not use `batch_cap=30` anywhere in the canonical product path.

Supply-plan `maxRobotsPerBatch` may be emitted as actual per-plan maximum metadata for v1 compatibility, not as a game-wide cap.

## Dynamic supply rows

No fixed 18 rows.

Rows = actual maximum FIFO depth produced by optimized batch count / game column count.

Retain bounded search and candidate count settings.

## Canonical input adaptation

Integrate with existing Factory candidate bundles/logical cells.

Add a canonical-grid path so the supply pipeline can consume existing exact logical grid + palette identities directly.

Do not rasterize/re-read PNG just to recover logical cells.

Keep PNG input support only where useful for owner/source import and enforce exact palette/no silent quantization.

## Existing Factory contracts

Connect results to:
- canonical candidate identity/provenance;
- LevelData V1 identity;
- M05 QA/report evidence;
- owner review queue;
- production readiness/handoff.

Historical solver/difficulty modules may remain but the default Pipeline action must route through this new primary supply pipeline.

## CLI / launcher / Studio

Add canonical CLI commands, at minimum:
- `supply-optimize`
- `supply-verify` or equivalent authenticated verification path.

Update:
- `level_factory/scripts/factory_core_launcher.py`
- `level_factory/scripts/factory_core_gateway.gd`
- Factory Studio Pipeline surface/back-end

When bridge capability is present:
- Solve = AVAILABLE
- Analyze = AVAILABLE
- supply optimization evidence visible

When absent:
- truthful UNAVAILABLE.

Do not invent UI-only success.

## Dependencies

Add bounded Python 3.12-compatible NumPy and Pillow dependencies.

Update setup/test and third-party notices.

No runtime internet/API dependency.

## Bridge strengthening

Adapt the ZIP bridge to current game authority.

Required improvements:
- do not reference a removed `SupplyPlanLoader.MAX_ROBOTS_PER_BATCH` constant;
- use authoritative current column/preview constants rather than retyping 3/3 where practical;
- include game HEAD/authority identity in response;
- keep real solve + replay;
- keep official Difficulty V1;
- add/execute a headless production-runtime/click sequence gate using current shipping gameplay seam;
- add shipping LevelLoader/SupplyPlanLoader load check for exports.

## Evidence / tests

Port the ZIP test suite and add the strict criteria cases.

Mandatory real-game runs:
- orange cat differential;
- butterfly replay;
- deliberate deadlock;
- 20x20;
- 37x37;
- 59x59;
- valid >30 batch after game-side uncapped loader exists;
- deterministic repeat.

Mandatory evidence must record:
- screening visited/trace;
- game solve status/visited/trace hash;
- replay result;
- runtime result;
- official Challenge Score/vector/class;
- supply row/batch counts;
- conservation;
- export/load result;
- game HEAD SHA.

## Product status

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

Create builder log before product edits:
`.hiveai/codex-logs/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_CODEX_LOG.md`

## Gates

Run focused supply-pipeline tests, complete existing Factory pytest, compileall, all Factory Studio Godot headless suites, relevant cross-repo read-only Scrubbots solver/runtime/load tests, diff check and protected-file no-diff checks.

Do not spend provider/API credits for tests.

Push directly to `main`, verify local HEAD == origin/main and 0/0, then stop for independent ChatGPT audit.

## Final response

Return only the full GitHub URL of the builder log.
