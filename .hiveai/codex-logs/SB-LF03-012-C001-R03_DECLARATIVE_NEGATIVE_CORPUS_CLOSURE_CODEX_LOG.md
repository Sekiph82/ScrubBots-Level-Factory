# SB-LF03-012-C001-R03 — Declarative Negative Corpus Closure

Document role: CODEX BUILDER LOG

## Chronology

- Start: 2026-09-23 Europe/Istanbul.
- Repository and branch: `Sekiph82/ScrubBots-Level-Factory`, `main`.
- Starting HEAD after safe fast-forward: `804c6e8`; `origin/main` matched; initial status contained only preserved untracked `level_factory/**/*.uid` files.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the R03 master prompt, R03 index, R02 re-audit, and exact task prompt were read before implementation. `TASKS.md` is untouched.
- This task is ordered after R03-009 and R03-011. The canonical bridge and timeout changes will be tested as dependencies; the owner ScrubBots checkout remains read-only.

## Work log

Implementation and verification entries will be appended chronologically.

- Read the R03 negative-corpus prompt, R02 audit, existing fixture loader, and retained LF03 contract tests. Replaced the ID-only `r01_negative_fixture_ids` list with eight versioned declarative objects, each `production=false`, payload, expected outcome, and canonical payload SHA-256.
- Added executable corpus coverage for wrong query binding, wrong state-key binding, transition authority drift, enumeration binding, frontier peak, replay identity tamper, max-visited stop, and timeout-before-result. The test recomputes every checksum and drives each payload through the relevant contract.
- Updated the canonical bridge fixture to carry exact LevelData V1 source bytes and the cryptographic source hash; real repeated legal_moves/apply_placement/solve calls now use the source-bound request.
- Focused/affected command: `python -m pytest -q` over R03 009/011/012, retained LF03, LF00, and LF06 tests -> `95 passed, 1 warning`; `python -m compileall -q src tests` passed.
- Godot headless editor boot: `godot_console.exe --headless --editor --path level_factory --quit` -> exit code 0. `git diff --check` passed and `git diff --exit-code -- TASKS.md` passed.
