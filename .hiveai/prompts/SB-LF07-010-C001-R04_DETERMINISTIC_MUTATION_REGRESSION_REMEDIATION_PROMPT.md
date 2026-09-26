# SB-LF07-010-C001-R04 — Remediation Prompt

Target: `SB-LF07-010`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-010-C001-R03_DETERMINISTIC_MUTATION_REGRESSION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Rebuild final M07 closure after R04 004..009 are fixed.

Required:
- Positive closure must use only sealed production APIs.
- Prove free-form synthetic evidence and self-asserted receipts cannot yield production ELIGIBLE.
- Prove authentic provenance evidence references cannot be caller-replaced.
- Prove fabricated TRUE safety cannot yield target MATCH; use only supported sealed target semantics.
- Exercise every authentic runner terminal and error-conversion path.
- Compare actual regeneration with full config workload matching and the same accepted validation chain.
- Prove same-seed/different-config mismatch is rejected.
- Prove cost/accounting remains unavailable.
- Prove source post-check catches byte mutation on applied, non-applied and exception paths.
- Preserve PASS/CLOSED SB-LF07-001/002/003, Palette V3 and no-proxy invariants.
- Run full retained M03/M04/M05/M06/M07 and repository gates.
- Do not self-promote M07 PASS/CLOSED.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-010-C001-R04_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
