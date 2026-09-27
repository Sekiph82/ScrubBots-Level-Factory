# SB-LF07-008-C001-R06 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R05 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R05_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-005
- SB-LF07-006
- SB-LF07-007
- SB-LF07-009

Do not reimplement accepted behavior.

## Remaining R06 closure

Bind the shared workload identity to the actual mutation execution, not merely a caller-supplied GenerationRequest.

Required:
- `generation_request.seed` must agree with the mutation run's `base_seed` contract. A different seed must fail closed before a MATCHED comparison can be produced.
- If the parent candidate carries canonical generation provenance/config identity, require the supplied GenerationRequest digest to match it exactly.
- If exact parent generation config provenance is unavailable, do not infer it. The mutation route may remain UNAVAILABLE for config-sensitive matched comparison rather than fabricating MATCHED.
- The canonical shared workload identity must still be used on both routes.
- Add an adversarial test: mutation executes with seed A, caller supplies workload/regeneration GenerationRequest with seed B, and comparison cannot be MATCHED.
- Add same-seed but parent-bound config-digest mismatch coverage where parent provenance is available.
- Preserve raw regeneration SUCCESS => produced/inconclusive without authentic validation.
- Preserve accounting/solver-workload unavailable truth.
- Keep all accepted 008 R05 behavior.

## Publication protocol
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R06_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before edits.
- Run focused 008/010 tests plus affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and protected-file no-diff proof.
- Do not edit TASKS.md or .hiveai/audits/**.
- Commit implementation separately from terminal-log publication.
- Do not self-promote PASS/CLOSED.
