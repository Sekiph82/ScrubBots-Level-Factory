# P3-R01 — Headless Batch Pipeline Audit Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Original owner P3 prompt, immutable:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md

Parent strict audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/P3_HEADLESS_BATCH_PIPELINE_STRICT_AUDIT.md

R01 audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CRITERIA.md

## Mandatory local ↔ GitHub main synchronization preflight

Before product/test edits:

1. Work only in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
2. Verify repository identity `Sekiph82/ScrubBots-Level-Factory`.
3. Verify branch `main`.
4. `git fetch origin --prune`.
5. Inspect local HEAD, `origin/main`, status, ahead/behind, stashes, and worktrees.
6. If clean and only behind, fast-forward with `git merge --ff-only origin/main`.
7. Preserve legitimate local/owner material non-destructively.
8. Never reset, rebase, stash, clean, force checkout, force push, or discard owner work.
9. Do not create a sibling Desktop clone/worktree/copy.
10. Stop before edits if safe reconciliation is impossible.

## Scope

This is a bounded audit-closure task only.

Do NOT change the original P3 prompt.

Do NOT redesign the P3 headless pipeline.

Do NOT change:
- canonical Studio orchestration authority;
- OWNER_UPLOAD immutability;
- ZIP supply/solve/Difficulty V1 authority;
- Review Queue terminal boundary;
- no-ACCEPT/no-publish behavior;
- concurrency default 1;
- offline core;
- producer manifest contract.

Only close P3-F01 and P3-F02 from the parent audit.

## R01.1 — True in-flight interruption tests

Replace/strengthen the current interruption test so every canonical stage is interrupted after its durable RUNNING checkpoint, before its completion checkpoint.

Stages:
- IMPORT
- NORMALIZE
- VALIDATE
- CANDIDATE
- ZIP_SUPPLY_SOLVE_DIFFICULTY
- QA
- REVIEW

For each stage prove:
- earlier completed stages are not re-executed;
- interrupted stage is retried/recovered exactly once;
- later stages complete;
- source bytes unchanged;
- producer manifest bytes unchanged;
- no duplicate candidate;
- no duplicate Review Queue entry;
- final canonical records equal uninterrupted canonical truth.

For ZIP add two explicit tests:

### ZIP-A
Interrupt after ZIP RUNNING and before `studio.run_pipeline` creates a canonical pipeline record.
Resume must execute canonical ZIP work once.

### ZIP-B
Simulate/process interruption after the canonical pipeline record is durably written but before P3's ZIP PASS checkpoint is written.
Resume must recover that existing `_pipeline_for_job` record and must NOT create a second canonical pipeline run.

Use deterministic counters/identity assertions.

If these tests expose a real resume defect, fix only that defect.

## R01.2 — Generic transient current-task governance regression

The full suite currently fails because the governance test assumes every current task is either:
- a canonical 224-row task, or
- one hard-coded historical maintenance exception.

Fix the TEST CONTRACT generically.

Do not edit root `TASKS.md`.

Do not add P3 to the 224 denominator.

Update `tests/unit/test_sb_lf00_007_governance_authority.py` so a current task outside the canonical denominator is accepted only when:
- current task ID is well-formed and hyphenated;
- Project Status declares it explicitly;
- Next Task/Action references it;
- Current Prompt points to an existing `.hiveai/prompts/*.md`;
- Current Audit Criteria points to an existing `.hiveai/audit-criteria/*.md`;
- Required Actor is uppercase/non-empty;
- task status is non-empty;
- the canonical 224 denominator and row states remain unchanged.

Make this generic for future owner-authorized transient maintenance/prompt cycles.
Do NOT hard-code `P3-R01`, `P3`, or another single ID as the exception.

Preserve the historical normalization assertions.

## Tests

Run:
- focused P3-R01 interruption suite;
- P3 parity integration;
- P3 CLI/status/idempotency/rejection/offline tests;
- relevant SB-LFX-005;
- relevant SB-LFX-015;
- governance authority unit test;
- full pytest;
- compileall;
- Factory Studio Godot headless/runtime suite;
- git diff --check.

Full pytest must be green except truthful capability skips.

## Builder governance

Do not edit:
- root `TASKS.md`;
- original `.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md`;
- `.hiveai/audits/**`;
- prior builder logs.

Create before edits:
`.hiveai/codex-logs/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CODEX_LOG.md`

Commit implementation/test corrections separately from final log publication.

Push `main`.
Fetch again.
Prove local HEAD == origin/main and ahead/behind 0/0.

Stop for independent ChatGPT re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CODEX_LOG.md
