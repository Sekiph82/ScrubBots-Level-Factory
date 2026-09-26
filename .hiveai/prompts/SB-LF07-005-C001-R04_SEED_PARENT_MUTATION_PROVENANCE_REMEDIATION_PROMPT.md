# SB-LF07-005-C001-R04 — Remediation Prompt

Target: `SB-LF07-005`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-005-C001-R03_SEED_PARENT_MUTATION_PROVENANCE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Seal authentic evidence provenance against caller replacement.

Required:
- Authentic production MutationProvenance must carry a canonical authenticity binding derived from the exact ValidationEnvelope and ordered M03/M04/M05 adapter producer/evidence digests.
- Caller code must not be able to dataclasses.replace or directly construct a production-valid provenance with substituted evidence references.
- ProvenanceLedger must reject unsealed/legacy anonymous evidence provenance when used as production-auditable validated-child provenance.
- Legacy anonymous evidence_digests support may remain only in a clearly separate historical/test compatibility surface.
- Preserve registered-root, exact-parent, duplicate-child and cycle protections.
- Add post-construction evidence-reference tamper, missing-stage, stage-swap, producer-digest drift and ledger rejection tests.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-005-C001-R04_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
