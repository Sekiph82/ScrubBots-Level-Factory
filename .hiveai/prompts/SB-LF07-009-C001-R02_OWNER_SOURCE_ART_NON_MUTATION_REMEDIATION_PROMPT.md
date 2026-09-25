# SB-LF07-009-C001-R02 — Remediation Prompt

Target: `SB-LF07-009`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-009-C001-R01_OWNER_SOURCE_ART_NON_MUTATION_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_AUDIT_CRITERIA.md`

Use the accepted M05 source authority directly and make it mandatory.

Required:
- Remove the duplicate M07 OwnerSourceRecord authority.
- Import/reuse qa.source_preservation.OwnerSourceRecord, SourcePreservationReport and verify_owner_source_preservation directly.
- Define source-linked M07 orchestration context so mutation -> authentic validation -> targeting -> bounded success cannot complete without pre/post M05 preservation PASS.
- Missing/stale/corrupt source record or failed preservation => ERROR/UNAVAILABLE and no eligible/target success.
- Use accepted M05 alias/samefile semantics and derived artifact separation.
- Add integrated tests around hardening, easing and bounded targeting, not standalone helper tests.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-009-C001-R02_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
