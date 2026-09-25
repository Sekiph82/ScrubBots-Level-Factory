# SB-LF07-009-C001-R03 — Remediation Prompt

Target: `SB-LF07-009`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-009-C001-R02_OWNER_SOURCE_ART_NON_MUTATION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Close the orchestration lifecycle and duplicate authority.

Required:
- Remove the legacy duplicate M07 OwnerSourceRecord/OwnerSourceReport/verify_owner_source_immutable production exports and implementation authority; compatibility aliases, if retained, must point to accepted M05 types/functions rather than parallel logic.
- Source-linked production orchestration must own: M05 pre-check -> mutation -> authentic revalidation -> typed targeting -> M05 post-check -> only then TARGET_MATCH/eligible return.
- Do not require a pre-built "after PASS" context before mutation.
- Post-check must run after the actual operation and before success is returned.
- Missing/stale/corrupt source or alias/byte/dimension change must fail closed.
- Add integrated hardening/easing/bounded-target tests that mutate/check real temp source files and prove byte preservation or rejection.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-009-C001-R03_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
