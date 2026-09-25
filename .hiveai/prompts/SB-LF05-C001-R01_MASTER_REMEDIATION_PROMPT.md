# SB-LF05-C001-R01 — M05 Master Remediation Prompt
Document role: CODEX MASTER REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization
Remediate only:
`SB-LF05-001 -> 002 -> 003 -> 004 -> 005 -> 007 -> 008 -> 010`

Do not reopen SB-LF05-006/009 except minimal compatibility.

Index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF05-C001-R01_REMEDIATION_INDEX.md

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF05-C001_STRICT_AUDIT_SUMMARY.md

## Governance
- Never edit root TASKS.md or ChatGPT audit files.
- Create each R01 builder log before edits.
- One implementation commit + terminal log-only commit per task.
- No Python clone of main-game validators/importer/gameplay.
- Re-resolve current Scrubbots main where required; exact-SHA clean checkout only.
- Missing capability => UNAVAILABLE, never fabricated PASS.
- No size/color difficulty inference; no source/art/LevelData/main-game mutation.
- No provider credits/network merely for tests; no new skip/xfail hiding failures.

## Frozen themes
001 exact LevelData/provider binding.
002 exact M09 intermediate LevelData palette/order/cells.
003 exact dimensions/opacity/full lineage.
004 exact solver level/source/request/authority/budget binding.
005 truly closed outcome/statistics catalog.
007 closed provenance-bearing QA report.
008 accepted OWNER_UPLOAD record + dimensions + destination separation.
010 current-main resolution + full handoff cross-lineage + truthful M30/M47/M48.

## Per-task process
Sync main; read audit/R01/original criteria; create log; remediate; run focused/predecessor and retained M03/M04/M05/M06/SP05/SP06 tests; use clean exact-SHA Scrubbots capability where required and prove non-mutation; run full pytest, compileall, Godot headless, git diff --check, TASKS no-diff; publish implementation and terminal log; continue.

R01 task logs:
- .hiveai/codex-logs/SB-LF05-001-C001-R01_EXACT_LEVELDATA_MAIN_GAME_VALIDATION_BOUNDARY_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-002-C001-R01_EXACT_M09_LEVELDATA_PALETTE_ROUND_TRIP_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-003-C001-R01_COMPLETE_LEVEL_ART_VALIDATION_PROVENANCE_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-004-C001-R01_SOLVER_EVIDENCE_SOURCE_REQUEST_IDENTITY_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-005-C001-R01_CLOSED_QA_OUTCOME_CATALOG_INTEGRITY_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-007-C001-R01_CLOSED_MACHINE_READABLE_QA_EVIDENCE_ENVELOPE_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-008-C001-R01_OWNER_SOURCE_RECORD_DIMENSION_SEPARATION_CODEX_LOG.md
- .hiveai/codex-logs/SB-LF05-010-C001-R01_CURRENT_MAIN_RESOLUTION_CROSS_LINEAGE_HANDOFF_CODEX_LOG.md

After all eight create:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md

Master log must include per-task implementation/terminal SHAs, focused/full results, exact Scrubbots SHA(s), capability limits, non-mutation, TASKS zero diff. Commit/push then STOP for ChatGPT re-audit.

Final response only: master log URL, final SHA, eight task-log URLs.
