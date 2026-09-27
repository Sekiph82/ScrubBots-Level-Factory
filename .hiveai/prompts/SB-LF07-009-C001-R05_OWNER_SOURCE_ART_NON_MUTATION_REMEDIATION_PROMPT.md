# SB-LF07-009-C001-R05 — Remediation Prompt

Target: `SB-LF07-009`

Authoritative R04 re-audit:
`.hiveai/audits/SB-LF07-009-C001-R04_OWNER_SOURCE_ART_NON_MUTATION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement accepted behavior.

Make M05 source identity mandatory and exact.

Required:
- Any parent with non-null source_art_sha256 is source-linked and must require SourceLinkedMutationContext.
- Before the first operation, require context.record.source_sha256 == parent.source_art_sha256; mismatched record fails closed.
- For each attempt: establish accepted M05 pre-check immediately before work; post-check in finally before any continue/return.
- Source mutation must override underlying INAPPLICABLE/NO_CHANGE/UNAVAILABLE/ERROR/exception outcome to terminal ERROR.
- Add tests for omitted context, wrong-source record, request-factory mutation+raise, engine INAPPLICABLE/error after source mutation, validator mutation+raise, and repeated attempts.
- Keep only accepted M05 OwnerSourceRecord/SourcePreservationReport/verifier authority.

## Publication protocol
- Read original criteria and complete C001/R01/R02/R03/R04 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-009-C001-R05_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md` before product edits.
- Add adversarial tests that specifically fail the R04 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
