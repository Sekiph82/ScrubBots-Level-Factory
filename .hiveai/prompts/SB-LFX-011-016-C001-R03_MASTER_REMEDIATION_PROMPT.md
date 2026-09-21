# SB-LFX C001-R03 — MASTER REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main
Canonical local mirror: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

Execute the R03 remediation batch sequentially in one run:

SB-LFX-011 → 012 → 013 → 015 → 016.

Do not reopen or alter accepted semantics of PASS/CLOSED SB-LFX-004, 005, 006, 007, 008, 009, 010, 014, or 017 except for strictly necessary compatibility regression fixes that do not weaken accepted contracts.

Read:
- root TASKS.md;
- `.hiveai/audits/SB-LFX-005-017-C001-R02_STRICT_AUDIT_SUMMARY.md`;
- `.hiveai/prompts/SB-LFX-011-016-C001-R03_REMEDIATION_INDEX.md`;
- each task's saved R02 strict audit;
- each task's original audit criteria;
- each task's exact R03 prompt.

For EACH R03 task:
1. sync main and confirm local == origin/main;
2. create that task's R03 builder log before product/test edits;
3. implement only the remaining findings in its R02 audit/R03 prompt;
4. run focused Python + required real Godot integration;
5. run retained dependent regressions;
6. run full pytest, compileall, Godot headless editor boot, diff-check, and prove TASKS diff empty;
7. commit non-log implementation/tests/docs and record FINAL R03 IMPLEMENTATION SHA;
8. push and confirm equality;
9. finalize only that task's R03 builder log;
10. make exactly one task-final LOG-ONLY commit and record its SHA;
11. continue to the next task without waiting for audit.

Cross-task dependency:
- SB-LFX-012 must complete before SB-LFX-016 finalization because similarity consumes revision authority.

Critical closure rules:
- 011: prove real draft/preset divergence and real durable unsupported/non-replayable capability through the UI-gated Exact Reproduce path.
- 012: prove revision operations through the real surface and a true fresh Studio/process restart, with review/promotion truth separation.
- 013: product failure/retry truth must be canonical-scanner-only; no caller-created free-form failure fallback.
- 015: RESUMED must execute real safe continuation and reuse successful durable stage evidence, not only classify references.
- 016: Candidate/Comparison/Search must render operator-visible canonical advisory similarity state; no GDScript score recomputation.

Never:
- edit TASKS.md;
- fabricate provider, solver, difficulty, owner-review, promotion/export or resume capability;
- weaken immutable source/candidate/review/revision contracts;
- spend provider credits or make network calls merely for tests.

If a task cannot be completed safely, leave main green, finalize its R03 log as BLOCKED with exact evidence, and continue only where later tasks remain truthful.

After SB-LFX-016-R03 create:
`.hiveai/codex-logs/SB-LFX-C001-R03_MASTER_REMEDIATION_CODEX_LOG.md`

The master log must include for each task:
- builder-log URL;
- start SHA;
- final implementation SHA;
- terminal log-only SHA;
- status;
- focused/runtime result;
- full-suite result.

Commit the master remediation log alone in the final summary commit.

Return only:
- master R03 log URL;
- final summary SHA;
- compact list of the five per-task R03 log URLs.

STOP. ChatGPT performs the independent strict re-audit after the complete R03 batch.
