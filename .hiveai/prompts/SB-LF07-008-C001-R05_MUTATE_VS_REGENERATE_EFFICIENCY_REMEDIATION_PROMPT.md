# SB-LF07-008-C001-R05 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R04 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R04_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement accepted behavior.

Create one real shared matched-workload identity.

Required:
- Introduce one canonical workload constructor used by both mutation and regeneration paths.
- The shared identity must bind exact GenerationRequest/config identity plus target digest, validation-policy identity and budget digest.
- Do not hash a custom mutation mapping on one side and GenerationRequest.digest() on the other.
- Mutation runner/report must carry or be given the exact accepted GenerationRequest/workload identity needed for comparison; if absent, route is UNAVAILABLE.
- Regeneration route must use the exact same constructor from GenerationResult.request.
- Add one deterministic fixture where mutation and regeneration routes are genuinely MATCHED.
- Same seed with different width/height/mode/style/theme/palette/options must be rejected/unmatched.
- Raw GenerationResult SUCCESS remains produced/inconclusive unless an authentic M03/M04/M05 validation chain bound to that regenerated output is supplied.
- If authenticated regeneration validation is supported, derive accepted/rejected/inconclusive from it. If repository capability is absent, keep acceptance explicitly unavailable/inconclusive.
- Solver workload unavailable remains explicit; accounting remains None per SB-LFX-017.

## Publication protocol
- Read original criteria and complete C001/R01/R02/R03/R04 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R05_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before product edits.
- Add adversarial tests that specifically fail the R04 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
