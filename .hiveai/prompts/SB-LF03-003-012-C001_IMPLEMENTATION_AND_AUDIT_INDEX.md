# SB-LF03-003..012-C001 - Implementation and Audit Index

Document role: CANONICAL BATCH INDEX

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Closed prerequisites

- SB-LF03-001: PASS/CLOSED
- SB-LF03-002: PASS/CLOSED through C001-R01

These are immutable accepted prerequisites for this batch.

## Batch execution order

Execute exactly:

`SB-LF03-003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011 -> 012`

## Per-task contracts

### SB-LF03-003
Prompt:
`.hiveai/prompts/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_CODEX_LOG.md`

### SB-LF03-004
Prompt:
`.hiveai/prompts/SB-LF03-004-C001_DETERMINISTIC_BASELINE_SEARCH_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-004-C001_DETERMINISTIC_BASELINE_SEARCH_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-004-C001_DETERMINISTIC_BASELINE_SEARCH_CODEX_LOG.md`

### SB-LF03-005
Prompt:
`.hiveai/prompts/SB-LF03-005-C001_CANONICAL_VISITED_STATE_MEMOIZATION_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-005-C001_CANONICAL_VISITED_STATE_MEMOIZATION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-005-C001_CANONICAL_VISITED_STATE_MEMOIZATION_CODEX_LOG.md`

### SB-LF03-006
Prompt:
`.hiveai/prompts/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_CODEX_LOG.md`

### SB-LF03-007
Prompt:
`.hiveai/prompts/SB-LF03-007-C001_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-007-C001_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-007-C001_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_CODEX_LOG.md`

### SB-LF03-008
Prompt:
`.hiveai/prompts/SB-LF03-008-C001_BOUNDED_SOLUTION_COUNT_AND_ENTROPY_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-008-C001_BOUNDED_SOLUTION_COUNT_AND_ENTROPY_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-008-C001_BOUNDED_SOLUTION_COUNT_AND_ENTROPY_CODEX_LOG.md`

### SB-LF03-009
Prompt:
`.hiveai/prompts/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_CODEX_LOG.md`

### SB-LF03-010
Prompt:
`.hiveai/prompts/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_CODEX_LOG.md`

### SB-LF03-011
Prompt:
`.hiveai/prompts/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_CODEX_LOG.md`

### SB-LF03-012
Prompt:
`.hiveai/prompts/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_CODEX_LOG.md`

## Master builder log

After all ten task attempts:

`.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`

The master log must enumerate every task, implementation SHA, terminal log SHA, builder-log URL, regression result and any known limitation/blocker.

## Audit handoff

Codex never edits root `TASKS.md` and never marks PASS/CLOSED.

After the complete batch, ChatGPT independently audits all ten tasks one by one using:

`.hiveai/audit-criteria/SB-LF03-003-012-C001_POST_BATCH_STRICT_AUDIT_PROTOCOL.md`

Only ChatGPT may advance tracker state.

If any task is CHANGES_REQUIRED, ChatGPT will create:
- one remediation prompt per failed task;
- one remediation index;
- one master remediation prompt containing only failed tasks;
- separate remediation logs plus one master remediation log;
- independent post-remediation audits before closure.
