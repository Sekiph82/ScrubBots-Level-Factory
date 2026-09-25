# SB-LF07-004-C001-R02 — Remediation Prompt

Target: `SB-LF07-004`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-004-C001-R01_RESOLVE_REVALIDATE_EVERY_MUTATION_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_AUDIT_CRITERIA.md`

Close the production trust boundary using actual accepted producer types.

Required:
- Delete/retire self-asserted ProducerEvidenceReceipt as a production acceptance authority.
- Implement adapters from the repository's actual accepted M03 SolverEvidenceReport / authoritative solver receipt chain, actual accepted M04 DifficultyAnalysis/ChallengeScore evidence, and actual M05 Unified QA/report result types.
- Derive producer schema/version/digest/authority from those objects; callers must not supply arbitrary producer digests.
- Bind exact mutated child LevelData/state/source/request/operator/current-main identities.
- The public production eligibility function must accept only these authentic adapter outputs.
- Free-form EvidenceRecord and synthetic fixtures may never yield production ELIGIBLE.
- Legacy revalidate_mutation may remain historical/test-only but must be clearly non-production and unreachable from M07 production orchestration.
- Add forged wrapper, forged digest, wrong producer object, stale child and unavailable capability tests.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-004-C001-R02_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
