# SB-LF07-006-C001-R01 — Remediation Prompt

Target: `SB-LF07-006`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Rebuild targeting on authentic M04/M05 evidence.

Required corrections:
- Consume only the remediated SB-LF07-004 authentic ValidationEnvelope/typed producer evidence.
- Challenge Score policy/version must be bound to the accepted M04 policy/result digest, not a free caller string.
- Define typed load/risk/retention constraint evidence or reuse accepted existing typed evidence. Do not accept arbitrary payload keys with boolean True as authority.
- Missing required safety evidence => INCONCLUSIVE/UNAVAILABLE, never default PASS.
- Preserve deterministic target range selection/tie-breaking and prohibition on dimensions/color-count/difficulty-label proxies.
- Add forged-policy, forged-constraint, stale-M04-digest and authentic-evidence tests.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-006-C001-R01_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
