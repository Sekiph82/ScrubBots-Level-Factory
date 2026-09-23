# SB-LF04-004-C001 — Canonical Dependency Depth

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-004`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-004-C001_CANONICAL_DEPENDENCY_DEPTH_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-004-C001_CANONICAL_DEPENDENCY_DEPTH_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement the SB-LF04-004 canonical dependency-depth boundary.

First inspect current Sekiph82/Scrubbots authority for an actual dependency/precedence semantic source. If it exists and can be invoked without copying rules, bind to it. If not, implement the versioned provider contract and leave production dependency_depth unavailable/absent.

Never reinterpret solution path length as dependency depth.

Add fixture providers only for unit tests and make them impossible to select as production authority.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
