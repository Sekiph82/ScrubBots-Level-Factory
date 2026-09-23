# SB-LF03-008-C001-R01 — Enumeration Binding Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-008 — Add bounded solution-count/entropy analysis.`

Audit:
`.hiveai/audits/SB-LF03-008-C001_BOUNDED_SOLUTION_COUNT_ENTROPY_ANALYSIS_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-008-C001-R01_ENUMERATION_BINDING_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Use the remediated SB-LF03-003 legal result validator for every enumeration query.

Fail closed on an AVAILABLE transition unless child state authority exactly matches parent authority.

A wrong-query move result or authority-switched child state must produce ERROR, never EXACT/LOWER_BOUND/INCONCLUSIVE derived from that graph.

Preserve:
- MOVE_SEQUENCE_V1 equivalence;
- deterministic caps;
- EXACT/LOWER_BOUND/INCONCLUSIVE truth;
- entropy versioning;
- no Difficulty mapping.

## Tests

Add negative enumeration cases for wrong query/state result binding and child authority drift.

Run focused 008 + 003/004 dependencies + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
