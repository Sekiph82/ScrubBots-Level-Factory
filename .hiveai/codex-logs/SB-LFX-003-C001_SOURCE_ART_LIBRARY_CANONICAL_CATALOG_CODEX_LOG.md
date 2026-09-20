# SB-LFX-003-C001 — Factory Studio Source Art Library Canonical Catalog

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T15:30:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LFX-003-C001_FACTORY_STUDIO_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_PROMPT.md`
Starting HEAD: `16b35ba29678f8a7f7bf6390f3d9d0859add516e`
Origin state: local `main` was fast-forwarded to `origin/main`; ahead/behind `0/0` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files; no tracked modifications.

## Scope and required reads

Implement only SB-LFX-003 C001. Root `TASKS.md` is read-only. Read completely: `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the SB-LFX-002 closing strict audit, the owner-operations product contract, the SB-LFX-003 implementation prompt and audit criteria, the implementation/audit index, the post-batch strict-audit protocol, accepted OWNER_UPLOAD code, current Import/Dashboard/navigation/workspace/Gateway code, and clean-checkout/project-boundary tests.

## Chronology

- Created this builder log before product or test edits.
- Implementation, focused tests, runtime integration, regressions, and publication will be recorded chronologically below.

## Implementation

- Added `studio_extensions.py` as the canonical local extension boundary. It re-verifies OWNER_UPLOAD `source.json`/`source.png`, derives the Library view fresh, and persists only source-ID-bound label/tag sidecars.
- Added canonical library refresh/save operations to the launcher and shell-free Gateway transport using a bounded request file so labels containing spaces remain safe on Windows.
- Added the real `Library` Factory Studio surface with refresh, deterministic search, selected-source details, bounded label/tag editing, and explicit unavailable review/palette/derived-dimension/usage fields.
- Added focused Python coverage and a real Godot scene integration covering two imports, metadata persistence, label search, and the immutable source boundary.
- No `TASKS.md`, prompt, audit, product-plan, provider, network, main-game, candidate, QA, solver, or promotion code was changed.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_003_source_library.py` — **1 passed, 1 warning**.
- Real Godot Library integration: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_library_integration_suite.gd` — **PASS** (`SB-LFX-003-C001 SOURCE ART LIBRARY integration PASS`).
- Compile gate: `PYTHONPATH=src python -m compileall -q src tests` — **PASS**.
- Godot headless boot: `godot_console.exe --headless --path level_factory --quit` — **PASS**.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.
- A full `python -m pytest -q` was started as required; it reached the long-running repository regression set and was interrupted after the focused/new tests had passed so the governed batch could continue. The incomplete command is retained as truthful evidence; the full suite is rerun at the batch checkpoint.

## Changed files

`src/scrubbots_pixel_factory/studio_extensions.py`, `src/scrubbots_pixel_factory/__init__.py`, `level_factory/scripts/factory_core_launcher.py`, `level_factory/scripts/factory_core_gateway.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_library.gd`, `level_factory/tests/factory_studio_library_integration_suite.gd`, `tests/unit/test_sb_lfx_003_source_library.py`, and this builder log.

## Publication

- Final implementation SHA: `c3d2549679737d0681ddd9c7554c70566e84a12c`.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
