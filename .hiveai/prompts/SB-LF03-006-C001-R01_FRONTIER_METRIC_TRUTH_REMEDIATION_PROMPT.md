# SB-LF03-006-C001-R01 — Frontier Metric Truth Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-006 — Record solution path/states/dead ends/depth/branching/solve time.`

Audit:
`.hiveai/audits/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-006-C001-R01_FRONTIER_METRIC_TRUTH_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Fix `frontier_peak` truth.

Current `depth + 1` is not DFS frontier size.

Preferred fix:
- instrument baseline search with observer evidence for the real count of pending search nodes/branches;
- record actual peak pending frontier deterministically.

Alternative:
- remove/rename `frontier_peak` if the current recursive engine cannot truthfully observe it.

Do not duplicate `maximum_depth` under another name.

Keep elapsed time non-canonical.

## Tests

Add a wide shallow graph where maximum depth is small but pending DFS frontier is larger. Prove the metric reports the true frontier peak and differs from max depth where expected.

Retain existing evidence determinism, dead-end, path, timing exclusion and unavailable tests.

Run focused 006 + 004/005 dependencies + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
