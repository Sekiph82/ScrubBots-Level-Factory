# MAINT-ZIP-CORE-V02-C001 — Level Factory Only — Strict Audit Criteria

Owner authority:
- `docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md`

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## Scope boundary

This audit is ONLY for:
`Sekiph82/ScrubBots-Level-Factory`

The builder must NOT modify:
`Sekiph82/Scrubbots`.

Game-side 3/4/5-column compatibility is a separate Claude task.

If current game-side support is not yet available, Level Factory may still implement and test its own 3/4/5 pipeline contracts using isolated fixtures/mocks, but must truthfully mark cross-repo live verification as pending rather than editing the game repository.

## Canonical owner rules

The owner ZIP is the single production backend for:
- supply planning;
- candidate generation/mutation;
- screening/ranking;
- authentic game solve;
- solver replay/WIN verification;
- supply scoring;
- solution verification;
- official game Difficulty V1;
- export/load verification.

Do not add ProductionGameplayHost as a mandatory acceptance gate.

Preserve:
- candidates=300;
- original + max 3 mutations;
- screening budget=3000;
- viability budget=3000;
- real solver budget = ZIP/game default behavior;
- SupplyScorer weights unchanged;
- mean-batch-size seeds unchanged;
- internal image-complexity/search-band heuristic unchanged;
- no global robots-per-batch cap;
- dynamic FIFO depth.

## Supply columns

Level Factory must support explicit:
- 3 columns;
- 4 columns;
- 5 columns.

Default = 3.

No automatic column-count selection.

Visible preview depth metadata = exactly 3.

All ZIP-derived stages must use the selected count consistently:
- planning;
- candidate generation/mutation;
- screening;
- scoring;
- real-solver request;
- verification;
- export;
- load-check request/evidence.

## Requested difficulty

Remove owner-facing requested difficulty from Level Factory production.

No EASY/MEDIUM/HARD/VERY_HARD target input for:
- artwork generation;
- supply generation;
- canonical request schema;
- Studio;
- CLI;
- presets/new production settings.

Do not substitute a hidden fixed difficulty.

Keep ZIP internal automatic search-band heuristic.

Final actual difficulty comes only after solve from current game Difficulty V1.

## Artwork sources

Both must enter the same canonical product path:
1. Level Factory generated artwork;
2. owner externally uploaded artwork.

Do not use or modify the inspected EXE.

Generated/uploaded artwork must converge at canonical artwork/palette validation before ZIP analysis.

## Background behavior

If background requested during artwork generation:
- background is generated/filled during artwork creation.

If not requested:
- transparency remains.

Do not silently post-fill transparent pixels later.

Transparent artwork may remain an artwork asset; if current shipping LevelData cannot publish it, publish readiness must remain unavailable.

## One production backend

No second competing production solver or difficulty engine may remain active.

Inspect legacy production routes/modules:
- compact_solver_state.py
- legal_move_provider.py
- baseline_search.py
- visited_memoization.py
- solver_evidence.py
- search_policy.py
- solution_analysis.py
- canonical_bridge.py
- solver_budget.py
- simulation_boundary.py
- difficulty_analysis.py
- level_metrics.py
- associated old M03/M04/M05 solver/difficulty routing/tests.

Delete components that exist solely as the retired production backend.

If retained for non-competing historical/evidence contracts:
- document exact reason;
- prove production ZIP path cannot call them as solver/difficulty authority.

## Product flow

Default production flow:

```
GENERATE ARTWORK or IMPORT ARTWORK
 -> canonical validation
 -> ZIP pipeline
 -> ScreeningSimulator ranking only
 -> real Scrubbots SolvabilitySolver.solve
 -> real Scrubbots SolvabilitySolver.replay
 -> ZIP SolutionVerifier
 -> official game Difficulty V1
 -> ZIP SupplyExporter/load-check
 -> owner review
 -> automatic publish
 -> deterministic difficulty-based progression placement
```

Image-path diagnostic helper may remain but cannot be the only ZIP route.

Canonical candidate/logical-grid bundles must enter ZIP path directly without unnecessary PNG roundtrip.

## Owner review and publish

Owner ACCEPT triggers automatic publish.
Owner REJECT never publishes.

No second Publish confirmation/button required.

Publishing must fail closed on:
- transparent non-publishable artwork;
- malformed export;
- load-check failure;
- game path/schema conflict;
- duplicate immutable identity;
- unsafe progression update.

Tests must never publish into live game data.

## Progression

Progression placement happens only after official Difficulty V1/Challenge Score.

Requirements:
- deterministic ordering;
- stable immutable internal level ID;
- documented deterministic tie-break;
- no destructive renaming of existing immutable levels.

## Validation

Required Level Factory evidence:
- ZIP parameter-lock tests;
- 3-column pipeline;
- 4-column pipeline;
- 5-column pipeline;
- preview metadata exactly 3;
- no global robot cap;
- no requested difficulty on product surfaces;
- generated artwork -> same ZIP path;
- external upload -> same ZIP path;
- background requested -> full canvas;
- no background -> transparency preserved;
- baseline five-slot generation only;
- owner ACCEPT -> isolated auto-publish;
- REJECT -> no publish;
- official Difficulty V1 -> progression placement;
- no legacy production solver/difficulty path;
- full pytest;
- compileall;
- Factory Studio headless;
- diff check.

Cross-repo live 4/5-column game verification may be PENDING only until the separately authorized Claude game task lands. It must not trigger writes to the game repo from this task.
