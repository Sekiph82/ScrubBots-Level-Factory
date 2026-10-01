# MAINT-SUPPLY-MASTER-C001 — Uncapped Game Supply + Primary Level Factory Pipeline

Document role: MASTER CROSS-REPOSITORY IMPLEMENTATION PROMPT

## Owner directive

Execute BOTH work packages in strict order and finish both before stopping:

1. **MAINT-SUPPLY-UNCAPPED-C001** — remove the stale global 30-robots-per-batch ceiling from the shipping Scrubbots game.
2. **MAINT-SUPPLY-PIPELINE-V01** — port the owner-supplied ZIP pipeline into ScrubBots-Level-Factory as the primary production supply / solve / difficulty pipeline.

Do not start unrelated roadmap work.
Do not resume SB-LF09-004 telemetry until this master package is independently audited.

---

# Repositories

Game authority:
https://github.com/Sekiph82/Scrubbots

Level Factory:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Canonical local Level Factory root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

The Scrubbots game must use its existing canonical local repository only.
Do not create new Desktop sibling clones, worktrees, remediation copies, or branches in either repository.

---

# Mandatory sync preflight — BOTH repositories

Before edits in each repository:

1. Verify exact repository identity.
2. Verify current branch is `main`.
3. Run `git fetch origin --prune`.
4. Record:
   - local HEAD;
   - `origin/main`;
   - `git status --short --branch`;
   - ahead/behind;
   - stashes;
   - registered worktrees.
5. If clean and only behind, fast-forward with `git merge --ff-only origin/main`.
6. If legitimate local work exists, preserve it non-destructively and reconcile with a normal merge when safe.
7. Never use reset, rebase, stash, clean, force checkout, force push, or destructive overwrite.
8. Never create a new branch/worktree/Desktop clone unless explicitly owner-authorized.
9. Product work begins only after safe synchronization.
10. If safe sync cannot be completed, stop before edits and report the blocker.

---

# WORK PACKAGE 1 — MAINT-SUPPLY-UNCAPPED-C001

Repository:
https://github.com/Sekiph82/Scrubbots

Owner decision:
https://github.com/Sekiph82/Scrubbots/blob/main/coordination/OWNER_UNCAPPED_BATCH_ROBOT_COUNT_DECISION_V01.md

Existing detailed prompt:
https://github.com/Sekiph82/Scrubbots/blob/main/coordination/sessions/MAINT-SUPPLY-UNCAPPED-C001/task_prompts/MAINT-SUPPLY-UNCAPPED-C001_REMOVE_GLOBAL_BATCH_ROBOT_CAP.md

## Required result

The former global `MAX_ROBOTS_PER_BATCH = 30` rule is retired.

Canonical behavior:
- every batch robot count is an exact positive integer;
- there is NO fixed global maximum;
- exact per-color conservation remains mandatory;
- exact grand-total conservation remains mandatory;
- FIFO order remains authoritative;
- shipping supply remains three columns / visible preview depth three unless a separate owner decision changes it;
- existing Levels 2–10 plans remain compatible and unchanged;
- plan-local `maxRobotsPerBatch` may remain as declarative metadata, but it is NOT a game-wide ceiling.

## Required game changes

At minimum inspect/update:
- `scripts/gameplay/supply/supply_plan_loader.gd`
- relevant M52 supply-plan tests;
- comments/docs that claim 1..30 or max <=30;
- any bridge/tool code that references `SupplyPlanLoader.MAX_ROBOTS_PER_BATCH`.

Do not redesign gameplay.

## Mandatory game evidence

Prove:
- existing Levels 2–10 still load;
- 0, negative, fractional counts fail;
- malformed/conservation failures fail;
- a valid conserved batch of 31 loads;
- a valid conserved substantially larger positive batch loads;
- uncapped fixture solves via real `SolvabilitySolver`;
- replay reaches solved state;
- relevant M23/M24/M25/M27/M52 regressions pass;
- full game test gates pass.

