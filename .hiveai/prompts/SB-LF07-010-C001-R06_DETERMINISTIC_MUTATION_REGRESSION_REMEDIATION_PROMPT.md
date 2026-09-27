# SB-LF07-010-C001-R06 — Remediation Prompt

Target: `SB-LF07-010`

Authoritative R05 re-audit:
`.hiveai/audits/SB-LF07-010-C001-R05_DETERMINISTIC_MUTATION_REGRESSION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED tasks:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003
- SB-LF07-004
- SB-LF07-005
- SB-LF07-006
- SB-LF07-007
- SB-LF07-009

Do not reimplement accepted behavior.

## Remaining R06 closure

After SB-LF07-008 R06 is implemented:
- Add regression proving mutation base seed A cannot be compared as MATCHED against a workload/regeneration GenerationRequest with seed B.
- If parent generation provenance/config identity exists, add exact digest mismatch rejection.
- Keep one valid actual MATCHED case using genuinely aligned mutation workload identity.
- Preserve all previously closed provenance/source/safety/accounting/governance/Palette V3 regressions.
- Full repository pytest must remain green except accepted capability-gated skips.
- Run compileall, Godot headless, diff and protected-file checks.
- Do not edit TASKS.md or ChatGPT audits.
- Do not self-promote M07 closed.

## Publication protocol
- Create `.hiveai/codex-logs/SB-LF07-010-C001-R06_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md` before edits.
- Commit implementation separately from terminal-log publication.
