# SB-LF07-001..010-C001-R02 — M07 Master Remediation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative R02 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-001-010-C001-R02_REMEDIATION_INDEX.md

## Authorization

Remediate all ten M07 tasks in this exact order, without stopping for intermediate review:

`SB-LF07-001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010`.

Read each task's original criteria, C001 audit, R01 prompt/log, R01 re-audit and R02 prompt before editing.

Do not start M08.

## R02 priorities

1. **Architectural separation first.** SB-LF07-001 base substrate must be physically/API-separated from 002..009 services.
2. **Fresh authority per task.** Resolve exact `Sekiph82/Scrubbots@main` inside each authority-dependent task. Never reuse a batch-start SHA. Record exact task-time SHA and source blob.
3. **Authentic producer evidence.** M07 production eligibility must adapt actual accepted M03/M04/M05 result objects, not self-signed wrappers over generic evidence.
4. **Graph provenance.** Explicit registered root, exact parent chain and typed stage evidence.
5. **Typed production targeting and truthful attempts.** Retire free-form production target path; runner must return real terminal disposition and provenance on every attempt.
6. **Real efficiency evidence.** Derive mutation counters from AttemptReport and regeneration counters from one accepted generator execution/result; accounting must come from actual trusted accounting evidence.
7. **M05 source authority directly.** No duplicate M07 owner-source authority; make preservation mandatory in source-linked orchestration.
8. **Regression last.** SB-LF07-010 must fail if any above boundary regresses.

## Governance

- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audits under `.hiveai/audits/**`.
- Do not rewrite historical evidence.
- No reset/rebase/stash/clean/force-push/destructive checkout.
- Preserve owner/untracked files.
- No invented gameplay/difficulty semantics.
- No size/color-count/difficulty-label proxies.
- No synthetic producer PASS in production paths.
- No network/provider spend merely for tests.
- Missing capabilities remain UNAVAILABLE/INCONCLUSIVE.
- Do not self-promote PASS/CLOSED.

## Per-task protocol

For each 001..010:
1. Safely sync current Level Factory main.
2. If gameplay authority is relevant, resolve Scrubbots main **now**, inside this task, and record exact SHA/blob/path/version.
3. Create task R02 builder log before product edits.
4. Close every remaining R01 finding.
5. Add adversarial tests that fail the R01 implementation.
6. Run focused task + affected M07 + retained M03/M04/M05/M06/Palette V3 tests.
7. Run full pytest, compileall, Godot headless checks, git diff --check and TASKS no-diff proof.
8. Commit product implementation.
9. Append changed files, commands/results, exact authority/evidence identities and capability limits to that task log.
10. Commit terminal log separately, push, verify HEAD == origin/main.
11. Continue immediately to next task.

## Required R02 logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-001-C001-R02_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-002-C001-R02_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-003-C001-R02_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-004-C001-R02_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-005-C001-R02_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-006-C001-R02_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-007-C001-R02_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R02_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-009-C001-R02_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R02_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log

Create:
`.hiveai/codex-logs/SB-LF07-C001-R02_MASTER_REMEDIATION_CODEX_LOG.md`

It must include:
- start/final Level Factory SHAs;
- per-task implementation and terminal-log SHAs;
- **per-task** Scrubbots current-main SHA where authority was required;
- exact frozen finding closure mapping;
- authentic M03/M04/M05 adapter proof;
- graph root/cycle proof;
- typed target + all runner terminal disposition proof;
- evidence-derived real regenerate comparison proof;
- accepted M05 source orchestration proof;
- final focused/full regression + compileall/Godot/diff/TASKS gates;
- Palette V3 preservation;
- explicit no-self-promotion statement.

Commit/push the master log and verify HEAD == origin/main, then STOP.

## Final response format

Return ONLY 11 GitHub URLs, one per line:
1. R02 master remediation log;
2-11. R02 task logs 001..010 in order.

No headings, bullets, prose, SHA-only lines or local paths.