Commit and push this work to Scrubbots `main`.

Do not proceed to Work Package 2 until:
- game local HEAD == origin/main;
- ahead/behind = 0/0;
- uncapped evidence is committed and pushed.

---

# WORK PACKAGE 2 — MAINT-SUPPLY-PIPELINE-V01

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Owner decision:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V01.md

Strict audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_AUDIT_CRITERIA.md

Existing detailed prompt:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_PROMPT.md

Owner ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## Source intake

Use the owner-provided ZIP for this task.

Before extraction:
- compute SHA-256;
- require exact match to the SHA above.

Extract only under:
`%TEMP%\ScrubBots-Level-Factory\owner-supply-v01\`

Never extract a second project copy onto Desktop.

Read first, in this order:
1. `README.md`
2. `PORT_PROMPT_screening_simulator.md`
3. `godot/solver_bridge.gd`
4. all remaining ZIP modules/tests.

## ZIP module family that must become the product core

Port/adapt these into the canonical Level Factory package:

- `supply_optimizer.py`
- `candidate_generator.py`
- `scrubbots_solver.py`
- `supply_scorer.py`
- `solution_verifier.py`
- `supply_exporter.py`
- `screening.py`
- `batch_planner.py`
- `pixel_analyzer.py`
- `difficulty_model.py`
- `game_rules.py`
- `godot/solver_bridge.gd`
- `godot/load_check.gd`
- port/adapt all 12 tests from `tests/test_supply_pipeline.py`.

Preferred canonical package:
`src/scrubbots_pixel_factory/supply_pipeline/`

Do not replace the ZIP optimizer with an unrelated implementation.

---

# PRIMARY PRODUCT PIPELINE

The default Level Factory production path must become:

```
canonical artwork / logical grid
 -> PixelAnalyzer
 -> DifficultyModel search seed/band
 -> BatchPlanner
 -> SupplyCandidateGenerator
 -> ScreeningSimulator
 -> SupplyScorer
 -> ScrubBotsSolver Godot bridge
 -> REAL GAME SolvabilitySolver.solve
 -> REAL GAME SolvabilitySolver.replay
 -> REAL production-runtime/click replay gate
 -> REAL GAME LevelDifficultyAnalyzerV1
 -> SolutionVerifier
 -> SupplyExporter
 -> game LevelLoader + SupplyPlanLoader load-check
 -> existing Factory QA / owner review / readiness / handoff
