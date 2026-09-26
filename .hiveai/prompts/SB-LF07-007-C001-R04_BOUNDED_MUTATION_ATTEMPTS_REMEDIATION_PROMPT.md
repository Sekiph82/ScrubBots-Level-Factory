# SB-LF07-007-C001-R04 — Remediation Prompt

Target: `SB-LF07-007`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-007-C001-R03_BOUNDED_MUTATION_ATTEMPTS_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Finish sealing the authentic runner.

Required:
- Accept only the sealed SB-LF07-006 target authority.
- Wrap validator, target selection and provenance construction failures so MutationContractError becomes deterministic AttemptDisposition.ERROR with recorded attempt evidence, never an escaping exception.
- Preserve TARGET_MATCH/ERROR/UNAVAILABLE/INCONCLUSIVE/REJECTED/EXHAUSTED semantics and exact budgets.
- Integrate corrected SB-LF07-009 source lifecycle so every source-linked attempted operation gets a post-check before continuing/returning.
- Add unrelated authentic candidate, forged target, provenance failure, selection failure, all-terminal, exact-limit and no-post-limit tests.
- Do not restore any legacy ChallengeTarget production path.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-007-C001-R04_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
