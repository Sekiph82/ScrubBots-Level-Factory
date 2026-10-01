# MAINT-ZIP-CORE-V02-C001 — LEVEL FACTORY ONLY — Canonical ZIP Core Cutover

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Owner authority:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-LF_ONLY_AUDIT_CRITERIA.md

Source ZIP SHA-256:
`c76e195bc1af211b3f4702fc21d00dd4ea509041f3a6db97a2d6b1009b619284`

## CRITICAL SCOPE

You may modify ONLY:
`Sekiph82/ScrubBots-Level-Factory`.

Do NOT modify:
`Sekiph82/Scrubbots`.

Do NOT create a second checkout, sibling clone or worktree of the game repo.

Game-side 3/4/5-column compatibility is being handled separately by Claude.

You may read current game source/contracts if an already-authorized local checkout is available, but absence of that checkout is NOT a blocker for implementing the Level Factory side. Truthfully mark cross-repo live verification pending where necessary.

The inspected EXE is out of scope. Do not modify, copy, port, decompile, or depend on it.

The old cross-repository prompt:
`.hiveai/prompts/MAINT-ZIP-CORE-V02-C001_CANONICAL_CUTOVER_MASTER_PROMPT.md`
is SUPERSEDED. Do not execute its game-repository work package.

## Mandatory local ↔ GitHub sync preflight

Before edits:

1. Work only in:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repo = `Sekiph82/ScrubBots-Level-Factory`.
3. Verify branch = `main`.
4. `git fetch origin --prune`.
5. Inspect local HEAD, origin/main, status, stashes, worktrees, ahead/behind.
6. Clean+behind => `git merge --ff-only origin/main`.
7. Preserve legitimate local work non-destructively.
8. Never reset, rebase, stash, clean, force checkout, force push, or discard owner work.
9. Never create a new branch or sibling Desktop clone/worktree.
10. Start product work only after safe synchronization.

## Objective

Make the owner ZIP the SINGLE production backend inside ScrubBots Level Factory for:
- supply generation;
- screening/ranking;
- solve;
- replay/WIN verification;
- difficulty;
- verification;
- export/load-check.

Do not add behavior not authorized by owner.

## Locked ZIP behavior

Do not change:
- default candidates = 300;
- one original + max three mutations;
- screening budget = 3000;
- viability budget = 3000;
- real solver budget behavior = ZIP/game default;
- SupplyScorer weights;
- mean-batch-size seed ranges;
- internal automatic image-complexity/search-band heuristic;
- ScreeningSimulator ranking-only role;
- real game SolvabilitySolver.solve authority;
- real game SolvabilitySolver.replay/WIN verification;
- ZIP SolutionVerifier;
- official game Difficulty V1;
- dynamic supply depth;
- uncapped robots-per-batch.

Do NOT add mandatory ProductionGameplayHost/runtime-WON acceptance.

## 1 — Supply columns

Add explicit product `column_count`:
- allowed: 3, 4, 5;
- default: 3;
- no automatic chooser.

Visible preview depth remains exactly 3.

Generalize all ZIP-derived Level Factory stages that still assume 3:
- DifficultyModel row math;
- BatchPlanner orchestration;
- SupplyCandidateGenerator;
- ScreeningSimulator where count-dependent;
- SupplyScorer where count-dependent;
- SolutionVerifier;
- ScrubBotsSolver request;
- Godot bridge payload;
- SupplyExporter;
- verify/load request/evidence;
- CLI;
- Studio;
- tests.

Do not change hidden FIFO depth semantics.

If live game 4/5 support is not yet installed, Level Factory must still generate correct 4/5 artifacts and mark live game verification pending. Do not edit game repo.

## 2 — Remove requested difficulty

This applies to Level Factory only.

Remove user-facing requested difficulty from:
- artwork generation;
- canonical generation request;
- supply generation;
- CLI;
- Studio;
- presets/new production settings;
- ZIP target override.

No EASY/MEDIUM/HARD/VERY_HARD generation request.

Do not replace it with hidden MEDIUM.

Keep ZIP's internal automatic complexity/search-band heuristic.

Actual difficulty is measured after solve by official game Difficulty V1.

