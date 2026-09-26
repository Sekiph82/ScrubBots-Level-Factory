# SB-LF07-004-C001-R04 — Remediation Prompt

Target: `SB-LF07-004`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-004-C001-R03_RESOLVE_REVALIDATE_EVERY_MUTATION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Seal the production eligibility boundary.

Required:
- Remove legacy synthetic eligibility helpers from the package-root production API: evidence(), revalidate_mutation(), revalidate_mutation_from_typed_receipts(), ProducerEvidenceReceipt and M03/M04/M05 self-asserted receipt types must either move to an explicit tests/legacy fixture namespace or be made structurally unable to yield a production-eligible ValidationEnvelope.
- The only production eligibility constructor/export must be revalidate_mutation_from_authentic_adapters() over actual accepted M03/M04/M05 producer objects.
- Tighten M05 producer authority binding. Reject stale/mismatched QA stage authority instead of accepting any same-repository non-UNAVAILABLE commit.
- Add tests proving package-root production callers cannot obtain ELIGIBLE from free-form EvidenceRecord or caller-created receipts.
- Add stale M05 authority and authentic positive-path tests.
- Correct the R03 implementation SHA evidence: the actual commit is 94d29dd0f94765cc374166398836b80830dcb965, not the mistyped SHA recorded in R03 logs.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-004-C001-R04_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
