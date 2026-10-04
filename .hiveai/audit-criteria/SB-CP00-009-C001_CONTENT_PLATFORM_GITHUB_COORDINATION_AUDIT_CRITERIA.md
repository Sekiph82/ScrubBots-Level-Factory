# SB-CP00-009-C001 - Content Platform GitHub Coordination - Audit Criteria

## PASS rule

PASS only if root `TASKS.md` remains the sole LF/CP tracker, ChatGPT/Codex ownership is mechanically documented/guarded, and builder publication evidence cannot become a competing task-state authority.

## A. Ownership
ChatGPT owns prompts/audits/tracker lifecycle; Codex owns implementation/tests/builder logs only.

## B. Sole tracker
No nested TASKS/roadmap/dashboard/task-state authority under Content Pipeline.

## C. Evidence receipt
Versioned immutable builder facts only. No PASS/acceptance authority or secret material.

## D. Git safety
Non-force main publication rules documented; no GitHub API credential/mutation automation.

## E. M11 log uniqueness
SB-CP00-003..009 builder-log paths are distinct and canonical.

## F. Regression
Require focused SB-CP00-009 PASS, prior SB-CP00-001..008 PASS, governance PASS, full pytest PASS except truthful skips, compileall PASS, diff check PASS.

Codex must not edit root `TASKS.md` or audit files.