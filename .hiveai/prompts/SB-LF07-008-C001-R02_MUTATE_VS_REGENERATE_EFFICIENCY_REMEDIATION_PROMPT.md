# SB-LF07-008-C001-R02 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R01 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R01_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original strict criteria remain authoritative:
`.hiveai/audit-criteria/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_AUDIT_CRITERIA.md`

Replace caller-made route counters with evidence-derived route adapters.

Required:
- Mutation route input must be constructed from a real M07 AttemptReport and derive all counters from its attempts/validation outcomes.
- Regeneration route input must be constructed from one specific already accepted generator path/result type in the repository. Identify and bind exact route id/version/config/seed/validation/budget/result identities.
- Derive produced/accepted/rejected/inconclusive/solver-workload counts from the actual results.
- Workload identity must separately bind target, seed/config, validation policy and budget, not collapse one digest into all four fields.
- Provider/accounting data may enter only through the actual accepted SB-LFX-017 accounting evidence type/digest.
- Keep telemetry noncanonical and do not rank globally.
- Add forged counter/accounting, mismatched workload and real-route adapter tests.

## Required publication protocol
- Read original criteria, C001 audit, R01 prompt/log and R01 strict re-audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-008-C001-R02_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md` before product edits.
- Close every remaining R01 finding with forward changes only.
- Add adversarial tests that fail the R01 implementation.
- Run focused R02 tests plus all affected M07 tests and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check and prove TASKS.md unchanged.
- Do not edit root TASKS.md or ChatGPT audits.
- Commit implementation separately, then terminal log-only publication separately.
- Resolve current Scrubbots main freshly inside every authority-dependent task.
- Do not self-promote PASS/CLOSED.
