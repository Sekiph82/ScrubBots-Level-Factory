# SB-LF07-010-C001-R07 — Remediation Prompt

Target: `SB-LF07-010`

Authoritative R06 re-audit:
`.hiveai/audits/SB-LF07-010-C001-R06_DETERMINISTIC_MUTATION_REGRESSION_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED:
SB-LF07-001,002,003,004,005,006,007,009

## Final regression closure

After SB-LF07-008 R07:
- build the positive MATCHED regression only through the sealed GenerationResult-derived parent provenance path;
- prove a forged raw payload `generation_request_digest` cannot establish workload availability or MATCHED;
- prove binding for another parent is rejected;
- retain seed mismatch, config mismatch and missing-provenance regressions;
- retain all previously closed provenance/source/safety/accounting/governance/Palette V3 regressions;
- full repository pytest must remain green except accepted capability-gated skips;
- compileall, Godot headless, diff and protected-file checks must pass.

Do not edit TASKS.md or ChatGPT audits. Do not self-promote M07 closed.
