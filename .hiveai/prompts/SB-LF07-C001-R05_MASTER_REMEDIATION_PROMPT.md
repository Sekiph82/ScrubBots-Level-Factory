# SB-LF07-C001-R05 — M07 Selective Master Remediation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative R05 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-C001-R05_REMEDIATION_INDEX.md

## Frozen PASS/CLOSED tasks
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement them.

Run only:
`005 -> 007 -> 008 -> 009 -> 010`

Do not start M08.

## R05 priorities

1. **Authentic provenance only.** Raw caller-created M03/M04/M05 references can never create sealed production provenance.
2. **Mandatory exact source guard.** A source-linked parent cannot run without a matching accepted M05 source context.
3. **One shared workload identity.** Mutation and regeneration must use the same canonical workload constructor and demonstrate one actual MATCHED case.
4. **Truthful regeneration evidence.** Raw generator success remains inconclusive unless accepted validation is actually bound.
5. **Regression and governance green.** Remove transient hard-coded task/status expectations from the governance regression and make full pytest green.

## Governance

- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audit files under `.hiveai/audits/**`.
- Preserve PASS/CLOSED 001/002/003/004/006 behavior/tests.
- Do not rewrite historical evidence.
- No reset/rebase/stash/clean/force-push/destructive checkout.
- Preserve owner/untracked files.
- No provider/network spend merely for tests.
- No synthetic PASS or proxy difficulty truth.
- Missing authority remains UNAVAILABLE/INCONCLUSIVE.
- Do not self-promote PASS/CLOSED.

## Per-task protocol

For each authorized task:
1. Read original criteria plus full C001/R01/R02/R03/R04 history and R04 re-audit.
2. Create the dedicated R05 builder log before product edits.
3. Close every remaining R04 finding.
4. Add adversarial tests that fail R04 behavior.
5. Run focused task tests plus affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
6. Run full pytest, compileall, Godot headless, git diff --check and protected-file no-diff proof.
7. Commit implementation separately, then terminal log-only publication.
8. Push, verify HEAD == origin/main, continue to next task.

## Required R05 logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-005-C001-R05_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-007-C001-R05_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R05_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-009-C001-R05_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R05_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log

Create:
`.hiveai/codex-logs/SB-LF07-C001-R05_MASTER_REMEDIATION_CODEX_LOG.md`

It must include:
- start/final Level Factory SHA;
- implementation + terminal-log SHA for 005,007,008,009,010;
- proof frozen tasks remained unchanged and green;
- forged-three-reference provenance rejection;
- missing/wrong source-context pre-operation rejection and all-path post-check proof;
- one actual MATCHED mutate-vs-regenerate workload using one shared canonical identity;
- same-seed/different-config mismatch proof;
- truthful regeneration validation/accounting availability;
- structurally future-proof governance regression;
- final full pytest, compileall, Godot, diff and protected-file results;
- explicit no-self-promotion statement.

Commit/push master log, verify HEAD == origin/main, then STOP.

## Final response format

Return ONLY 6 GitHub URLs, one per line:
1. R05 master remediation log;
2-6. task logs for 005,007,008,009,010 in that order.

No headings, bullets, prose, SHA-only lines or local paths.
