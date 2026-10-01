# MAINT-ZIP-CORE-V02-C001 — Canonical ZIP Core Cutover — Strict Audit Criteria

Owner authority:
- `docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md`
- game: `Sekiph82/Scrubbots/coordination/OWNER_SUPPLY_COLUMNS_3_4_5_PREVIEW3_V01.md`
- game uncapped count decision remains in force.

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## Supersession

This V02 criteria supersedes the prior R01 criteria.

Do NOT require a ProductionGameplayHost runtime-WON gate.

The canonical owner ZIP acceptance remains:
- ScreeningSimulator = ranking only;
- real game SolvabilitySolver.solve;
- real game SolvabilitySolver.replay;
- ZIP SolutionVerifier;
- official Difficulty V1.

## PASS rule

PASS only if the Level Factory has one production supply/solve/difficulty backend: the owner ZIP-derived pipeline, with only the explicitly approved owner changes below.

## A. ZIP algorithm fidelity

Preserve unchanged:
- default candidates = 300;
- original candidate + max 3 mutations;
- screening budget = 3000;
- viability budget = 3000;
- real solver budget behavior = game/ZIP default;
- SupplyScorer weights;
- mean batch-size seeds;
- internal automatic image-complexity/search-band heuristic;
- screening as ranking only;
- real game solve/replay acceptance;
- SolutionVerifier invariants;
- official Difficulty V1 final measurement;
- no global robots-per-batch cap;
- dynamic supply depth.

Fail if these are silently retuned.

## B. 3/4/5 supply columns, 3 preview rows

Game:
- `BatchSupplyEngine` 3..5 support preserved;
- `BatchSupplyPanel` 3..5 support preserved;
- `SupplyPlanLoader` accepts exactly 3, 4, or 5 declared columns;
- plan array length must equal declared count;
- engine creation uses declared validated count;
- visiblePreviewDepth must equal exactly 3;
- existing 3-column plans remain byte-compatible.

Factory/ZIP:
- explicit column_count accepts only 3/4/5;
- default = 3;
- no automatic column selection;
- planner/generator/screening/scorer/solver/export/verify all use the selected count;
- no hardcoded 3-column conservation/verifier assumptions remain;
- output metadata accurately records column count.

## C. Booster boundary

Canonical generation/solve/difficulty uses baseline five slots.

+1 Slot booster must not be applied during:
- generation;
- screening;
- real solver acceptance;
- difficulty measurement.

## D. Requested difficulty removed from Level Factory

No owner-facing requested difficulty for:
- artwork generation;
- supply generation;
- presets;
- Studio controls;
- CLI;
- canonical request schemas.

Remove target-difficulty override from the production ZIP call.

The ZIP internal automatic image-complexity/search band remains.

Final difficulty is post-solve current-game Difficulty V1.

No hidden substitution such as forcing MEDIUM internally as a user-request proxy.

## E. Artwork generation + external upload

Level Factory supports both:
- generated artwork;
- owner-uploaded artwork.

Both converge to the same canonical artwork/palette validation boundary before ZIP analysis.

External upload is implemented using the Level Factory's own product architecture, not the inspected EXE.

The inspected EXE is out of scope and unchanged.

## F. Background/transparency

Artwork generation has an explicit owner background choice:
- background requested => background generated/filled during artwork generation, producing intended full-canvas artwork;
- background not requested => transparency remains transparency.

No later silent background fill.

Transparent artwork may exist as an asset, but if current shipping LevelData cannot publish transparent cells, publish must truthfully remain unavailable for that artifact.

## G. Single production backend

Active production flow must not use a second Factory solver or second Factory difficulty authority.

At minimum audit all active imports/routes for:
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

If a module exists only to implement the retired competing production solver/difficulty backend:
- delete it and its dedicated tests.

If a piece is retained because another non-competing feature requires it:
- document the exact retained role;
- prove no production supply/solve/difficulty route calls it;
- rename/deprecate misleading active authority claims where necessary.

No M03/M04 "pending" or legacy solver/difficulty path may intercept production.

## H. Factory Studio / CLI

The default production level flow is:

GENERATE or IMPORT ARTWORK
-> canonical validation
-> ZIP primary pipeline
-> real game solve/replay
-> official Difficulty V1
-> ZIP export/load verification
-> owner review
-> automatic publish
-> progression placement.

Studio and CLI must expose the same backend.

No detached "Primary Supply" side-route that leaves the old canonical candidate flow unchanged.

## I. Owner review + automatic publish

Owner ACCEPT is the human approval boundary.

After ACCEPT:
- publish automatically;
- no second Publish button/approval step.

Publish must fail closed on:
- transparent non-publishable artwork;
- malformed/failed export;
- game path/schema conflict;
- duplicate immutable level identity;
- inability to safely update progression.

Tests must use isolated fixtures/temp copies and must not accidentally publish test levels into the live game repo.

## J. Difficulty-based progression placement

Final progression position is decided only after official Difficulty V1/Challenge Score exists.

Requirements:
- deterministic ordering;
- documented tie-break;
- stable immutable internal level identity independent of displayed progression number/order;
- no destructive renaming of prior immutable IDs merely because a new level is inserted;
- publish updates the game's canonical progression/catalog through the current accepted game data contract.

No requested difficulty participates.

## K. Export/load

Preserve ZIP `SupplyExporter` and `load_check.gd` role.

Load check is file compatibility validation, not a new gameplay acceptance authority.

Exact emitted level/supply must load through current game loaders before publish.

## L. Evidence

Required authentic cases:
- existing 3-column reference case;
- valid 4-column solved/replay/export/load case;
- valid 5-column solved/replay/export/load case;
- preview depth other than 3 rejected;
- >30 batch remains accepted under uncapped contract;
- conservation exact for 3/4/5;
- same seed/settings/column count deterministic;
- +1 Slot not used in generation authority;
- requested difficulty absent from public product surfaces;
- generated artwork enters ZIP path;
- external artwork upload enters same ZIP path;
- background requested full-canvas path;
- background-not-requested transparency-preserved path;
- official Difficulty V1 determines progression placement;
- owner ACCEPT triggers automatic publish in isolated integration fixture;
- owner REJECT does not publish.

## M. Regression

- all adapted ZIP tests pass, updated only where owner-approved column support requires parameterization;
- full Factory pytest green except truthful capability skips;
- Factory Studio headless suite green;
- relevant Scrubbots M23/M24/M27/M28/M29/M52 solver/supply/UI tests green;
- compileall green;
- git diff --check green;
- no extra Desktop clone/worktree;
- builders do not edit root TASKS or ChatGPT audits.
