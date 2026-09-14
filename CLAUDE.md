# SCRUBBOTS Content Production Platform — Builder Operating Rules

## Repository identity

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

This repository is the canonical SCRUBBOTS Content Production Platform.

## Current authority

Read before material work:

1. root `TASKS.md` — sole live 224-task Content Platform tracker;
2. `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`;
3. `GOVERNANCE.md`;
4. `docs/CONTENT_PLATFORM_ARCHITECTURE_V01.md`;
5. `docs/CROSS_REPO_CONTRACT_V01.md`;
6. active prompt / audit criteria;
7. relevant historical PAG/SP evidence only as needed.

Historical `.hiveai` state files are evidence/history, not a competing current tracker.

## Role boundary

ChatGPT is independent auditor and tracker owner.

Codex/Claude implement and test only the active prompt scope.

Builders must not:

- self-award canonical task completion;
- edit root `TASKS.md` checkbox/acceptance/current-state fields;
- author independent audit verdicts/files;
- rewrite used historical prompts/logs/audits;
- hide failed commands/tests;
- modify `Sekiph82/Scrubbots` unless the active task explicitly declares a `GAME_RUNTIME` or `CROSS_REPO` write scope.

## Cross-repo rule

The Content Platform tracker may contain tasks implemented in the main game repository.

When a task says `GAME_RUNTIME`, implementation belongs in `Sekiph82/Scrubbots`; do not place shipping runtime code in this repository merely because the task is tracked here.

When a task says `FACTORY`, do not modify the game repository.

When a task says `CROSS_REPO`, follow the exact prompt boundaries for each repository.

## Contract precedence

Newest explicit owner decisions in `Sekiph82/Scrubbots` govern gameplay, LevelData, palette, Difficulty V1, campaign and runtime semantics.

Do not extend stale historical Factory assumptions that equate difficulty class with board dimensions or fixed color-count bands.

Current general production rules include:

- rectangular boards supported;
- engine/content envelope currently 20..59 per dimension;
- C01..C16 logical palette;
- general production used-color envelope 3..12;
- board size/color count are difficulty inputs, not class identity;
- Challenge, Session Load and Frustration Risk are separate.

## LEVEL_ART semantic reduction

Current owner direction:

`SEMANTIC IMAGE -> CELL_MAJORITY -> PALETTE SNAP -> ONE LOGICAL PIXEL = ONE GAMEPLAY CELL -> C01..C16 -> CURRENT DIFFICULTY/QA EVALUATION -> VALIDATION/EXPORT`

`AREA_AVERAGE_V1` is not canonical LEVEL_ART reduction.

## Factory Core / Studio boundary

Factory Core owns compilation, validation, solver, difficulty, QA, campaign and packaging truth.

Studio is an operator layer and may not keep an independent second compiler truth.

Allowed dependency: `Studio -> Factory Core`.

## Remote-content safety

Remote content is declarative only. Never publish or design runtime execution of arbitrary scripts/native code/plugins through content packages.

No secrets in Git.

## Tracker workflow

- Builders read root `TASKS.md` but do not edit it.
- Builders implement/test/log/commit/push only active scope.
- Builders return `AWAITING_AUDIT` when requested.
- ChatGPT independently audits actual GitHub state and updates root `TASKS.md`.

## Historical PAG/SP cycles

Existing `.hiveai` prompts/logs/audits and review packs remain immutable evidence.

A historical PASS may be proposed as evidence for a new `SB-LF*`/`SB-CP*` task, but only ChatGPT may map it into canonical task closure after checking the current task contract.
