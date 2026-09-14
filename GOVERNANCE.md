# SCRUBBOTS Content Production Platform Governance

## Purpose

This repository is the canonical development-time Content Production Platform for SCRUBBOTS. It uses evidence-first development with strict separation between builder and independent auditor.

Canonical repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Canonical live tracker:

`TASKS.md`

Canonical consolidation decision:

`coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`

## Program scope

The repository tracks all 224 canonical sidecar tasks:

- `SB-LF00-* .. SB-LF10-*` — Level Factory / Puzzle / Difficulty / Campaign / Studio.
- `SB-CP00-* .. SB-CP09-*` — Packaging / Publishing / Remote Content / Operations.

Not every tracked task is implemented in this repository. Runtime milestones such as CP04 and CP05 are implemented primarily in `Sekiph82/Scrubbots` and require cross-repo evidence to close.

## Roles

### ChatGPT — planner, tracker owner, independent auditor

ChatGPT owns:

- canonical task-state updates in root `TASKS.md`;
- implementation/remediation prompt authoring;
- independent strict audits;
- acceptance/rejection decisions;
- migration/evidence mapping;
- cross-repo closure decisions;
- milestone/cycle closure;
- final determination of whether work advances.

### Codex / Claude — builders only

Builders own:

- implementation authorized by the active prompt;
- builder-side tests and verification;
- chronological implementation logs;
- authorized commits/pushes.

Builders do **not** independently audit or self-close canonical tasks.

They must not:

- declare final `AUDITED_PASS` or canonical task closure;
- change root `TASKS.md` checkbox/acceptance/current-state fields unless an explicit owner-approved governance prompt changes this rule;
- author independent audit files;
- rewrite historical prompt/log/audit evidence;
- hide failed tests/commands after correction;
- opportunistically write to the other repository outside explicit cross-repo scope.

## GitHub authority

GitHub `main` is repository truth. Local folders are execution workspaces only.

Current known local mirror may be `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, but local naming does not define project identity.

Do not discover work by searching sibling folders. Every implementation handoff must identify the repository explicitly.

## Tracker authority

Root `TASKS.md` is the sole live tracker for the 224 Content Platform tasks.

Historical PAG/SP trackers, `.hiveai` machine files, cycle indexes, prompts, logs and audits remain immutable evidence/history only. They may be read for migration evidence but do not compete with root `TASKS.md` for current state.

The corresponding LF/CP rows in the main-game `Scrubbots/TASKS.md` are shadow/historical roadmap entries after the 2026-09-14 consolidation decision. They must not be independently advanced there.

## Cross-repo implementation ownership

Task ownership metadata uses:

- `FACTORY` — implement in `ScrubBots-Level-Factory`.
- `GAME_RUNTIME` — implement primarily in `Scrubbots`.
- `CROSS_REPO` — coordinated producer/consumer work required.
- `OWNER_DECISION` — owner choice/gate required.

A `GAME_RUNTIME` task is still closed by ChatGPT in this repository's canonical 224-task tracker after inspecting both repositories.

## Contract precedence

When contracts conflict:

1. newest explicit owner instruction;
2. newest owner-locked decision in either canonical repository;
3. current `TASKS.md` state for active work;
4. versioned machine configs/schemas for exact model values;
5. current subsystem docs;
6. historical PAG/SP docs/audits as evidence only.

Current main-game Difficulty V1 outranks stale Factory class=dimension and class=color-count assumptions.

## Evidence policy

A builder log is a claim/evidence record, not proof.

Statements such as “all tests passed”, “implementation complete” or “requirements satisfied” must be independently verified by ChatGPT.

A passing suite does not override a direct contract violation.

Missing independent evidence remains `UNVERIFIED`, not silently promoted to PASS.

## Audit verdicts

Independent audits use one final verdict:

- `PASS`
- `CONDITIONAL`
- `FAIL`

Acceptance criteria use:

- `PASS`
- `PARTIAL`
- `FAIL`
- `UNVERIFIED`

Findings use severity:

- `BLOCKER`
- `MAJOR`
- `MINOR`
- `NOTE`

## Strict audit minimum

Every material strict audit should cover at least:

1. verdict;
2. recovered contract/scope;
3. branch/HEAD/diff scope;
4. acceptance matrix;
5. builder claims vs repository truth;
6. file/symbol evidence;
7. focused tests;
8. regressions;
9. security/safety/network review;
10. architecture consistency;
11. tracker/log/documentation truthfulness;
12. final repository state;
13. open cross-milestone/cross-repo findings;
14. defects by severity;
15. debt/opportunities;
16. unverified items;
17. regression risk;
18. confidence;
19. final verdict;
20. required remediation/next action.

## Remediation

If an audit is not unconditional PASS, ChatGPT decides whether a bounded remediation cycle is required.

Each finding should identify:

- source cycle/finding ID;
- severity;
- affected path/symbol/subsystem;
- incorrect current behavior;
- required target behavior;
- required changes;
- focused/regression tests;
- security/offline constraints;
- acceptance criteria;
- prohibited shortcuts.

## Historical evidence immutability

Existing `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, review packs and published evidence remain immutable historical records once used.

Do not rewrite failed history to appear successful.

## Existing PAG/SP evidence migration

Accepted PAG M00-M10 and PAG-SP work is preserved and mapped to the 224 canonical task IDs through migration audit.

No new canonical checkbox closes solely because a historical task had a similar name. The current task contract must be satisfied, including newer Difficulty V1 and cross-repo rules.

## Factory Core vs Studio

Core owns truth. Studio owns operator UX.

Allowed dependency:

`Studio -> Factory Core`

Forbidden:

`Factory Core -> Studio UI`

The owner-supplied Windows v1.3.6 application is a Studio source candidate, not an independent second compiler authority.

## Network / provider policy

The deterministic core must remain usable without a mandatory network dependency.

Semantic provider adapters and publishing adapters may use network services when explicitly selected/authorized. They must remain optional boundaries and must not make importing/testing the core depend on network availability.

Provider secrets and publishing credentials are never committed.

## Remote-content safety

Remote game content is declarative only.

Forbidden payloads include executable scripts intended for runtime execution, native libraries, plugins and arbitrary expression/eval code.

Runtime-downloaded content lives under `user://` and never replaces `res://` application code.

Publishing is staging-first, versioned, integrity-checked, reversible and auditable.

## Cross-repo closure

For cross-repo tasks, final acceptance requires producer and consumer evidence where applicable. Examples:

- `.scrubpack` producer + game parser golden vectors;
- manifest producer + runtime parser/compatibility tests;
- publisher staging artifact + real runtime download/integrity path;
- disable/rollback control-plane action + game behavior.

No task closes from only one half of an end-to-end contract when the task requires both.
