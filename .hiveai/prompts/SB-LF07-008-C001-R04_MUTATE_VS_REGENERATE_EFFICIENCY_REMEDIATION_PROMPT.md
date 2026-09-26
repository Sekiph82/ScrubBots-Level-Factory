# SB-LF07-008-C001-R04 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R03_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Make the comparison truly apples-to-apples.

Required:
- Define a canonical matched-workload identity containing the complete relevant GenerationRequest/config identity: seed, difficulty, width/height, generator mode, style/theme, palette subset, generator options plus target policy/range, validation policy and declared budget.
- Mutation path must bind an equivalent starting/config identity. If equivalent config cannot be derived, comparison is UNAVAILABLE rather than guessed.
- Regeneration SUCCESS is not accepted/eligible. Run the regenerated candidate through the same accepted M03/M04/M05 validation chain before incrementing accepted.
- Record regeneration rejection/inconclusive/unavailable outcomes from that real validation.
- Solver/evidence workload must be derived when available or explicitly unavailable, not silently zero.
- Retain accepted SB-LFX-017 accounting truth: cost/credits remain unavailable/None.
- Reject same-seed but different width/height/mode/options as unmatched.
- Compare only sealed SB-LF07-006 target authority.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R04_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
