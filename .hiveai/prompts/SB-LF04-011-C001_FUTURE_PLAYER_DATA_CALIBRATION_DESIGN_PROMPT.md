# SB-LF04-011-C001 — Future Player-Data Calibration Design

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-011

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-011-C001_FUTURE_PLAYER_DATA_CALIBRATION_DESIGN_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-011-C001_FUTURE_PLAYER_DATA_CALIBRATION_DESIGN_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

DESIGN/DISABLED ONLY. No analytics policy is approved here. Do not add telemetry upload, HTTP, SDKs, identifiers, profiling or runtime collection. Define state DISABLED_UNTIL_POLICY_APPROVED and a strict offline/import-only aggregate future CalibrationDataset/CalibrationPlan schema. Forbid names, emails, device/account IDs, IPs, raw event streams and free-form PII. Aggregate fields may include score-policy version, approved future anonymous cohort label, completion/failure aggregates, move-count aggregates and sample count. Require minimum sample count. Future calibration must create a new explicit policy version, never silently mutate Difficulty V1. Document privacy/product/security/retention/consent approval gates. Tests prove current production path cannot enable calibration/network behavior and forbidden identity fields are rejected.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
