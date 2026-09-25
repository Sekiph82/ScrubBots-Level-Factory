# SB-LF07-001-C001-R02 — Remediation Prompt

Target: `SB-LF07-001`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-001-C001-R01_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_AUDIT_CRITERIA.md`

Close the remaining R01 findings without weakening the original C001 criteria.

Required:
- Split the SB-LF07-001 base substrate into a dedicated module/API containing only authority resolution, immutable candidate/request/result/lineage identities, registry interface, and engine substrate.
- Move concrete hardening/easing operators, evidence validation, targeting, attempts, efficiency comparison, and OWNER_UPLOAD logic out of the base substrate into task-owned modules/services.
- SB-LF07-001 tests must run without importing future-task implementations.
- Keep current-main resolver capability and fail-closed UNAVAILABLE/DRIFT semantics.
- Preserve deterministic digests, deep parent immutability, distinct child identity and closed dispositions.
- Do not rewrite prior history; remediate forward.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-001-C001-R02_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
