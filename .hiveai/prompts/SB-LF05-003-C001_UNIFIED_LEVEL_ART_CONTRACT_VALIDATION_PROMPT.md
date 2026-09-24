# SB-LF05-003-C001 — Unified Level Art Contract Validation

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-003`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-003-C001_UNIFIED_LEVEL_ART_CONTRACT_VALIDATION_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-003-C001_UNIFIED_LEVEL_ART_CONTRACT_VALIDATION_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Validate the complete accepted LEVEL_ART contract without mutating source.

For final gameplay LEVEL_ART require:
- exact production dimensions 20..59 per axis;
- cells count = width*height;
- C01..C16 only;
- actual used-color count 3..12;
- canonical cell/palette indexing;
- no foreign logical colors;
- no semi-alpha;
- final logical gameplay cells opaque;
- exact provenance chain from source/raw -> compiler/artifact -> LevelData;
- duplicate level IDs rejected against the supplied QA/catalog/batch context.

Distinguish source-image alpha from final LEVEL_ART: immutable OWNER_UPLOAD/raw semantic source may contain transparency, but that never makes transparent/semi-alpha logical gameplay cells legal.

Do not apply class-specific dimension or color-count bands.

Do not silently palette-snap, resize, recolor, repair or rename during validation. Validation reports facts/reasons only.

Tests: 20x59/59x20 legal, 19/60 illegal, 2 and 13 used colors illegal, off-palette, semi-alpha, transparent final cell, bad cell count/index, stale provenance, duplicate ID, unchanged bytes.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
