# SB-LF03-005,009..012-C001-R02 — Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

## Authorization

Remediate only:
SB-LF03-005 -> SB-LF03-009 -> SB-LF03-010 -> SB-LF03-011 -> SB-LF03-012

R02 index:
.hiveai/prompts/SB-LF03-005-012-C001-R02_REMEDIATION_INDEX.md

R01 re-audit summary:
.hiveai/audits/SB-LF03-003-012-C001-R01_STRICT_REAUDIT_SUMMARY.md

Do not reopen 003, 004, 006, 007 or 008 except for the minimum compatibility edit required by an accepted dependency API migration. Preserve their accepted semantics and tests.

## Governance

- Do not edit root TASKS.md.
- Do not create/edit .hiveai/audits/.
- Do not rewrite prior prompts/logs.
- Each R02 task gets its own new builder log, implementation commit and terminal log-only commit.
- No force push/reset/clean/stash/discard of unrelated owner work.
- No Python clone of ScrubBots gameplay rules.
- No provider credits/network calls merely for tests.

## Canonical ScrubBots execution rule

Resolve current Sekiph82/Scrubbots main at execution time.
The owner's primary ScrubBots working checkout may be dirty and must not be cleaned or modified.

For 009/012, create an independent temporary clean Git checkout from the local ScrubBots repository/object store at the exact canonical commit. Prefer a local-path clone or another method that leaves the owner's working tree/content untouched. Verify clean Git status and exact source bytes before execution.

Use the committed Level Factory external runner and the locally available Godot executable to perform real CanonicalHeadlessBridge.invoke() operations.
A dirty primary checkout is not a valid reason to skip if a clean local execution checkout can be created.

## Per-task order

For each task:
1. safely sync Level Factory main;
2. read its R01 re-audit and exact R02 prompt;
3. create the R02 builder log before product edits;
4. implement only the stated findings;
5. run focused + affected dependent tests;
6. run required retained/full gates;
7. verify TASKS.md diff zero;
8. commit/push implementation + tests/docs/log;
9. finalize task log and publish terminal log-only commit;
10. continue to next task.

## Key closure requirements

005: bare/unbound memo observation must no longer succeed.

009: real canonical invoke must actually run against a clean verified independent checkout; capability must verify the expected runner contract and cannot accept arbitrary runner files.

010: replay MATCH requires explicit current closed execution context; missing context cannot self-validate from manifest.

011: operational wall-clock timeout must be non-canonical telemetry only; deterministic max-visited enforcement remains real.

012: negative regression families must be real declarative payloads and executed; canonical invoke regression must really invoke gameplay; full repository pytest must be green. Diagnose and fix the six R01 full-suite failures without weakening LF00/LF06 contracts.

## Final R02 verification

After all five tasks:
- all retained LF03 tests;
- affected LF00/LF06 tests;
- full python -m pytest -q;
- repeat full pytest from clean tracked state if practical;
- python -m compileall -q src tests;
- Level Factory Godot headless editor boot;
- real canonical legal_moves/apply_placement/solve bridge regression;
- git diff --check;
- git diff --exit-code -- TASKS.md.

Create final master log:
.hiveai/codex-logs/SB-LF03-C001-R02_MASTER_REMEDIATION_CODEX_LOG.md

Record per-task builder-log URLs, implementation SHAs, terminal log-only SHAs, focused/full test results, real canonical invoke evidence, skips/limitations, and TASKS zero diff.

Commit/push master log, then STOP for independent ChatGPT re-audit.

## Final response

Return only:
1. full GitHub URL of the R02 master remediation log;
2. final master-log commit SHA;
3. five R02 builder-log GitHub URLs.