```

## Non-negotiable authority boundary

Python `ScreeningSimulator` is ONLY a fast ranking/screening system.

It is NEVER production acceptance authority.

Production acceptance requires current authentic Scrubbots game evidence:
1. `SolvabilitySolver.solve == SOLVED`;
2. solution trace replay succeeds;
3. final ACTIVE=0;
4. supply exhausted;
5. slots empty;
6. production-runtime/click sequence reaches valid completion;
7. current official `LevelDifficultyAnalyzerV1` returns the production difficulty;
8. exported LevelData/supply plan pass current shipping loaders.

If game/Godot authority is unavailable or incompatible:
- final disposition is UNAVAILABLE/ERROR;
- never fall back to Python screening as ACCEPT.

## Difficulty rule

Use the ZIP's image/supply difficulty heuristics to GUIDE search and ranking.

Final production Challenge Score / difficulty class must come from the current Scrubbots `LevelDifficultyAnalyzerV1`.

No second canonical difficulty authority.

## Robot-count rule

There is no global maximum robot count per batch.

Do not introduce 30 in:
- planner;
- generator;
- mutation;
- scorer;
- exporter;
- bridge;
- verification;
- Factory Studio.

Counts must remain positive integers and exactly conserved.

## Dynamic supply depth

No fixed 18-row supply.

Supply depth is derived from actual optimizer output / FIFO batch count.

Prove dynamic scaling on representative 20x20, 37x37 and 59x59 cases.

## Input integration

Prefer the existing Factory canonical logical-grid candidate as input.

Do not rasterize canonical cells to PNG and then re-read them unnecessarily.

PNG/source-image input may remain supported, but:
- exact palette only;
- no silent quantization;
- explicit alpha semantics;
- source hash retained.

## Factory integration

Make this the default product path, not a detached utility.

Integrate with:
- canonical candidate provenance;
- existing Factory CLI;
- `level_factory/scripts/factory_core_launcher.py`;
- `level_factory/scripts/factory_core_gateway.gd`;
- Factory Studio Pipeline;
- existing M05 QA evidence;
- owner review queue;
- production readiness;
- Content Pipeline handoff.

When the authenticated local Scrubbots bridge exists:
- Solve must be AVAILABLE;
- Analyze must be AVAILABLE.

When unavailable:
- show truthful UNAVAILABLE.

Historical M03/M04/M05 code may remain for regression/evidence/adapter purposes but must not silently bypass the new approved default pipeline.

## Dependencies

NumPy and Pillow are approved local/offline dependencies.

Add bounded Python 3.12-compatible dependency ranges and update setup/tests/notices.

No cloud/API/runtime internet dependency.

---

# REQUIRED REAL-GAME EVIDENCE

At minimum:

1. `level_004_orange_cat`
   - screening trace compared to game trace / clear progression.
2. `level_008_butterfly`
   - screening-generated solution replays through real game to solved.
3. deliberate unsolvable/deadlock
   - real game rejects.
4. 20x20 full pipeline
   - optimize -> game solve -> replay -> runtime -> Difficulty V1 -> export/load.
5. 37x37 full pipeline
   - same.
6. 59x59 full pipeline
   - same.
7. valid >30 batch
   - game loader accepts under uncapped contract;
   - solver/replay passes.
8. deterministic rerun
   - identical source/settings/seed/game authority => identical canonical supply/evidence.
9. no fixed 18 rows.
10. every generation and mutation preserves exact color conservation.
11. malformed/off-palette input fails closed.
12. game authority missing => no production ACCEPT.
13. screening/game divergence => game wins and divergence is recorded.
14. final export passes shipping LevelLoader + SupplyPlanLoader.

## ZIP regression

Port/adapt and pass all 12 ZIP tests.

Also run:
- full Level Factory pytest;
- compileall;
- Factory Studio Godot headless suites;
- relevant current Scrubbots read-only solver/runtime/load tests;
- git diff --check.

No provider/API credit spend.

---

# BUILDER LOGS

Game log:
`coordination/sessions/MAINT-SUPPLY-UNCAPPED-C001/MAINT-SUPPLY-UNCAPPED-C001_CODEX_LOG.md`

Level Factory log:
`.hiveai/codex-logs/MAINT-SUPPLY-PIPELINE-V01_PRIMARY_SUPPLY_SOLVER_DIFFICULTY_PIPELINE_CODEX_LOG.md`

Master log:
`.hiveai/codex-logs/MAINT-SUPPLY-MASTER-C001_UNCAPPED_GAME_AND_PRIMARY_PIPELINE_MASTER_CODEX_LOG.md`

Create logs before corresponding product edits.

Do not edit Level Factory root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

---

# COMMIT / PUSH ORDER

1. Synchronize Scrubbots main.
2. Implement uncapped game supply contract.
3. Test.
4. Commit/push Scrubbots main.
5. Verify 0/0.
6. Synchronize Level Factory main again so it includes latest governance/prompt state.
7. Port/integrate ZIP primary pipeline.
8. Run cross-repo authentic game evidence against the updated Scrubbots main.
9. Test Level Factory.
10. Commit/push Level Factory main.
11. Publish Level Factory per-task log.
12. Publish master log.
13. Verify Level Factory local HEAD == origin/main and 0/0.
14. STOP for independent ChatGPT audit.

Do not continue to SB-LF09-004 in the same run.

---

# FINAL RESPONSE

Return ONLY these 3 full GitHub URLs:

1. game uncapped builder log;
2. Level Factory primary pipeline builder log;
3. master builder log.
