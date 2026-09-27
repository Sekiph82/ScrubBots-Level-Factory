# SB-LF07-007-C001-R05 — Remediation Prompt

Target: `SB-LF07-007`

Authoritative R04 re-audit:
`.hiveai/audits/SB-LF07-007-C001-R04_BOUNDED_MUTATION_ATTEMPTS_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement accepted behavior.

Close the source-linked entry boundary while preserving bounded semantics.

Required:
- If parent.source_art_sha256 is not None, source_context is mandatory. Missing context => deterministic ERROR before request_factory/engine/validator is called.
- Cross-bind source_context.record.source_sha256 to parent.source_art_sha256 before any operation. Wrong-source context => ERROR before calls.
- Keep per-attempt re-establish pre-check + finally post-check.
- Preserve sealed target requirement, exception-to-ERROR conversion, all terminal precedence and exact budget/no-post-limit behavior.
- Add tests proving zero request/operator/validator calls on missing/wrong source context.
- Add applied, non-applied, validator-error and request-error source-linked cases.

## Publication protocol
- Read original criteria and complete C001/R01/R02/R03/R04 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-007-C001-R05_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md` before product edits.
- Add adversarial tests that specifically fail the R04 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
