# SB-LF07-003-C001-R01 — Remediation Prompt

Target: `SB-LF07-003`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Retain the useful +1 Slot easing concept but remediate its authority boundary.

Required corrections:
- Resolve exact current Scrubbots main at execution time, not the historical Palette V3 SHA.
- Bind repository SHA + source blob/path + mechanic/contract version, and fail closed if current-main capability/source verification is unavailable or drifts.
- Prove a stale historical commit identity is rejected even when its source content happens to match.
- Keep +1 Slot preconditions/bounds and forbid resize/recolor/difficulty-label shortcuts.
- Ensure the operator is installed in the task-appropriate concrete operator layer, not the SB-LF07-001 base substrate.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-003-C001-R01_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
