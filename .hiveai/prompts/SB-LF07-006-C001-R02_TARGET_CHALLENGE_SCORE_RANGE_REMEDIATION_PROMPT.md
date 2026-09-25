# SB-LF07-006-C001-R02 — Remediation Prompt

Target: `SB-LF07-006`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-006-C001-R01_TARGET_CHALLENGE_SCORE_RANGE_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_AUDIT_CRITERIA.md`

Replace the legacy production targeting path with the typed authentic path.

Required:
- Production selection must consume TypedChallengeTarget and authentic SB-LF07-004 M04/M05 adapter evidence.
- Remove free-form policy_version/required_constraints payload authority from production targeting.
- Policy digest/version and Challenge Score must be derived from accepted M04 evidence.
- Load/risk/retention constraints must be derived from a real accepted typed producer/evidence contract, not arbitrary booleans/digests.
- Missing safety evidence => INCONCLUSIVE/UNAVAILABLE.
- Integrate typed targeting into bounded mutation orchestration.
- Preserve deterministic tie-breaking and no size/color/difficulty proxies.
- Add forged policy/safety/digest and authentic selection tests.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-006-C001-R02_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
