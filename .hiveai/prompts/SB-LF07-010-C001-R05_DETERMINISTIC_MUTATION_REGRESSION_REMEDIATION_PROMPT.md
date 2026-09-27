# SB-LF07-010-C001-R05 — Remediation Prompt

Target: `SB-LF07-010`

Authoritative R04 re-audit:
`.hiveai/audits/SB-LF07-010-C001-R04_DETERMINISTIC_MUTATION_REGRESSION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement accepted behavior.

Close the M07 milestone regression and governance gate.

Required:
- Rebuild closure around final R05 005/007/008/009 behavior.
- Prove three-ref forged provenance cannot become sealed/ledger-valid.
- Prove source-linked parent without exact context fails before any operation.
- Prove wrong-source context fails before operation.
- Prove source post-check catches mutation on applied, non-applied and exception paths.
- Prove an actual MATCHED mutate-vs-regenerate workload using the shared canonical workload identity; prove same-seed/different-config mismatch.
- Keep truthful regeneration validation/accounting availability semantics.
- Fix tests/unit/test_sb_lf00_007_governance_authority.py structurally: it must validate that Current Task agrees with the unique [~] row and that status/actor fields are internally coherent, rather than hard-coding a transient sprint/task/status such as SB-LF07-001/R03. Do not edit TASKS.md to satisfy the test.
- Full repository pytest must be green except accepted capability skips.
- Run compileall, Godot headless, diff and protected-file checks.
- Preserve PASS/CLOSED 001,002,003,004,006 and Palette V3/no-proxy invariants.
- Do not self-promote M07 closed.

## Publication protocol
- Read original criteria and complete C001/R01/R02/R03/R04 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-010-C001-R05_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md` before product edits.
- Add adversarial tests that specifically fail the R04 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
