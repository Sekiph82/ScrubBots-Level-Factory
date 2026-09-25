# SB-LF07-002-C001-R02 — Remediation Prompt

Target: `SB-LF07-002`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-002-C001-R01_SAFE_HARDENING_CANONICAL_MECHANICS_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`

Close the remaining R01 authority finding.

Required:
- Keep the canonical M39 +1 Slot rollback hardening only if its source/mechanic contract remains current.
- Resolve Sekiph82/Scrubbots@main freshly during this task through the accepted authority resolver. Do not reuse a batch-start or test-constant SHA.
- Bind exact task-time main SHA + M39 source blob/path/version to the operator registry.
- Demonstrate rejection of the immediately previous main SHA even when the M39 source blob is byte-identical.
- Host the hardening operator in the SB-LF07-002 concrete operator module/service, not the SB-LF07-001 base module.
- Preserve canonical rollback preconditions, source/parent immutability, and no size/color/difficulty proxies.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-002-C001-R02_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
