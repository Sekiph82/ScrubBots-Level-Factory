# SB-LF07-008-C001 — Mutate vs Regenerate Efficiency Comparison
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-008-C001`, immediately after published SB-LF07-007.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `c8770555a78948b89b11d2f115aee19923d33d5b`.
- Initial status: equal to origin; pre-existing untracked LF04 worktree directories and Godot UID files preserved and not staged.

## Required records and contracts read before edits

- Live `TASKS.md`, M07 master prompt/index, this task prompt and strict criteria.
- `AGENTS.md`, `GOVERNANCE.md`, and accepted SB-LF07-001..007 implementation/log evidence.
- Accepted M07 targeting/budget semantics and existing generator route boundary; no new generator or provider spending is authorized.

This log was created before SB-LF07-008 product implementation and tests.

## Planned implementation boundary

- Provide apples-to-apples comparison records for the same target/policy/seed-config/validation/budget workload.
- Keep mutation and regeneration lineage/counters separate; record deterministic counters and only trusted existing cost evidence.
- Exclude wall-clock/machine telemetry from canonical digest and avoid global superiority claims.

## Chronological implementation and verification

- Reused `EfficiencyWorkload`, `EfficiencyCounters`, `EfficiencyComparison` and `compare_efficiency()` and added `tests/unit/test_sb_lf07_008_efficiency.py` for matched workloads, target/budget mismatch, zero acceptance/inconclusive counts, deterministic counters, trusted/untrusted cost evidence and telemetry exclusion.
- Focused command for M07-001..008 -> `28 passed`.
- Full command: `python -m pytest -q -p no:cacheprovider` -> `1013 passed, 2 skipped` in `321.98s`. Skips remain the pre-existing explicitly capability-gated canonical ScrubBots checkout/bridge skips.
- `python -m compileall -q src tests` -> exit code 0.
- `godot_console.exe --headless --editor --path level_factory --quit` (Godot 4.7.2) -> exit code 0.
- `git diff --check` -> exit code 0. `git diff --exit-code -- TASKS.md` -> exit code 0.
- Canonical comparison digest includes matched workload and deterministic counters only. Wall-clock/machine telemetry and untrusted provider cost do not enter identity, and the report does not declare a globally superior strategy.

## Publication checkpoints

Implementation and terminal log-only publication checkpoints are recorded below. Root `TASKS.md`, prompts, audits, prior logs, and owner-local untracked files remain unchanged.

- Implementation/evidence commit: `983bf1f92c780effe4fe1f491b7f207708abed80` (`Add M07-008 efficiency evidence`).
- Implementation push succeeded; local `HEAD` and `origin/main` were both `983bf1f92c780effe4fe1f491b7f207708abed80` immediately afterward.
- Terminal log-only publication commit is the final SB-LF07-008 checkpoint.
