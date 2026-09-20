# SB-LFX-011-C001 — Factory Studio Exact Reproduce Action

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T18:05:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `f5e10b019b55f4ca443c206fd25c2ac9f60c3b58`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-011 C001. Root `TASKS.md` is read-only. Read product contract, SB-LFX-011 prompt/criteria, accepted Factory Core Generate/Reproduce contracts, Candidate/Readiness code, and prior logs.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added identity-bound reproducibility capability classification and a real Exact Reproduce surface. Deterministic recorded Generator bundles are classified exact-capable; unsupported/manual paths remain unavailable or source-retrievable-only.
- The action reads recorded candidate metadata and does not use current draft/preset values or replace the original bundle.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_011_reproduce.py tests/unit/test_sb_lfx_010_readiness.py` — **2 passed, 1 warning**.
- Godot headless Studio boot — **PASS**.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.

## Changed files

`src/scrubbots_pixel_factory/studio_extensions.py`, `level_factory/scripts/factory_core_launcher.py`, `level_factory/scripts/factory_studio_reproduce.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_navigation.gd`, `tests/unit/test_sb_lfx_011_reproduce.py`, and this builder log.

## Publication

- Final implementation SHA: `bec72af1b3545a44d74783711b1e480c4106b168`.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
