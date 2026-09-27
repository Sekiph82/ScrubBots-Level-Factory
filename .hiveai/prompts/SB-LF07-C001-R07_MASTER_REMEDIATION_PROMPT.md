# SB-LF07-C001-R07 — M07 Final Provenance-Seal Remediation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative R07 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-C001-R07_REMEDIATION_INDEX.md

## Frozen PASS/CLOSED
SB-LF07-001,002,003,004,005,006,007,009

Do not reimplement them.

Run only:
`SB-LF07-008 -> SB-LF07-010`

Do not start M08.

## Final closure target

The only remaining M07 gap is that a parent candidate can self-assert generation provenance by carrying an arbitrary syntactically valid GenerationRequest SHA.

R07 must replace that with producer-derived sealed provenance:
- derive parent generation provenance from an actual accepted GenerationResult/GenerationRequest path;
- bind exact GenerationRequest digest, GenerationResult digest, generator id/version/mode, seed/config identity, and exact parent candidate identity;
- raw payload SHA strings must not establish workload availability;
- missing sealed provenance => UNAVAILABLE;
- sealed provenance for another parent/result/request => reject;
- one actual accepted sealed aligned case => MATCHED;
- forged raw digest => UNAVAILABLE/non-MATCHED;
- retain R06 seed/config mismatch protections and all previously closed M07 invariants.

## Governance

- Never edit root `TASKS.md`.
- Never edit/create ChatGPT audits under `.hiveai/audits/**`.
- Preserve all frozen task behavior/tests.
- No history rewrite/reset/rebase/stash/clean/force-push/destructive checkout.
- No provider/network spend merely for tests.
- Do not self-promote M07 PASS/CLOSED.

## Required logs

- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R07_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R07_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md

## Final master log

Create:
`.hiveai/codex-logs/SB-LF07-C001-R07_MASTER_REMEDIATION_CODEX_LOG.md`

It must include:
- implementation + terminal-log SHAs for 008 and 010;
- exact sealed generation-provenance construction proof;
- forged raw payload digest rejection;
- wrong-parent/wrong-result provenance rejection;
- one real sealed MATCHED case;
- retained seed/config mismatch proof;
- full affected M07 and retained M03/M04/M05/M06/Palette V3 gates;
- full repository pytest, compileall, Godot, diff and protected-file results;
- explicit no-self-promotion statement.

Commit/push master log, verify HEAD == origin/main, then STOP.

## Final response format

Return ONLY 3 GitHub URLs, one per line:
1. R07 master log
2. SB-LF07-008 R07 log
3. SB-LF07-010 R07 log
