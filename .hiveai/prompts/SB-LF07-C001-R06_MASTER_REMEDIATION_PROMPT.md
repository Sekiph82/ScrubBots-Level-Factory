# SB-LF07-C001-R06 — M07 Final Selective Remediation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative R06 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-C001-R06_REMEDIATION_INDEX.md

## Frozen PASS/CLOSED tasks
001,002,003,004,005,006,007,009

Do not reimplement them.

Run only:
`008 -> 010`

Do not start M08.

## Final closure target

There is one remaining product truth gap: the shared mutate-vs-regenerate workload identity is not yet cross-bound to the actual mutation execution seed/config provenance.

SB-LF07-008 must:
- reject generation/workload seed identity that does not agree with the mutation base-seed contract;
- bind parent generation provenance/config when available;
- remain UNAVAILABLE when exact config provenance cannot be proven;
- preserve one genuinely aligned MATCHED fixture;
- preserve same-seed/different-config mismatch, truthful regeneration acceptance availability, solver-workload availability and accounting-unavailable behavior.

SB-LF07-010 must:
- add regression for mutation seed A vs workload/regeneration seed B and prove MATCHED is impossible;
- retain one aligned MATCHED case;
- retain all previously closed provenance/source/safety/accounting/governance/Palette V3 regression gates;
- keep full repository pytest green except accepted capability-gated skips.

## Governance
- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audits under `.hiveai/audits/**`.
- Preserve frozen task behavior/tests.
- No history rewrite, reset, rebase, stash, clean, force-push or provider spend.
- Do not self-promote M07 PASS/CLOSED.

## Required logs
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R06_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R06_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log
Create:
`.hiveai/codex-logs/SB-LF07-C001-R06_MASTER_REMEDIATION_CODEX_LOG.md`

It must include:
- implementation + terminal log SHAs for 008 and 010;
- explicit seed/config cross-binding proof;
- seed-A vs workload-seed-B negative proof;
- valid aligned MATCHED proof;
- final affected M07 and retained gates;
- full repository pytest, compileall, Godot, diff and protected-file results;
- explicit no-self-promotion statement.

Commit/push master log, verify HEAD == origin/main, then STOP.

## Final response format
Return ONLY 3 GitHub URLs, one per line:
1. R06 master log
2. SB-LF07-008 R06 log
3. SB-LF07-010 R06 log
