# SB-LF07-006-C001-R03 — Remediation Prompt

Target: `SB-LF07-006`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-006-C001-R02_TARGET_CHALLENGE_SCORE_RANGE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Close load/risk/retention truth.

Required:
- Determine whether accepted repository contracts currently provide authoritative load, risk and retention evidence.
- If yes, adapt those exact producer objects and bind their digests/policy identities.
- If no authoritative producer exists for any requested constraint, mark that constraint UNAVAILABLE/INCONCLUSIVE. Never synthesize TRUE from UnifiedQAReport ACCEPT.
- Target policy identity must be the stable accepted M04 Challenge Score policy identity/version, not a candidate-specific result digest.
- Candidate Challenge Score remains derived from authentic M04 evidence.
- MATCH requires in-range score plus every requested authoritative constraint PASS.
- Add explicit no-authority tests proving load/risk/retention requests cannot match when evidence is unavailable.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-006-C001-R03_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
