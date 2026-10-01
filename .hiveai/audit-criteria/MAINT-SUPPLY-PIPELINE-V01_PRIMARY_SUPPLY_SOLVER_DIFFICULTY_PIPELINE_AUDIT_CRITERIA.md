# MAINT-SUPPLY-PIPELINE-V01 — Primary Supply / Solver / Difficulty Pipeline — Strict Audit Criteria

Owner decision:
`docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V01.md`

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## Verdict rule

PASS only if the supplied ZIP architecture becomes the default production Level Factory supply/solve/difficulty path while Python screening remains ranking-only and all production acceptance is proven by current authentic Scrubbots game code.

## Mandatory source fidelity

The implementation must port/adapt the owner-supplied source family:
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
- godot/solver_bridge.gd
- godot/load_check.gd
- tests/test_supply_pipeline.py

Do not replace it with a materially different optimizer under the same name.

Allowed adaptation:
- package paths;
- existing Factory typed/provenance contracts;
- deterministic RNG/provenance integration;
- canonical-grid input instead of rendered-PNG roundtrip;
- current game authority drift;
- uncapped batch-count decision;
- Factory Studio/CLI integration;
- stronger runtime/load/identity gates.

## Primary product path

The default production orchestration must be:

canonical artwork/logical grid
-> PixelAnalyzer
-> DifficultyModel generation seed/band
-> BatchPlanner
-> SupplyCandidateGenerator
-> ScreeningSimulator
-> SupplyScorer
-> ScrubBotsSolver bridge
-> game SolvabilitySolver.solve
-> game SolvabilitySolver.replay
-> production runtime/click-sequence validation
-> game LevelDifficultyAnalyzerV1
-> SolutionVerifier
-> SupplyExporter
-> game LevelLoader + SupplyPlanLoader load check
-> existing Factory QA/review/handoff evidence.

No second competing production solve/supply/difficulty route may be silently selected.

Historical M03/M04/M05 code may remain for compatibility/evidence, but it must not supersede the approved product path.

## Trust boundary

ScreeningSimulator:
- ranking/screening only;
- may reject/rank candidates;
- may provide advisory gameplay metrics;
- may not mark production accepted;
- may not provide canonical Difficulty V1;
- may not substitute for missing game authority.

Production acceptance requires exact current game checkout evidence.

If game/Godot authority is unavailable, stale, dirty/incompatible, or bridge execution fails:
- final acceptance = UNAVAILABLE/ERROR;
- no fallback to Python screen SOLVED;
- no fabricated difficulty.

## Game authority binding

Every accepted result must bind:
- canonical Scrubbots repository URL;
- exact game HEAD SHA;
- exact relevant source identities/digests or a versioned authority fingerprint;
- bridge version;
- LevelData identity;
- supply-plan identity;
- solution trace/hash;
- replay result;
- official Difficulty V1 result;
- load-check result.

Do not pin forever to stale source SHA. Resolve/verify current main at execution time under the repository's accepted authority rules.

## Uncapped robot count

Owner rule:
- no fixed global robots-per-batch max;
- every count positive integer;
- exact per-color and grand conservation;
- existing plan field may record actual/per-plan max metadata;
- do not reintroduce 30 as a hidden optimizer or exporter ceiling.

A >30 accepted/loadable fixture is mandatory.

## Dynamic supply size

- no fixed 18-row supply.
- rows derive from actual optimized batch count / shipping column count.
- 20/37/59 examples must demonstrate scaling.
- shipping columns remain current game-authoritative count (currently 3), not a hardcoded retyped constant where an authority source exists.

## Difficulty

Final difficulty class/score must come from official current-game LevelDifficultyAnalyzerV1 evidence.

Allowed search inputs:
- image complexity;
- target band;
- mean-batch tuning seed;
- SupplyScorer ranking score/pressure metrics.

These may guide search but cannot become production Difficulty V1 authority.

## Full-canvas production rule

