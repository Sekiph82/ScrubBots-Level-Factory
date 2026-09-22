# SB-LF03-003..012-C001 - Master Batch Implementation Prompt

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authorization

Execute the complete remaining M03 Puzzle Intelligence implementation batch:

`SB-LF03-003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011 -> 012`

SB-LF03-001 and SB-LF03-002 are already PASS/CLOSED. Preserve them.

Canonical batch index:

`.hiveai/prompts/SB-LF03-003-012-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md`

Post-batch audit protocol:

`.hiveai/audit-criteria/SB-LF03-003-012-C001_POST_BATCH_STRICT_AUDIT_PROTOCOL.md`

Root tracker:
`TASKS.md`

## Absolute governance

- Do not modify `TASKS.md`.
- Do not mark any task PASS/CLOSED.
- Builder logs are claims only.
- Do not rewrite prior prompts/audits/logs.
- No force push/reset/clean/discard of unrelated user work.
- Preserve all accepted SB-LF03-001/002 semantics.
- Preserve all previously PASS/CLOSED Level Factory and SB-LFX behavior.

## Gameplay authority

Canonical gameplay truth remains:
https://github.com/Sekiph82/Scrubbots

Resolve current `main` SHA at batch start and again before any real cross-repository bridge work where drift would matter.

The Level Factory may implement generic search/orchestration/evidence algorithms, but must never copy canonical gameplay rules into Python.

Specifically do not reimplement:
- ProofState legal action semantics;
- ProofKernel placement/quiesce/routing/target/clear semantics;
- main-game completion/deadlock truth;
- canonical ProofState key semantics.

WFC is generation machinery, never gameplay solver authority.

## Batch execution rule

For each task in order:

1. Synchronize safely with current `origin/main`.
2. Read the task's exact prompt and exact audit criteria from the batch index.
3. Create that task's builder log at the exact indexed path **before product/test edits**.
4. Implement only that task's scope.
5. Add/retain focused tests.
6. Run the task's required focused/retained tests.
7. Run repository regression gates required by its prompt.
8. Run:
   - `git diff --check`
   - `git diff --exit-code -- TASKS.md`
9. Commit product/tests/docs + in-progress/finalized task log as the implementation commit.
10. Push `main`.
11. Finalize publication details in that task log.
12. Create a terminal log-only commit.
13. Push.
14. Continue to the next task.

Do not wait for ChatGPT audit between tasks.

## Dependency handling

A task may build on prior batch product code before prior tasks are independently audited.

If a required production capability is genuinely unavailable:
- preserve truthful UNAVAILABLE;
- implement only the safe interface/generic machinery allowed by the task prompt;
- record the exact limitation;
- never fabricate a production result merely to keep the batch moving.

If a task is technically blocked from meaningful implementation, log the blocker truthfully and continue only where later tasks can safely implement generic/dependency-gated layers without inventing semantics.

## Real canonical bridge

SB-LF03-009 is the production canonical-semantics bridge task.

It must attempt a real read-only headless execution path against the verified `Sekiph82/Scrubbots` checkout.

Do not modify the verified main-game checkout to insert bridge files.

Do not replace execution with source scraping.

If safe real execution cannot be established, record the blocker; do not fabricate closure.

## Regression discipline

No provider credits or external AI/provider calls merely for tests.

Use deterministic offline fixtures wherever possible.

Real canonical cross-repository integration may be capability-gated by a configured checkout, but once the capability is supplied it must execute rather than silently skip.

At every task keep prior accepted LF03 tests green unless an intentional versioned migration is explicitly required by that task prompt.

## Master log

After all ten task attempts, create:

`.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`

The master log must include for every task:
- task ID;
- builder-log path and full GitHub URL;
- implementation SHA;
- terminal log-only SHA;
- focused test result;
- full-suite result at that point;
- any skip with exact reason;
- any known limitation/blocker;
- confirmation TASKS diff was zero.

Then run a final batch-wide verification:
- all retained LF03 tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge regression if configured;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record final results in the master log.

Commit/push the master log as the final summary commit.

## Final response

Return only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`;
2. final master-log commit SHA;
3. the ten per-task builder-log GitHub URLs.

Then STOP.

ChatGPT will independently strict-audit all ten tasks after the complete batch and will create a separate master remediation batch only for tasks that require remediation.
