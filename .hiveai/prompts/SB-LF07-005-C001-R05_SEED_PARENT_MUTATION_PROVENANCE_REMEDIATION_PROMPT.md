# SB-LF07-005-C001-R05 — Remediation Prompt

Target: `SB-LF07-005`

Authoritative R04 re-audit:
`.hiveai/audits/SB-LF07-005-C001-R04_SEED_PARENT_MUTATION_PROVENANCE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-006

Do not reimplement accepted behavior.

Seal provenance through authentic evidence objects, not raw references.

Required:
- Remove or retire public MutationProvenance.seal_authentic(request, result, references) as a production-capable factory.
- Production sealing must accept the exact ValidationEnvelope plus authentic M03/M04/M05 adapters and derive TypedEvidenceReference objects internally.
- Raw caller-provided references/digests must never be sufficient to produce is_authentic_sealed == True.
- If a compatibility factory remains, it must be test/legacy-only and structurally rejected by ProvenanceLedger.
- Add adversarial test: construct three valid-looking refs with stages M03_SOLVER/M04_DIFFICULTY/M05_QA and arbitrary 64-hex digests; prove no package/public path can seal or ledger-record them.
- Preserve deterministic digest, root registration, missing-parent, duplicate-child and cycle guards.

## Publication protocol
- Read original criteria and complete C001/R01/R02/R03/R04 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-005-C001-R05_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md` before product edits.
- Add adversarial tests that specifically fail the R04 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
