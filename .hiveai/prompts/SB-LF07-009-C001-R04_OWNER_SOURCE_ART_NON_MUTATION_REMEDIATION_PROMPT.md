# SB-LF07-009-C001-R04 — Remediation Prompt

Target: `SB-LF07-009`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-009-C001-R03_OWNER_SOURCE_ART_NON_MUTATION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Make source preservation cover every source-linked operation path.

Required:
- For every source-linked attempt, perform accepted M05 pre-check immediately before the attempted operation and accepted M05 post-check in a finally-style path before any continue/return/raised terminal is finalized.
- Post-check must run after non-applied outcomes (NO_CHANGE/INAPPLICABLE/UNAVAILABLE/ERROR), validator failures, target-selection failures and provenance failures as well as successful applied attempts.
- If source changed, final outcome must fail closed as ERROR regardless of the underlying mutation outcome.
- Re-establish/verify pre-check for each attempt in multi-attempt runs rather than relying on one stale initial snapshot.
- Preserve direct aliases to accepted M05 source types only; no parallel M07 source authority.
- Add adversarial tests where source bytes are mutated then operator returns INAPPLICABLE/ERROR or validator raises.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-009-C001-R04_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
