# OWNER_PRIMARY_SUPPLY_PIPELINE_V01

Status: OWNER APPROVED
Date: 2026-10-01

## Owner decision

The ZIP package supplied by the owner on 2026-10-01 becomes the primary Level Factory supply/solve/difficulty pipeline foundation.

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

The source package contains:
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
- `tests/test_supply_pipeline.py`
- `PORT_PROMPT_screening_simulator.md`
- `README.md`

## Canonical repository roles

Game authority:
`https://github.com/Sekiph82/Scrubbots`

Level production application:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

All production implementation of this ZIP belongs in the Level Factory repository, except narrowly required game-side contract corrections.

## Primary architecture

The product pipeline is:

```
canonical artwork / logical grid
 -> PixelAnalyzer
 -> DifficultyModel generation seed/band
 -> BatchPlanner
 -> SupplyCandidateGenerator
 -> ScreeningSimulator
 -> SupplyScorer
 -> ScrubBotsSolver / Godot bridge
 -> GAME SolvabilitySolver.solve
 -> GAME SolvabilitySolver.replay
 -> production-runtime replay gate
 -> GAME LevelDifficultyAnalyzerV1
 -> SolutionVerifier
 -> SupplyExporter
 -> game LevelLoader + SupplyPlanLoader load check
```

## Trust boundary

The Python `ScreeningSimulator` is ranking/screening only.

It must never become acceptance authority.

A candidate is production-acceptable only after authentic current-game evidence from `Sekiph82/Scrubbots` proves:
1. `SolvabilitySolver.solve == SOLVED`;
2. solver trace replays to exact completion;
3. final ACTIVE count is zero, supply is exhausted, and slots are empty;
4. the accepted click sequence is valid through the production runtime/headless gameplay seam;
5. official `LevelDifficultyAnalyzerV1` produces the Difficulty V1 result;
6. hard conservation/FIFO invariants pass;
7. exported LevelData and supply plan load through the game's shipping loaders.

If game authority is unavailable or incompatible, production acceptance is UNAVAILABLE, never inferred from Python screening.

## Difficulty

The ZIP pipeline becomes the main Level Factory path for supply generation, solve orchestration and difficulty scoring.

Final production difficulty score/class must come from the current game's official `LevelDifficultyAnalyzerV1` reached through the ZIP's bridge architecture.

Image complexity and SupplyScorer scores remain search/ranking/tuning inputs, not production difficulty authority.

## Robot-count owner rule

The old global `MAX_ROBOTS_PER_BATCH = 30` cap is stale and no longer owner-approved.

Canonical owner rule:
- every batch must contain a positive integer robot count;
- there is no fixed global maximum robot count per batch;
- exact per-color and grand-total conservation remain mandatory;
- a supply plan may record its actual maximum batch size as metadata, but that value is not a global gameplay cap.

The Scrubbots shipping `SupplyPlanLoader` must be updated accordingly before >30 plans can be considered loadable production output.

## Dynamic supply depth

Supply rows are dynamic and derived from artwork/pixel workload and the optimizer. There is no fixed 18-row contract.

Three FIFO columns remain the current shipping supply-column contract unless a separate owner decision changes it.

## Integration principles

- Port/adapt the supplied algorithms rather than re-inventing a different supply optimizer.
- Preserve current Level Factory provenance, QA, owner-review and output contracts around the new core.
- Do not keep a second competing product solve/supply/difficulty path.
- Historical M03/M04/M05 components may remain for evidence/regression/adapter purposes, but the default production orchestration must use this primary pipeline and authentic game authority.
- Add NumPy/Pillow deliberately as local offline dependencies if required by the port.
- No cloud/runtime API dependency.
- No silent quantization of off-palette artwork.
- Full-canvas LevelData remains required for production export under the current game contract.
- Determinism/provenance must include source artwork/grid identity, optimizer settings, seed, game authority SHA and bridge version.

## Required differential evidence

At minimum:
- screening trace vs real game trace on `level_004_orange_cat`;
- screening solution replay through real game on `level_008_butterfly`;
- deliberate unsolvable supply is rejected by real game;
- 20x20 end-to-end proof;
- 37x37 end-to-end proof;
- 59x59 end-to-end proof;
- a valid plan containing a batch >30 proves the uncapped loader path;
- same seed/settings reproduce the same supply and evidence;
- no fixed-18-row behavior;
- exported level + supply plan load through shipping loaders.

## Source review completed by ChatGPT

Static source review found no network/API client, `shell=True`, repository deletion/reset/clean logic, or hidden game-repo writes. The only external process path is local Godot headless execution.

Independent local static/core checks performed on the supplied ZIP:
- Python compileall: PASS.
- BatchPlanner conservation/bounds: PASS across 1500 generated cases.
- SupplyCandidateGenerator conservation across 500 candidates + mutations: PASS.
- Screening trivial solve: PASS.
- Screening deliberate deadlock: PASS.
- SolutionVerifier synthetic invariant case: PASS.

The package's official Godot/game integration claims were not independently re-run in the ChatGPT container because the canonical Scrubbots checkout/Godot runtime is not present there. They must be reproduced by the builder on the owner's machine before acceptance.
