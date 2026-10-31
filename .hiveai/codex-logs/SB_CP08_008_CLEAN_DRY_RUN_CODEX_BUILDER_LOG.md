# SB-CP08-008 — Clean-Machine Publish Dry Run

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repo `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == 4e36ff0d010033c662d7d8db52afc71acc9bac44`, 0 ahead / 0 behind; queue guard selected `SB-CP08-008`.
- Active owner prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; read CP08 task row, M19 clean dry-run scope, CLI and focused operations tests.
- Current CLI `--dry-run` produces deterministic fail-closed JSON and declares `remote_mutation_performed=false`; local operation files are opt-in with `--operations-dir`. A clean-machine environment requires a new isolated install/workspace, prohibited by the current Desktop-only/no-temp/no-worktree policy. This task will verify the real CLI path in-memory from the canonical checkout and mark the isolated-environment gate NOT_RUN.
- Planned new test calls the CLI without output directory and fails if the evidence writer is invoked; two runs must emit the same report. No file output, provider, R2, CI, scratch, clone/worktree, owner data, Release Apply, GUI, or game repository operation.

## Verification and outcome

- Added `test_plain_dry_run_is_deterministic_and_never_invokes_evidence_writer` to `tests/unit/test_sb_cp08_operations_evidence.py`; it invokes the actual CLI twice without `--operations-dir`, rejects any evidence-writer call, compares exact JSON output, and asserts a blocked/non-complete report with `remote_mutation_performed=false`.
- Exact command: `$oldPythonPath = $env:PYTHONPATH; $env:PYTHONPATH = Join-Path (Get-Location) 'content_pipeline/src'; try { python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py::test_plain_dry_run_is_deterministic_and_never_invokes_evidence_writer tests/unit/test_sb_cp08_operations_evidence.py::test_dry_run_cli_wires_blocked_preflight_into_weekly_summary_without_writing } finally { $env:PYTHONPATH = $oldPythonPath }` — 2 passed in 0.21s.
- `rg -n "import .*cloudflare|from .*cloudflare|requests\\.|httpx\\.|boto3|wrangler|remote_mutation_performed" content_pipeline/src/scrubbots_content_pipeline/cli.py tests/unit/test_sb_cp08_operations_evidence.py` — only the local report's `remote_mutation_performed` field/assertions matched; no provider import/call matched in the CLI module.
- `git diff --check` passed. No provider, remote service, R2, Production, CI/Actions, GUI, Release Apply, owner-data, game-repository, scratch, clone, or worktree operation was performed.
- **NOT RUN:** a genuinely clean-machine installation/workspace, remote Staging/Production reads, and a live R2 dry-run. Current owner rules permit only the canonical Desktop checkout and prohibit TEMP/worktrees/clones/provider contact; in-memory CLI evidence is not equivalent to those external gates.
- Result: the reproducible local path is builder-verified as deterministic, fail-closed, and mutation-free at the CLI boundary. The isolated clean-machine and live-provider requirements remain open, so CP08-008 remains partial (`[~]`). No independent audit or release acceptance is claimed.
- Changed product/test files: `tests/unit/test_sb_cp08_operations_evidence.py` only. No production source change, dependency/license change, secret, or generated cache.