Under current LevelData V1:
- transparent pixels may be analyzed/screened as experimental input;
- transparent output cannot be exported as a production game level unless the game contract changes;
- fail/mark PROVISIONAL truthfully.

## Factory integration

Required product integration:
- package code under the canonical `scrubbots_pixel_factory` package, not a detached sibling utility;
- canonical CLI operation for supply optimize/solve/export;
- `level_factory/scripts/factory_core_launcher.py` route;
- `FactoryCoreGateway` capability surface;
- Factory Studio Pipeline uses the new supply/solve/difficulty route;
- Solve/Analyze must no longer be falsely shown UNAVAILABLE when the authenticated local game bridge is available;
- output stays under approved Factory output roots;
- existing candidate provenance, QA, owner review and handoff remain connected.

The Studio UI may expose separate Optimize/Solve/Analyze controls, but all must use the same canonical backend evidence.

## Input identity

Prefer canonical logical-grid/candidate input from existing Factory bundles.

Do not require lossy PNG re-encoding to recover already-canonical logical cells.

If PNG is accepted:
- exact palette only;
- no silent quantization;
- alpha semantics explicit;
- source hash retained.

## Dependencies

NumPy and Pillow may be added as approved local/offline dependencies.

Requirements:
- compatible with Python 3.12;
- pinned to bounded major ranges;
- THIRD_PARTY_NOTICES/license metadata updated;
- no runtime HTTP/cloud dependency;
- setup/test scripts install/verify them safely.

## Determinism

Same:
- source grid/artifact identity;
- optimizer version;
- settings;
- seed;
- game authority;
must reproduce same candidate ranking, selected supply and canonical evidence, excluding noncanonical elapsed timing.

Do not place wall-clock timing in canonical identity.

## Required differential and adversarial evidence

1. level_004_orange_cat:
   - screening and real-game trace/step clears/active-after agree for accepted reference path.
2. level_008_butterfly:
   - screening solution replays through real game to WIN.
3. deliberate enclosed unsolvable:
   - Python may identify DEADLOCK;
   - authentic game solver must reject production.
4. 20x20 full pipeline:
   - SOLVED + replay + runtime + Difficulty V1 + export/load.
5. 37x37 full pipeline:
   - same.
6. 59x59 full pipeline:
   - same.
7. >30 valid batch:
   - authentic uncapped shipping loader accepts it;
   - solve/replay passes.
8. exact same seed/settings:
   - byte/identity deterministic canonical supply output.
9. dynamic rows:
   - 20 < 37 < 59 in appropriate workload fixture;
   - no fixed 18.
10. conservation:
   - generation and every mutation preserve exact per-color counts.
11. malformed/off-palette:
   - fail closed.
12. game authority unavailable:
   - no production ACCEPT.
13. screening divergence:
   - real game wins authority; divergence is recorded and candidate rejected/quarantined as needed.
14. exported files:
   - LevelLoader + SupplyPlanLoader load successfully.
15. old pipeline bypass:
   - prove product Factory Pipeline cannot mark supply/solve/difficulty accepted without this bridge path.

## Regression gates

- supplied ZIP 12-test suite ported/adapted and green;
- existing Level Factory full pytest green except accepted capability skips;
- compileall green;
- Factory Studio headless Godot suite green;
- relevant current Scrubbots M23/M24/M25/M27/M52/Difficulty tests green;
- game-side uncapped loader maintenance must be complete before production-ready PASS;
- git diff check green;
- no TASKS/audits builder edits;
- no extra Desktop clone/worktree.

## Audit focus

Particular failure conditions:
- Python ScreeningSimulator treated as solver authority;
- official difficulty replaced by ZIP heuristic score;
- hidden 30 cap remains;
- fixed 18 rows;
- bridge pins stale game semantics without current authority proof;
- direct PNG roundtrip loses canonical grid identity;
- existing QA/review/handoff bypassed;
- Factor Studio UI claims Solve/Analyze available while backend is not authentic;
- Godot unavailable but Python output accepted;
- production result lacks exact solver replay/load evidence.
