# SB-LF07-008-C001-R01 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Replace the caller-supplied counter DTO as the authoritative comparison path with evidence-derived matched execution comparison.

Required corrections:
- Mutation side must derive counters from real M07 AttemptReport/evidence.
- Regeneration side must bind to one already accepted generator route in this repository, with exact generator route/version/config/seed/budget/validation identities and real result evidence. Do not invent a new generator.
- Derive produced/accepted/rejected/inconclusive/solver-workload counters from evidence rather than trusting caller integers.
- Bind the same target/policy/seed-config/validation/budget workload across both paths.
- Provider cost may be accepted only from the existing trusted provider-accounting evidence contract, never because a caller sets trusted=true.
- Keep wall-clock/machine telemetry noncanonical and do not declare a global winner.
- Add forged-counter, mismatched-route, trusted-cost-authority and evidence-derived comparison tests.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R01_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
