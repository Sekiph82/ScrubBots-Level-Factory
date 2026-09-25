# SB-LF07-007-C001-R03 — Remediation Prompt

Target: `SB-LF07-007`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-007-C001-R02_BOUNDED_MUTATION_ATTEMPTS_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Finish the authentic runner.

Required:
- Consume the corrected SB-LF07-004 authentic validation chain and SB-LF07-006 typed target contract directly.
- Every applied attempt must emit SB-LF07-005 typed M03/M04/M05 provenance references automatically.
- Every non-applied attempt must retain exact attempt provenance.
- Add runner-level tests for TARGET_MATCH, ERROR, UNAVAILABLE, INCONCLUSIVE, REJECTED and genuine EXHAUSTED; prove deterministic precedence and replay.
- Prove exact limit and no post-limit request/operator/validator calls.
- Integrate source-linked lifecycle from corrected SB-LF07-009 so source-linked success cannot bypass post-operation verification.
- Remove dependency on legacy ChallengeTarget/free-form validator behavior in the production runner.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-007-C001-R03_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
