# SB-LF07-008-C001-R03 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R02_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Close matched workload and accounting authority.

Required:
- Derive mutation workload identity from actual target, seed/config, validation policy and attempt budget used by the AttemptReport.
- Derive regeneration workload identity from actual GenerationRequest/GenerationResult plus the same target/validation/budget contract; reject comparisons where these do not match.
- Do not accept arbitrary caller config/workload digests as authority.
- Derive all counters truthfully, including inconclusive/unavailable where applicable.
- Bind exact generator id/version/request digest/seed/dimensions/config.
- Respect accepted SB-LFX-017-C001-R02 truth: there is currently no authoritative provider/job accounting producer. Cost/credits must therefore be NOT AVAILABLE/None and caller-created CostUsageRecord must not establish trusted financial evidence.
- Add forged workload/config/accounting and matched actual-route tests.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R03_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
