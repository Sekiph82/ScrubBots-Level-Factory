# SB-LF08-C001 — M08 Open-Task Master Batch Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF08-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md

## Authorization

Implement only the five currently open M08 tasks in this exact order:

`SB-LF08-001 -> SB-LF08-006 -> SB-LF08-007 -> SB-LF08-008 -> SB-LF08-009`

Do not reimplement accepted:
`SB-LF08-002,003,004,005,010` or accepted `SB-LFX-013,014,015`.

Do not start M09 unified roadmap work.

## Architecture rules

- Reuse accepted PAG-M09 deterministic batch/resume infrastructure rather than creating another batch engine.
- Reuse accepted PAG-M08 output bundle/artifact contracts.
- Reuse actual M03/M04/M05/M07 evidence/validation contracts.
- Reuse SB-LFX-006 owner-review authority; no parallel review database.
- SB-LF08-008 is only the Level Factory handoff envelope. Do not implement future Content Pipeline milestones.
- Factory acceptance, owner acceptance and handoff readiness are separate dispositions.
- Legacy PAG-M09 quality ACCEPT alone is not M08 production Factory acceptance.
- Never infer difficulty/lane from dimensions, color count or request labels.
- Missing capability/evidence is UNAVAILABLE/INCONCLUSIVE.
- Finite budgets only. No “generate until enough” unbounded loops.
- No provider/network spend merely for tests.
- Never edit root TASKS.md or `.hiveai/audits/**`.
- Preserve owner/untracked files and existing accepted task behavior.
- No reset/rebase/stash/clean/force-push/destructive checkout.

## Per-task protocol

For each task:
1. safely synchronize current main;
2. read its implementation prompt and strict audit criteria;
3. create its dedicated builder log **before product edits**;
4. implement only that task scope;
5. add focused positive/adversarial tests;
6. run focused tests plus all previously implemented M08 open-task tests;
7. run retained PAG-M08/PAG-M09, M03/M04/M05/M06/M07, Palette V3 and relevant SB-LFX review/pipeline tests;
8. run full `python -m pytest -q -p no:cacheprovider`;
9. run `python -m compileall -q src tests`, relevant Godot headless checks, `git diff --check`, and protected-file no-diff proof;
10. commit product implementation;
11. append exact files/commands/results/SHAs/capability limits to the task log;
12. commit terminal log separately, push, verify HEAD == origin/main;
13. continue immediately to the next task.

## Required logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF08-007-C001_OWNER_REVIEW_GATE_BEFORE_PUBLICATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF08-008-C001_CONTENT_PIPELINE_PRODUCTION_HANDOFF_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF08-009-C001_HIGH_REJECTION_STRESS_SAFETY_CODEX_LOG.md

## Final master log

Create:
`.hiveai/codex-logs/SB-LF08-C001_MASTER_BATCH_CODEX_LOG.md`

It must record:
- start/final repository SHAs;
- per-task implementation + terminal-log SHAs;
- exact existing batch/output/review contracts reused;
- proof accepted M08 tasks were not reimplemented/regressed;
- requested-vs-Factory-accepted lane counts;
- accepted batch artifact set;
- owner-review publication gate;
- Content Pipeline handoff envelope;
- high-rejection stress/boundedness;
- full focused/regression/full-suite/compileall/Godot/diff/protected-file results;
- explicit no-self-promotion statement.

Commit/push master log, verify HEAD == origin/main, then STOP.

## Final response format

Return ONLY 6 GitHub URLs, one per line:
1. M08 C001 master batch log
2. SB-LF08-001 log
3. SB-LF08-006 log
4. SB-LF08-007 log
5. SB-LF08-008 log
6. SB-LF08-009 log

No headings, bullets, prose, SHA-only lines or local paths.