Historical records may retain old requested-difficulty fields only as inert provenance.

## 3 — Artwork generation + external artwork upload

Level Factory must support:
- generated artwork;
- owner external image/artwork upload.

Both enter the SAME canonical artwork/palette validation pipeline and then the SAME ZIP backend.

Do not make external upload a separate solver path.

Use existing Level Factory import architecture; do not use the inspected EXE.

## 4 — Background/transparency

Expose/preserve artwork background intent.

If background requested:
- generate/fill during artwork creation.

If not requested:
- preserve transparency.

Never silently fill transparency downstream just to make a publishable level.

If current game contract cannot publish transparent cells:
- keep the artwork;
- publish readiness = unavailable;
- do not alter the artwork.

## 5 — ZIP becomes the only production solver/difficulty backend

Remove/decommission the competing production path.

Dependency-scan:
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
- old M03/M04/M05 solver/difficulty wiring/tests.

If a module is solely the retired alternative backend:
DELETE it and update imports/tests/docs.

If something must remain for non-competing historical/evidence use:
- retain only minimal needed contract;
- document why;
- prove product ZIP route cannot call it as solver/difficulty authority.

Remove stale product messages such as:
- solver pending M03;
- difficulty pending M04.

Do not keep two brains.

## 6 — Canonical product flow

Make normal Studio/CLI production flow:

```
GENERATE ARTWORK or IMPORT ARTWORK
 -> canonical validation
 -> ZIP PixelAnalyzer
 -> internal ZIP search band
 -> ZIP BatchPlanner
 -> ZIP SupplyCandidateGenerator
 -> ZIP ScreeningSimulator
 -> ZIP SupplyScorer
 -> real game solve
 -> real game replay/WIN
 -> ZIP SolutionVerifier
 -> official Difficulty V1
 -> ZIP export/load-check
 -> owner review
 -> automatic publish
 -> progression placement
```

Canonical candidate/logical-grid bundles must enter ZIP directly without unnecessary PNG encode/decode.

An image-path diagnostic helper may remain, but cannot be the canonical product route.

## 7 — Gateway/CLI/Studio

FactoryCoreGateway, CLI and Studio must all point to the same ZIP backend.

When game/Godot bridge capability exists:
- Solve available;
- Analyze available.

When it does not:
- truthful unavailable/pending live-game verification.

Absence of local game checkout must not cause this task to stop before implementing LF-side code.

## 8 — Owner ACCEPT => automatic publish

After ZIP output is solver/replay verified, official difficulty exists, export/load compatibility passes, and owner review = ACCEPT:
- publish automatically.

No second Publish button/approval.

Owner REJECT => no publish.

Tests must use isolated fixture/temp destinations only.

## 9 — Difficulty-based progression placement

After official Difficulty V1/Challenge Score:
- compute deterministic progression position;
- use stable immutable internal level identity;
- document deterministic tie-break;
- do not destructively rename existing immutable levels.

Requested difficulty plays no role.

## 10 — Tests

Add/update tests proving:
- candidates=300 unchanged;
- max three mutations unchanged;
- screening=3000 unchanged;
- viability=3000 unchanged;
- scorer weights unchanged;
- mean seeds unchanged;
- 3/4/5 column LF artifacts;
- default column_count=3;
- preview depth=3;
- requested difficulty absent from current product surfaces;
- generated artwork and external upload converge to same ZIP route;
- background intent behavior;
- transparent artwork preserved;
- baseline five-slot generation;
- owner ACCEPT auto-publish in isolated fixture;
- owner REJECT no publish;
- difficulty-based progression placement;
- no active alternate production solver/difficulty route;
- full pytest;
- compileall;
- Studio headless;
- diff check.

Do not weaken tests merely to accommodate deleted legacy production code. Replace obsolete tests with tests for the canonical ZIP backend.

## Builder governance

Do not edit:
- root `TASKS.md`;
- `.hiveai/audits/**`.

Create before product edits:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CODEX_LOG.md`

Commit implementation separately from final log publication.

Push only Level Factory `main`.

Final:
- local HEAD == origin/main;
- divergence 0/0.

STOP for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CODEX_LOG.md
