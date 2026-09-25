# SB-LF07-007-C001-R02 — Remediation Prompt

Target: `SB-LF07-007`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-007-C001-R01_BOUNDED_MUTATION_ATTEMPTS_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_AUDIT_CRITERIA.md`

Close the runner, not just helper types.

Required:
- Make run_bounded_mutations consume the authentic SB-LF07-004 validation adapter and typed SB-LF07-006 target interface.
- Every attempt record, applied or not, must contain deterministic attempt provenance with ordinal, effective seed, exact request/parent/operator/authority and terminal reason.
- Define deterministic terminal precedence/aggregation and actually return TARGET_MATCH, ERROR, UNAVAILABLE, INCONCLUSIVE, REJECTED or true EXHAUSTED as appropriate.
- EXHAUSTED means the finite budget was genuinely consumed without a stronger terminal truth.
- Keep signed-64 seed bounds and strict no-post-limit calls.
- Add runner-level tests for each terminal disposition, non-applied provenance, overflow and replay.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-007-C001-R02_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
