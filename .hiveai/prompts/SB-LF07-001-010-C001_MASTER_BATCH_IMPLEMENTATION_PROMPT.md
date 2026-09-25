# SB-LF07-001..010-C001 — M07 Master Batch Implementation Prompt

Document role: CODEX MASTER BATCH PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-001-010-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

## Authorization

Implement, in this exact order and without stopping for intermediate ChatGPT review:

`SB-LF07-001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010`.

For each task, read its dedicated implementation prompt AND strict audit criteria before editing anything.

Do not start M08.

## Non-negotiable governance

- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audit files under `.hiveai/audits/**`.
- Do not rewrite historical logs/audits/evidence.
- Preserve owner working files and untracked files.
- No reset, rebase, stash, clean, force-push, destructive checkout, or silent owner-file overwrite.
- If `origin/main` advances, fetch and integrate safely/non-destructively.
- Canonical gameplay truth remains current `Sekiph82/Scrubbots`; do not clone gameplay mechanics into Python.
- Palette V3 remains canonical.
- No board-size/color-count difficulty inference.
- No owner-source mutation.
- No network/provider credits merely for tests.
- Missing canonical capability/evidence => truthful UNAVAILABLE/INCONCLUSIVE, never fabricated PASS.

## Per-task execution protocol

For each task 001..010:

1. Safely synchronize current `main` / `origin/main`.
2. Read the task prompt + audit criteria + all accepted predecessor contracts it depends on.
3. Create the task-specific builder log BEFORE product edits.
4. Implement only that task's authorized scope.
5. Run focused tests and all earlier M07 task tests.
6. Run retained relevant M03/M04/M05/M06 + Palette V3 tests.
7. Run full repository pytest, compileall, Godot headless checks, `git diff --check`, and prove `TASKS.md` unchanged.
8. Where current Scrubbots authority is needed, resolve current main and use a clean exact-SHA/read-only capability; prove no mutation.
9. Commit product implementation for the task.
10. Append exact commands/results/changed files/implementation SHA/capability limits to that task's builder log.
11. Commit the terminal builder-log update separately.
12. Push and verify local HEAD == origin/main.
13. Immediately continue to the next M07 task. Do NOT wait for ChatGPT.

A predecessor task's builder completion may be used as an implementation dependency for later tasks, but it remains unaudited until ChatGPT reviews it after the batch. Never relabel builder completion as PASS/CLOSED.

## Required task logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log

After all ten task publications, create:

`.hiveai/codex-logs/SB-LF07-C001_MASTER_BATCH_CODEX_LOG.md`

It must include:
- starting/final repository SHAs;
- per-task implementation SHA and terminal log SHA;
- per-task focused gate results;
- final full regression/compileall/Godot/diff/TASKS results;
- exact Scrubbots authority SHA(s) used where applicable;
- capability limits/UNAVAILABLE evidence;
- owner-source and parent non-mutation proof;
- Palette V3 preservation;
- explicit statement that no task was self-promoted to PASS/CLOSED.

Commit/push the master log, verify `HEAD == origin/main`, then STOP for independent ChatGPT audit.

## Final response format

Your final chat response must contain ONLY GitHub URLs, one URL per line, with no headings, bullets, prose, SHA-only lines or local filesystem paths.

Return exactly these 11 GitHub URLs:
1. the master batch log URL;
2-11. the ten task-specific builder-log URLs in SB-LF07-001..010 order.
