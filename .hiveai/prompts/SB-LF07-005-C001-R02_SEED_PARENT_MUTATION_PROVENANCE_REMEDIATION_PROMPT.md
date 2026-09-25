# SB-LF07-005-C001-R02 — Remediation Prompt

Target: `SB-LF07-005`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-005-C001-R01_SEED_PARENT_MUTATION_PROVENANCE_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_AUDIT_CRITERIA.md`

Close remaining graph/evidence provenance findings.

Required:
- Introduce explicit lineage-root registration/identity. First mutation edge must bind the registered root exactly.
- Every later edge must reference an already-recorded exact parent.
- Reject forged root-like parent, missing parent, self-parent, A->B->A/multi-edge cycle, mixed root and duplicate conflict.
- Replace anonymous evidence_digests tuple with typed/stage-labelled evidence references for M03/M04/M05 authentic receipts.
- Preserve exact request/operator/version/intent/authority/seed/pre/post binding.
- Add stage-swap, duplicate-stage, cycle and forged-root tests.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-005-C001-R02_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
