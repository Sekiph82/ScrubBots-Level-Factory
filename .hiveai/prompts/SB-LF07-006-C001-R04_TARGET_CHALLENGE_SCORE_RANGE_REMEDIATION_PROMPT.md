# SB-LF07-006-C001-R04 — Remediation Prompt

Target: `SB-LF07-006`

Authoritative R03 re-audit:
`.hiveai/audits/SB-LF07-006-C001-R03_TARGET_CHALLENGE_SCORE_RANGE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

Do not reimplement accepted 001/002/003 behavior.

Make safety/load/risk/retention authority non-forgeable.

Required:
- Because no accepted repository producer currently supplies load/risk/retention truth, production code must make TRUE values for those required constraints impossible to construct.
- Do not trust public booleans on SafetyConstraintEvidence.
- Introduce an authority-derived/sealed safety evidence construction path. With current repository capability it must resolve to UNAVAILABLE/INCONCLUSIVE.
- select_authentic_target() must validate that safety evidence was produced by that accepted path and reject caller-built/fabricated SafetyConstraintEvidence.
- If a target intentionally requests no unavailable safety constraints, define that explicitly and version it; do not silently reinterpret the original all-gates target.
- Remove R03 tests that forge TRUE safety just to obtain TARGET_MATCH.
- Add forged-safety rejection and truthful-unavailable tests.

## Publication protocol
- Read original criteria and full C001/R01/R02/R03 history before edits.
- Create `.hiveai/codex-logs/SB-LF07-006-C001-R04_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail the R03 implementation.
- Run focused task tests, affected M07, retained M03/M04/M05/M06/Palette V3, full pytest, compileall, Godot headless and git diff --check.
- Prove root TASKS.md and .hiveai/audits/** unchanged.
- Never weaken criteria.
- Commit implementation separately from terminal log publication.
- Do not self-promote PASS/CLOSED.
