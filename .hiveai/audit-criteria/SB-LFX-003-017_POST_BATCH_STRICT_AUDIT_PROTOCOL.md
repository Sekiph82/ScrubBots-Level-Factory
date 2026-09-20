# SB-LFX-003..017 — Post-Batch Independent Strict Audit Protocol

Document role: CHATGPT AUDIT WORKFLOW CONTRACT

## Owner-authorized workflow

The builder implements SB-LFX-003 through SB-LFX-017 sequentially before any intermediate ChatGPT acceptance audit.

Each task must still have:
- its own audit criteria;
- its own implementation prompt;
- its own builder log created before task edits;
- identifiable implementation commit range/final implementation SHA;
- a task-final builder-log-only publication commit.

## Audit phase

After the complete builder batch, ChatGPT audits SB-LFX-003, 004, ... 017 in numerical order.

For every task ChatGPT must independently:
1. read the task builder log;
2. read that task's audit criteria and implementation prompt;
3. identify start, implementation and task-final log-only SHAs;
4. inspect exact task diff and relevant retained contracts;
5. inspect real tests/runtime evidence claimed;
6. distinguish builder-reported test results from independently inspected semantics;
7. assign PASS/CLOSED or CHANGES_REQUIRED with BLOCKER/MAJOR/MINOR/NOTE findings;
8. save a separate strict audit file to `.hiveai/audits/` before moving to the next task.

No post-batch audit may retroactively assume that a previous unaudited builder task was correct merely because a later task depends on it.

## Tracker policy

Root TASKS.md remains ChatGPT-owned.

During builder batch execution task checkbox state is intentionally not advanced by Codex.

After the post-batch audits, ChatGPT updates task truth from independent audit results. PASS tasks may close; failed tasks remain open and enter the remediation batch.

## Remediation phase

After all 003..017 audits are saved:
- create one remediation prompt per task with BLOCKER/MAJOR/MINOR findings requiring code changes;
- do not create needless remediation for PASS-only/NOTE-only tasks;
- preserve accepted code from tasks that passed;
- then create one master remediation prompt that executes all required task-specific remediations sequentially;
- each remediation gets its own builder log and task-final log-only publication;
- after remediation coding, run a second independent task-by-task audit only for remediated tasks.

This protocol does not weaken the individual audit criteria.
