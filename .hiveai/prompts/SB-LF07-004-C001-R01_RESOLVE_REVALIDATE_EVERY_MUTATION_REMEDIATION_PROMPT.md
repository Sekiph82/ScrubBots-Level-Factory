# SB-LF07-004-C001-R01 — Remediation Prompt

Target: `SB-LF07-004`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Close the core M07 trust boundary.

Required corrections:
- Production eligibility must not accept generic caller-minted evidence labels.
- Replace the acceptance use of evidence(stage, disposition, payload) with typed adapters/providers over the already accepted M03 solver evidence, M04 DifficultyAnalysis/ChallengeScore result, and M05 Unified QA result/report contracts.
- Each adapter must verify producer schema/version/authority, exact child LevelData/state/source/request/operator/current-main identities and the authentic producer evidence digest.
- Caller-created synthetic fixtures may exist only in tests and must not satisfy the production eligibility path.
- Missing provider/capability => UNAVAILABLE; M03 inconclusive remains INCONCLUSIVE; proven unsolvable remains REJECTED.
- Add tests proving a forged SOLVED/AVAILABLE/PASS triple cannot create ELIGIBLE, even when its internal hashes are self-consistent.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-004-C001-R01_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
