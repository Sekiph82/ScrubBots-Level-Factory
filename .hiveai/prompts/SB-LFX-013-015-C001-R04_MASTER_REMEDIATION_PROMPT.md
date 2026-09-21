# SB-LFX C001-R04 — MASTER REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main
Canonical local mirror: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

Execute the complete R04 remediation batch sequentially:

SB-LFX-013 → SB-LFX-015

Read:
- root TASKS.md;
- `.hiveai/audits/SB-LFX-011-016-C001-R03_STRICT_AUDIT_SUMMARY.md`;
- `.hiveai/prompts/SB-LFX-013-015-C001-R04_REMEDIATION_INDEX.md`;
- each task's R03 strict audit;
- each task's original audit criteria;
- each task's exact R04 prompt.

For EACH task:
1. sync main and confirm local == origin/main;
2. create the task's R04 builder log before product/test edits;
3. implement only the remaining R03 finding;
4. run focused Python + real Godot integration;
5. run retained dependent regressions;
6. run full pytest, compileall, Godot headless editor boot, diff-check and prove TASKS diff empty;
7. commit implementation/tests;
8. push and confirm equality;
9. finalize the builder log;
10. make one terminal log-only commit;
11. continue without waiting for audit.

Critical semantic rules:

SB-LFX-013:
- do not label prior successful stages “reused” while calling full `run_pipeline()`;
- either execute a true stage-aware continuation or mark unsupported retries NOT_AVAILABLE;
- prior successful stage operations must not run again.

SB-LFX-015:
- RESUMED means real canonical work advances beyond the interruption boundary;
- safe context re-entry alone is not RESUMED;
- if no executable remaining stage exists, use NOT_RESUMABLE / NEEDS_OPERATOR_ACTION;
- do not invent solver/difficulty capability.

Never:
- edit TASKS.md;
- reopen PASS/CLOSED SB-LFX semantics;
- fabricate provider/solver/difficulty/review/promotion truth;
- make network/provider-credit calls for tests.

After SB-LFX-015-R04 create:
`.hiveai/codex-logs/SB-LFX-C001-R04_MASTER_REMEDIATION_CODEX_LOG.md`

Master log must include for both tasks:
- builder-log URL;
- start SHA;
- implementation SHA;
- terminal log-only SHA;
- status;
- focused/runtime result;
- full-suite result.

Commit the master log alone in the final summary commit.

Return only:
- master R04 log URL;
- final summary SHA;
- the two per-task R04 log URLs.

STOP. ChatGPT performs the independent strict re-audit.
