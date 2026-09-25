# SB-LF07-009-C001-R01 — Remediation Prompt

Target: `SB-LF07-009`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Integrate the accepted M05 OWNER_UPLOAD/source-library authority into every M07 path.

Required corrections:
- Remove or bridge the duplicate M07 OwnerSourceRecord; reuse the accepted M05 owner-source record/identity contract as the sole source truth.
- Source-linked mutation orchestration must require pre/post accepted source verification. Missing/stale/corrupt source evidence must fail closed before eligibility/targeting.
- MutationEngine/targeting/bounded orchestration must not silently bypass source preservation when a candidate is source-linked.
- Derived paths/artifacts must use the accepted M05 separation/alias rules.
- Prove hardening/easing/targeting cannot execute to eligible success with stale/missing source guard.
- Add integrated pipeline tests, not only standalone verifier tests.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-009-C001-R01_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
