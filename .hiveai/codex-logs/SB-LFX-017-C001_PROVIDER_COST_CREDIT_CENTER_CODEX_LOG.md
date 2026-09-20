# SB-LFX-017-C001 — Factory Studio Provider Cost / Credit Center

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T20:05:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `1bbf65bcb33fc52593e8652527c27efc93a8ae39`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-017 C001. Root `TASKS.md` is read-only. Read product contract, SB-LFX-017 prompt/criteria, existing provider execution/evidence contracts, and prior logs. No provider/network/credit calls are authorized.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added the local-only `factory_studio_cost.gd` surface and wired it into the Studio workspace/navigation.
- Added provider-cost accounting through the existing offline `studio-extension` transport, with explicit provider, model, operation, unit, credit, and total-cost fields.
- Added focused regression coverage for deterministic credit/cost totals and zero-cost local operations.
- No provider, network, telemetry, API-key, or runtime HTTP dependency was introduced.

## Verification and publication

- Focused tests: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_017_cost_center.py tests/unit/test_sb_lfx_016_similarity.py` — 2 passed, 1 warning.
- Headless Godot boot: `godot_console.exe --headless --path level_factory --quit` — exit 0.
- Python bytecode check: `PYTHONPATH=src python -m compileall -q src tests` — exit 0.
- `git diff --check` passed; root `TASKS.md` remained unchanged.
- Implementation commit: `2999d941098140fd068b0f8df96e777b80a238a6`.
- Task-final log-only commit and final equality checkpoint follow after this log update.
