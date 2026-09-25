# SB-LF07-004-C001-R03 — Remediation Prompt

Target: `SB-LF07-004`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-004-C001-R02_RESOLVE_REVALIDATE_EVERY_MUTATION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Close the exact producer-to-child identity gap.

Required:
- M03: verify SolverEvidenceReport native provenance fields against the mutation child/request/source/authority/state. Missing native provenance is UNAVAILABLE/INCONCLUSIVE; do not stamp the mutation identity onto an unrelated report.
- M04: verify DifficultyAnalysis.level_source_sha256, solver_evidence identity, authority, challenge-score source metrics digest/policy and exact child identity.
- M05: verify UnifiedQAReport.level_data identity/source/level-data digest against the mutated child and exact accepted LevelData bytes/identity.
- Adapter records must be derived only after these native identity checks.
- Production ELIGIBLE must be impossible from authentic-but-unrelated producer objects.
- Add a complete positive authentic chain test using actual accepted M03/M04/M05 producer objects bound to one mutation, plus unrelated-object/cross-child/stale-source negatives.
- Legacy synthetic revalidate paths remain fixture-only and may not be reachable from production orchestration.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-004-C001-R03_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
