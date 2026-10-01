# MAINT-ZIP-CORE-V02-C001 — Canonical ZIP Core Cutover

Document role: CROSS-REPOSITORY CODEX MASTER IMPLEMENTATION PROMPT

Level Factory:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Game:
https://github.com/Sekiph82/Scrubbots

Owner V02:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md

Game 3/4/5-column decision:
https://github.com/Sekiph82/Scrubbots/blob/main/coordination/OWNER_SUPPLY_COLUMNS_3_4_5_PREVIEW3_V01.md

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001_CANONICAL_CUTOVER_AUDIT_CRITERIA.md

Source ZIP identity:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## Superseded instructions

Do NOT execute the old:
`MAINT-SUPPLY-PIPELINE-V01-R01_STRICT_CLOSURE_REMEDIATION_PROMPT.md`.

Specifically DO NOT add a mandatory ProductionGameplayHost/runtime-WON acceptance gate.

The later EXE supplied to ChatGPT was inspection-only and is OUT OF SCOPE.
Do not modify, port, copy, decompile, or depend on that EXE.

## Mandatory local ↔ GitHub sync preflight

Perform this separately before edits in EACH repository.

1. Verify exact repo identity and canonical local root.
2. Verify branch `main`.
3. `git fetch origin --prune`.
4. Record HEAD, origin/main, status, ahead/behind, stashes, worktrees.
5. Clean + behind => `git merge --ff-only origin/main`.
6. Preserve legitimate local changes non-destructively.
7. Never reset, rebase, stash, clean, force checkout, force push, or discard owner work.
8. Never create a new branch or Desktop sibling clone/worktree.
9. Begin edits only after safe reconciliation.
10. If safe sync is impossible, stop before product changes.

---

# WP1 — Scrubbots game: 3/4/5 columns, preview 3

Repository:
`Sekiph82/Scrubbots`

Do not redesign the engine.

Current foundations already support:
- BatchSupplyEngine 3..5 columns;
- BatchSupplyPanel 3..5 columns;
- BatchSupplyPanel exactly 3 visible rows.

Implement the owner decision narrowly.

## WP1.1 SupplyPlanLoader

Replace fixed:
`COLUMN_COUNT := 3`

with a validated 3..5 column plan contract.

Requirements:
- declared `columnCount` exact integer in 3..5;
- `visiblePreviewDepth == 3` exactly;
- `columns.size() == declared columnCount`;
- `BatchSupplyEngine.create(declared_column_count, 3)`;
- all current conservation/palette/batch-ID/per-plan bound validation retained;
- no global robot cap;
- existing 3-column plans unchanged.

## WP1.2 Scan remaining game fixed-three assumptions

Audit runtime, input, solver, UI, tests and tools for fixed-three assumptions.

Change only assumptions that prevent an actual 4/5-column shipping plan.

Do not modify semantics that are already dynamic.

Keep baseline generation/solver slot capacity five.
Do not activate +1 Slot for canonical level solve/difficulty.

## WP1.3 Game evidence

Add/retain tests proving:
- legacy 3-column plans pass;
- valid 4-column plan passes loader + real solve/replay;
- valid 5-column plan passes loader + real solve/replay;
- 2 or 6 columns rejected;
- preview 2/4 rejected; preview 3 accepted;
- >30 batch still accepted;
- panel renders 3/4/5 columns and exactly 3 rows;
- canonical solver reasons over the selected column count;
- +1 Slot not required for these accepted fixtures.

Commit/push game main, verify 0/0, then continue.

---

# WP2 — Level Factory: ZIP becomes the system

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Preserve the existing ZIP-derived port as the algorithmic source.

Do not invent an alternate optimizer.

## WP2.1 Lock ZIP algorithm parameters

Do not change:
- candidates=300;
- original + max 3 mutations;
- screening budget=3000;
- viability budget=3000;
- real solver budget default behavior;
- SupplyScorer weights;
- mean-batch seeds;
- internal automatic image-complexity/search-band heuristic.

Screening remains ranking only.

Acceptance remains:
`SolvabilitySolver.solve -> SolvabilitySolver.replay -> SolutionVerifier`.

Final production difficulty remains current game Difficulty V1.

No ProductionGameplayHost acceptance gate.

## WP2.2 3/4/5 supply columns

Add explicit `column_count` to the ZIP-derived product route:
- allowed only 3,4,5;
- default 3;
- no automatic selection.

Generalize every ZIP-derived stage currently assuming 3:
- DifficultyModel plan row math;
- BatchPlanner orchestration;
- SupplyCandidateGenerator;
- ScreeningSimulator where relevant;
- SupplyScorer where relevant;
- SolutionVerifier;
- ScrubBotsSolver request/bridge;
- SupplyExporter;
- verify/load route;
- tests/UI/CLI.

Visible preview depth remains exactly 3.

Do not alter hidden FIFO depth behavior.

## WP2.3 Remove requested difficulty from Level Factory

This applies to ScrubBots Level Factory, NOT the inspected EXE.

Remove owner-facing requested difficulty from:
- artwork generation controls;
- canonical generation request;
- CLI;
- presets;
- Studio target controls where they represent requested level difficulty;
- ZIP supply invocation target override.

There must be no user choice EASY/MEDIUM/HARD/VERY_HARD for creating artwork or supply.

Do not secretly map the missing field to MEDIUM.

Keep the ZIP's INTERNAL automatic complexity/search-band heuristic.

After solve, official Difficulty V1 computes actual difficulty.

Migrate persisted presets/records truthfully:
- old requested-difficulty metadata may remain as historical data;
- it must not drive new production generation.

## WP2.4 Artwork sources

