# SB-LF05-008-C001 — Owner Source Byte Preservation QA

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-008`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-008-C001_OWNER_SOURCE_BYTE_PRESERVATION_QA_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-008-C001_OWNER_SOURCE_BYTE_PRESERVATION_QA_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Integrate immutable OWNER_UPLOAD/source-library truth into Unified QA.

Requirements:
- owner source bytes remain byte-for-byte unchanged before/after every validation/analysis path;
- source SHA/length/dimensions must match the immutable source record;
- derived logical art/LevelData/preview/report are separate artifacts and paths;
- no normalized/quantized/resized output may overwrite or masquerade as OWNER_UPLOAD source;
- stale/corrupt/missing source record or bytes fail closed;
- repeated QA is idempotent and produces no meaningless source diff.

Reuse accepted owner_upload/source-library contracts. Do not invent a second source store.

Tests: pre/post exact bytes/SHA, re-run idempotence, corrupt source bytes, corrupt record, derived output separation, source filename/path metadata cannot override content identity.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
