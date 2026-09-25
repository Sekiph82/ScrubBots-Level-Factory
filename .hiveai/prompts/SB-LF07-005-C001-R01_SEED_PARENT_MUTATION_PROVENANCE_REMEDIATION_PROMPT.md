# SB-LF07-005-C001-R01 — Remediation Prompt

Target: `SB-LF07-005`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Turn provenance into a graph-aware lineage authority.

Required corrections:
- Require every non-root child’s immediate parent to be the known lineage root or an already-recorded node/edge.
- Reject missing-parent insertion, ancestor cycles, A->B->A reconstruction, self-parenting, mixed roots and conflicting duplicate child identities.
- Cross-bind result operator id/version/intent/authority to the exact MutationRequest, not only request digest/parent.
- Replace anonymous evidence digest tuples with typed/stage-labelled evidence identities that can bind authentic M03/M04/M05 producer evidence after SB-LF07-004 remediation.
- Preserve deterministic replay and canonical metadata exclusions.
- Add genuine multi-edge cycle, missing-parent, operator-version drift and evidence-stage swap tests.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-005-C001-R01_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
