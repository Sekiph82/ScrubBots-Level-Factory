# SB-LF07-C001-R06 — M07 Final Selective Remediation Prompt

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: 2026-09-27T08:54:08+03:00.
- Canonical repository: https://github.com/Sekiph82/ScrubBots-Level-Factory.
- Canonical branch: main.
- Canonical Level Factory root: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator.
- R06 authoritative prompt: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-C001-R06_MASTER_REMEDIATION_PROMPT.md.
- Starting Level Factory SHA after safe fast-forward to live origin/main: 3cf80cdb0219c3ab78e4f7bc55b6d3d62021f054.
- Origin: https://github.com/Sekiph82/ScrubBots-Level-Factory.git.
- Initial tracked worktree was clean. Pre-existing owner/untracked files were preserved and never staged.
- Read TASKS.md, AGENTS.md, GOVERNANCE.md, the live R06 master/index, both R06 task prompts, original criteria, and R05 strict re-audits for 008 and 010.
- Scope executed exactly in order: 008 -> 010. Frozen PASS/CLOSED tasks 001,002,003,004,005,006,007,009 were not reimplemented. M08 was not started.
- TASKS.md and .hiveai/audits/** were not edited or created.

## SB-LF07-008 R06

- Added explicit parent generation provenance binding. Only a validated generation_request_digest supplied directly or through the accepted generation_provenance field is trusted; raw parent payload configuration is never hashed or inferred.
- A supplied GenerationRequest whose seed differs from the mutation base_seed fails closed before mutation attempts and before a workload can be marked available.
- When parent generation provenance exists, the exact supplied GenerationRequest.digest() must match it before the shared canonical workload identity is constructed.
- When parent provenance is absent, mutation route workload remains UNAVAILABLE even if a caller supplies a request; no config-sensitive MATCHED claim is fabricated.
- The shared canonical workload constructor remains the sole constructor for both mutation and regeneration routes.
- Valid aligned MATCHED proof: parent carries the exact digest of GenerationRequest(seed=41, MASK, 20x20); mutation runs with base_seed 41 and the same request; regeneration uses that exact request; both route identities are equal and comparison disposition is MATCHED.
- Seed/config mismatch proof: mutation base seed A=41 with workload/regeneration seed B=42 returns ERROR with no mutation workload; route availability is UNAVAILABLE and comparison disposition is not MATCHED.
- Same-seed parent-bound config mismatch proof: parent digest for seed 41/MASK/20x20 versus supplied seed 41/MASK/21x21 returns ERROR before workload construction.
- Missing parent provenance proof: supplied seed-41 request with no parent digest leaves report.workload absent and route availability UNAVAILABLE.
- Raw regeneration SUCCESS remains produced/inconclusive without authentic M03/M04/M05 validation; solver workload and provider accounting availability remain truthful/unavailable.
- Implementation commit: a5680fb5ea57b82e6e6ce671aed6ff00f39808f5.
- Final task-log publication commit: 763181dd926202397e980755a0bfdff8c93ab8ea.
- Task log: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R06_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md.

## SB-LF07-010 R06

- Rebuilt the M07 regression fixture so the aligned GenerationRequest digest is bound into the actual parent candidate before mutation execution.
- Added regression coverage for seed A versus workload/regeneration seed B, parent-bound config digest mismatch, missing parent provenance unavailability, and the valid aligned MATCHED case.
- Retained forged provenance, source-preservation, safety, truthful accounting, governance, Palette V3, and frozen-task regression coverage.
- Implementation commit: 8fa343dbeea0a1116d8492129d0d8e0d0af5aa3c.
- Final task-log publication commit: 0be7359b3c44fcff443307932248ec348dd6d376.
- Task log: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R06_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md.

## Verification evidence

- Final affected M07 004–010 suite: 33 passed.
- Retained M03/M04/M05/M06/Palette V3 gate: 296 passed, 2 skipped; both skips were accepted canonical ScrubBots capability gates.
- Full repository pytest: 1039 passed, 2 skipped in 421.27s; both skips were accepted canonical ScrubBots capability gates.
- python -m compileall -q src tests: passed.
- godot_console.exe --headless --path level_factory --editor --quit: passed on Godot 4.7.2.
- git diff --check: passed.
- Protected-file proof git diff --name-only -- TASKS.md .hiveai/audits: returned no paths.
- Frozen production behavior remained unchanged; frozen-task and retained gates remained green. No TASKS.md or audit state was advanced by this builder.
- Final pre-master Level Factory SHA: 0be7359b3c44fcff443307932248ec348dd6d376, equal to origin/main.

## Builder boundary

- No task or M07 status was self-promoted to PASS/CLOSED. This is builder evidence only and is handed to ChatGPT for independent final re-audit.
- No history rewrite, reset, rebase, stash, clean, force-push, destructive checkout, provider spend, runtime network dependency, synthetic acceptance, or proxy difficulty truth was introduced.