The Level Factory artwork stage supports:
1. its existing artwork generators;
2. owner external artwork upload/import.

Both must converge into the same canonical palette/artwork validation and then the same ZIP primary pipeline.

Do not use the inspected EXE.

Do not create a separate solve path for uploads.

## WP2.5 Background/alpha behavior

Add/retain explicit artwork background intent.

When background requested:
- fill/generate it during ARTWORK creation;
- canonical result is intended full canvas.

When background not requested:
- preserve transparency;
- never post-fill merely to make the game accept it.

If transparent artwork cannot become current shipping LevelData:
- keep it as artwork;
- mark publish unavailable;
- do not mutate it silently.

## WP2.6 Remove competing production solver/difficulty backend

The ZIP-derived pipeline must be the only production supply/solve/difficulty route.

Dependency-scan these legacy modules and their dedicated tests:
- `compact_solver_state.py`
- `legal_move_provider.py`
- `baseline_search.py`
- `visited_memoization.py`
- `solver_evidence.py`
- `search_policy.py`
- `solution_analysis.py`
- `canonical_bridge.py`
- `solver_budget.py`
- `simulation_boundary.py`
- `difficulty_analysis.py`
- `level_metrics.py`
- legacy solver/difficulty-specific M03/M04 tests and stale M05 solver gate wiring.

If a file is solely the retired alternative production backend:
DELETE it and update imports/tests/docs.

If a sub-contract must remain for a non-competing feature:
- retain only the minimal needed piece;
- document why;
- prove the production pipeline cannot call it as solver/difficulty authority.

Remove active stale UI/messages such as:
- `solver pending M03`;
- `difficulty pending M04`;
where the ZIP/current game bridge is available.

Do not keep two brains.

## WP2.7 Canonical Studio flow

The normal production flow must be one path:

```
GENERATE ARTWORK or IMPORT ARTWORK
 -> canonical validation
 -> ZIP primary supply pipeline
 -> real game solve/replay
 -> ZIP SolutionVerifier
 -> official Difficulty V1
 -> ZIP export/load-check
 -> owner review
 -> automatic publish
 -> progression placement
```

The current image-only `Run Primary Supply` side route may be retained as a diagnostic helper, but it must not be the only ZIP path.

Existing canonical candidate/bundle IDs must enter the ZIP pipeline directly without lossy PNG round-trip when exact logical cells already exist.

## WP2.8 Gateway/CLI capability truth

FactoryCoreGateway and CLI must report Solve/Analyze availability from actual local capability:
- current game checkout;
- Godot;
- ZIP bridge.

No stale M03/M04 pending status.

## WP2.9 Owner review => automatic publish

Owner ACCEPT triggers publish automatically.

Do not add a second Publish approval button.

Implementation must:
- publish exact solver-proven exported level/supply;
- fail closed on path/schema/conflict/load errors;
- never auto-publish owner REJECT;
- never publish transparent non-game-compatible artwork by silently filling it.

Tests must publish only into isolated fixture/temp game copies.

## WP2.10 Difficulty-based progression placement

After official Difficulty V1 is known:
- determine progression position from Challenge Score/difficulty;
- use deterministic ordering/tie-break;
- preserve immutable internal level identity independent of displayed progression position;
- update the current accepted game progression/catalog data contract during publish.

Do not use requested difficulty.

Do not destructively rename existing immutable levels merely because a new level inserts before them.

Document the tie-break in code/docs and test it.

## WP2.11 ZIP load_check

Keep ZIP/game `load_check.gd` as export compatibility validation.

Do not reinterpret it as a new solver authority.

Before publish, exact emitted level/supply must load through current game loaders.

---

# WP3 — Product cleanup

Remove stale product UI/settings/docs/tests that imply:
- old Factory solver is canonical;
- old Factory difficulty analyzer is canonical;
- requested difficulty is an owner input;
- supply is always three columns;
- M03/M04 are pending production capabilities.

Preserve historical Git/audit artifacts. Do not rewrite history.

Root `TASKS.md` remains ChatGPT-owned.

Do not edit `.hiveai/audits/**`.

---

# Required validation

## Game
- 3-column legacy regression
- 4-column real solve/replay
- 5-column real solve/replay
- preview exactly 3
- >30 robot batch
- relevant M23/M24/M27/M28/M29/M52
- full game gate

## Level Factory
- all owner ZIP tests, parameterized only as needed for 3/4/5
- 3-column, 4-column, 5-column complete ZIP pipelines
- 300 candidate default contract
- max 3 mutations contract
- screening/viability 3000 contract
- scorer weights unchanged
- mean seeds unchanged
- no requested-difficulty public field
- generated artwork -> ZIP
- uploaded artwork -> same ZIP
- background requested -> full-canvas generation path
- no background -> transparency preserved
- baseline five-slot authority
- owner ACCEPT -> isolated automatic publish
- REJECT -> no publish
- official Difficulty V1 -> deterministic progression placement
- no legacy production solver/difficulty route
- full pytest
- compileall
- Studio headless
- diff check

No network/provider credits merely for tests.

---

# Builder logs

Game:
`coordination/sessions/MAINT-ZIP-CORE-V02-C001/MAINT-ZIP-CORE-V02-C001_GAME_CODEX_LOG.md`

Level Factory:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001_LEVEL_FACTORY_CODEX_LOG.md`

Master:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001_MASTER_CODEX_LOG.md`

Create logs before corresponding edits.

Commit product code separately from terminal log publication.

Push both `main` branches normally.

Final proof:
- both local HEAD == origin/main;
- both divergence 0/0.

Stop for independent ChatGPT audit.

## Final response

Return only the three full GitHub log URLs.
