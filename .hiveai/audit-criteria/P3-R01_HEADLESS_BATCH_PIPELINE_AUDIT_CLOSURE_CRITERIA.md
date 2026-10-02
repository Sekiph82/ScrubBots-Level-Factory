# P3-R01 — Headless Batch Pipeline Audit Closure

Document role: CHATGPT AUDIT CRITERIA

Parent prompt:
`.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md`

Parent strict audit:
`.hiveai/audits/P3_HEADLESS_BATCH_PIPELINE_STRICT_AUDIT.md`

## PASS rule

PASS only if P3-F01 and P3-F02 close without changing the owner P3 behavior.

## P3-F01 — True in-flight interruption coverage

For every canonical stage:
- IMPORT
- NORMALIZE
- VALIDATE
- CANDIDATE
- ZIP_SUPPLY_SOLVE_DIFFICULTY
- QA
- REVIEW

the focused test must interrupt immediately after the durable RUNNING checkpoint and before that stage's completion event.

After restart prove:
- all previously completed stages are not rerun;
- the interrupted stage is retried/recovered exactly once;
- later stages continue;
- no duplicate source/candidate/pipeline/review-queue identity is created;
- final canonical source/candidate/pipeline/review-queue truth matches an uninterrupted run.

ZIP additionally requires two crash windows:
1. interruption before a canonical pipeline record exists -> canonical ZIP work executes on resume;
2. canonical pipeline record exists but P3 completion checkpoint is absent -> resume reuses that exact canonical pipeline record instead of creating a duplicate.

Do not alter production behavior merely to satisfy the test unless a real defect is exposed.

## P3-F02 — Generic transient-task governance contract

Keep:
- root `TASKS.md` as sole tracker authority;
- canonical source-requirement denominator exactly 224;
- existing live row states unchanged;
- no new transient task row added to the 224 denominator.

Update the governance regression so an owner/ChatGPT-authorized transient current task outside the denominator is valid when all of these are true:
- current task ID is a well-formed hyphenated uppercase/digit ID;
- it is explicitly declared in Project Status;
- Current Task Status is non-empty;
- Required Actor is valid uppercase;
- Next Task/Action references the same current task/prompt;
- Current Prompt exists and is under `.hiveai/prompts/`;
- Current Audit Criteria exists and is under `.hiveai/audit-criteria/`;
- the transient task does not pretend to be one of the 224 canonical source-requirement rows.

Do not hard-code P3 as a one-off exception.
Do not weaken tracker authority.
Do not edit historical task rows or denominator.

## Regression

Required:
- strengthened P3 interruption tests PASS;
- Studio parity PASS;
- P3 idempotency PASS;
- P3 rejection truth PASS;
- SB-LFX-005 relevant regressions PASS;
- SB-LFX-015 relevant regressions PASS;
- governance authority test PASS;
- full pytest green except truthful environment capability skips;
- compileall PASS;
- Factory Studio headless/runtime PASS;
- git diff --check PASS.

Builder must not edit:
- the original P3 prompt;
- the P3 strict audit;
- root TASKS.md;
- any prior logs/audits.
