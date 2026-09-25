# SB-LF07-001..010-C001-R01 — M07 Master Remediation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative R01 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-001-010-C001-R01_REMEDIATION_INDEX.md

## Authorization

Remediate all ten M07 tasks in this exact order without stopping for intermediate review:

`SB-LF07-001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010`.

For every task, read:
1. original strict audit criteria;
2. C001 strict audit frozen findings;
3. task-specific R01 remediation prompt;
4. all accepted predecessor contracts it depends on.

Do not start M08.

## Non-negotiable governance

- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audit files under `.hiveai/audits/**`.
- Never weaken original criteria to make tests pass.
- Do not rewrite historical logs, prompts, audits or commits.
- Preserve owner files/untracked files.
- No reset/rebase/stash/clean/force-push/destructive checkout.
- Resolve current `Sekiph82/Scrubbots@main` whenever a task requires current gameplay authority; do not treat historical `edf672f...` as permanently current.
- No invented gameplay/difficulty semantics.
- No size/color-count/difficulty-label proxies.
- No synthetic M03/M04/M05 PASS evidence in production acceptance paths.
- No silent OWNER_UPLOAD mutation.
- No provider/network spending merely for tests.
- Missing capability/evidence remains UNAVAILABLE/INCONCLUSIVE.

## Per-task R01 protocol

For each 001..010:
1. Synchronize safely with current origin/main.
2. Create the dedicated R01 builder log before product edits.
3. Close every frozen finding for that task with forward changes.
4. Add adversarial tests that would fail the old C001 behavior.
5. Run focused task tests plus all affected M07 predecessor/successor tests.
6. Run retained relevant M03/M04/M05/M06 + Palette V3 gates.
7. Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
8. Commit remediation implementation.
9. Append exact commands/results/changed files/authority SHAs/capability limits to that task's R01 log.
10. Commit the terminal log update separately.
11. Push and verify HEAD == origin/main.
12. Continue immediately to the next task.

## Required R01 task logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-001-C001-R01_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-002-C001-R01_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-003-C001-R01_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-004-C001-R01_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-005-C001-R01_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-006-C001-R01_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-007-C001-R01_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R01_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-009-C001-R01_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R01_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log

After all ten remediations, create:
`.hiveai/codex-logs/SB-LF07-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md`

It must include:
- start/final Level Factory SHAs;
- exact current Scrubbots authority SHA(s) resolved during R01;
- per-task implementation SHA + terminal log SHA;
- per-task frozen finding closure mapping;
- final focused and full regression results;
- compileall/Godot/diff/TASKS no-diff evidence;
- proof no production path accepts synthetic M03/M04/M05 evidence;
- proof hardening/easing semantics are canonically justified or truthfully unavailable;
- graph-cycle/missing-parent provenance negatives;
- terminal attempt outcome/seed-bound evidence;
- real accepted regeneration-route comparison evidence;
- integrated M05 OWNER_UPLOAD gate evidence;
- Palette V3 preservation;
- explicit statement that no task was self-promoted PASS/CLOSED.

Commit/push the master log, verify HEAD == origin/main, then STOP.

## Final response format

Return ONLY 11 GitHub URLs, one URL per line:
1. R01 master remediation log;
2-11. R01 task logs 001..010 in order.

No headings, bullets, prose, SHA-only lines or local paths.
