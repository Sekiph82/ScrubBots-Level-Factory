# SB-LFX-014-C001 — Factory Studio Multi-File Pixel Art Batch Import

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T19:05:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `861ac9e9fd87d19275207ad1e7401dd0c80e8abd`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-014 C001. Root `TASKS.md` is read-only. Read product contract, SB-LFX-014 prompt/criteria, accepted LFX-002 import, and prior logs.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added versioned per-file batch-run evidence over the canonical LFX-002 importer. Each item records its own display entry, source identity or exact error, and disposition; batch metadata never copies source bytes.
- Added the real Batch Import Studio surface and navigation entry with explicit per-file provenance/partial-success wording.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_014_batch_import.py tests/unit/test_sb_lfx_013_failures.py` — **2 passed, 1 warning**.
- Godot headless Studio boot — **PASS**.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.

## Changed files

`level_factory/scripts/factory_core_launcher.py`, `level_factory/scripts/factory_studio_batch_import.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_navigation.gd`, `tests/unit/test_sb_lfx_014_batch_import.py`, and this builder log.

## Publication

- Final implementation SHA: pending commit.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
