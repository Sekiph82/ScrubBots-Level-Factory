# SB-LF07-007-C001-R01 — Remediation Prompt

Target: `SB-LF07-007`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Fix bounded-attempt terminal truth and provenance.

Required corrections:
- Define deterministic terminal aggregation/precedence for ERROR, UNAVAILABLE, INCONCLUSIVE, REJECTED, TARGET_MATCH and genuine budget EXHAUSTED. Do not collapse all non-success runs into EXHAUSTED.
- Every attempt, including NO_CHANGE/INAPPLICABLE/ERROR/non-applied attempts, must have deterministic attempt provenance/evidence accounting with ordinal and effective seed.
- Enforce signed 64-bit bounds in attempt-seed derivation and fail closed before constructing an invalid request.
- Consume only authentic SB-LF07-004 remediated validation.
- Preserve strict max-attempt enforcement and no post-limit calls.
- Add all-terminal-outcome, overflow-boundary, non-applied provenance and replay tests.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-007-C001-R01_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
