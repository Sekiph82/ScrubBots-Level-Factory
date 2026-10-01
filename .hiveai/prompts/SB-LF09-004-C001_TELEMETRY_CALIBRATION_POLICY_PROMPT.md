# SB-LF09-004-C001 — Telemetry-Calibrated Difficulty Policy

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Owner-approved policy:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/policies/SB_LF09_004_ANALYTICS_DATA_POLICY_V01.md

Strict audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_AUDIT_CRITERIA.md

## Task

Implement SB-LF09-004 exactly under the approved V01 policy.

Build a versioned, deterministic, privacy-safe, advisory-only telemetry calibration subsystem that consumes gameplay aggregate evidence and compares it to the accepted deterministic M04 difficulty result.

## Hard boundaries

- M03/M04 remains canonical difficulty authority.
- Telemetry never auto-mutates Challenge Score or lane.
- No live per-player personalization.
- No live/online learning.
- No LevelData/gameplay/source-art mutation.
- No core runtime internet dependency.
- No provider/network spend merely for tests.
- Missing analytics => UNAVAILABLE, never fabricated PASS.
- Below 100 valid sessions => INSUFFICIENT_DATA.
- Raw telemetry retention <= 90 days.
- Aggregate calibration retention <= 12 months.
- No prohibited PII from the policy.

## Implement

1. Closed versioned approved telemetry event/session schema.
2. Validation/filtering for allowed fields only.
3. Retention-aware evidence selection.
4. Duplicate/session identity protection.
5. Deterministic aggregate evidence contract.
6. Versioned immutable advisory calibration report.
7. Exact cross-binding to M04 analysis / Challenge Score / lane/version.
8. >=100-session recommendation threshold.
9. Explicit ADVISORY_READY / INSUFFICIENT_DATA / UNAVAILABLE / INCONCLUSIVE / ERROR dispositions.
10. Deterministic observed-vs-predicted divergence evidence.
11. Offline/unavailable path preserving canonical M04 truth.
12. Focused privacy, retention, threshold, tamper, mismatch and determinism tests.

Do not implement future production auto-calibration coefficients or promotion logic.

## Builder governance

- Work on `main`.
- Use only canonical local project root if local execution is needed:
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Do not create Desktop sibling clones/worktrees.
- Do not create another branch unless explicitly authorized.
- Do not edit root `TASKS.md`.
- Do not edit `.hiveai/audits/**`.
- Create the builder log before product edits:
  `.hiveai/codex-logs/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_CODEX_LOG.md`

## Verification

Run focused task tests, retained SB-LF09-001/002/003, affected M03/M04/M05/M06/M07/M08/Palette tests, full pytest, compileall, Godot headless and git diff --check.

Commit implementation separately from terminal log publication. Push to `main`, verify local HEAD == origin/main, then stop for independent ChatGPT audit.

## Final response

Return only the full GitHub URL of:

`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_CODEX_LOG.md`
