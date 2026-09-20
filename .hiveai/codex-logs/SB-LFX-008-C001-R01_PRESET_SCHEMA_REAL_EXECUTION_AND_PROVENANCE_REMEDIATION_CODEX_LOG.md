# SB-LFX-008-C001-R01 — Preset Schema + Real Execution + Provenance Remediation

Document role: CODEX BUILDER LOG

## Start and process note

- Starting timestamp: 2026-09-20 (Europe/Istanbul; exact command timestamp will be recorded at finalization).
- Canonical repository/branch: `Sekiph82/ScrubBots-Level-Factory` / `main`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Authoritative master prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LFX-004-017-C001-R01_MASTER_REMEDIATION_PROMPT.md`.
- Task R01 prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LFX-008-C001-R01_PRESET_SCHEMA_REAL_EXECUTION_AND_PROVENANCE_REMEDIATION_PROMPT.md`.
- Start HEAD before SB-LFX-008 implementation: `b3696cb85883774253b7229746f87399c86e4bd6`; `origin/main` matched.
- Initial tracked status: clean; ten pre-existing untracked Godot `.uid` files remain preserved and unstaged.
- Process correction: the required builder-log creation was accidentally omitted before the first SB-LFX-008 product edits. This log is created immediately upon detection and records the chronology truthfully; no prior command or edit is being rewritten.

## Read and findings

- Read root `TASKS.md`, governance, remediation index, SB-LFX-008 original prompt and criteria, strict audit, and exact R01 prompt from canonical `main`.
- Audited findings: MAJOR-001 preset application was preview-only; MAJOR-002 settings were not schema-complete; MAJOR-003 real lifecycle/provenance integration was absent.

## Scope

Restrict presets to validated canonical Generate requests, execute Apply through canonical offline generation, persist expanded request provenance independent of preset lifetime, and add real lifecycle integration. No provider/network work, no LFX-009+ behavior, and no `TASKS.md` edit.

Further commands, implementation, tests, failures/corrections, publication SHAs and final topology will be appended chronologically.

## Implementation and verification chronology

- Restricted supported presets to truthful canonical Generate and added exact operation-schema validation for fields, types, ranges, generator mode, difficulty and typed seed. Unsupported/secret/fabricated fields fail closed.
- Added `apply_preset()` using canonical offline `GenerationRequest`/`GeneratorRouter`/bundle export and immutable expanded-request execution evidence independent of later preset edits/deletion.
- Added launcher `preset-apply` routing and changed the real Presets surface Apply action from preview-only expansion to canonical Generate execution.
- Added real Godot lifecycle integration covering create/apply, exact expanded request, update/new execution, prior execution immutability, delete preservation and invalid-field rejection.
- Focused Python command: `.venv\Scripts\python.exe -m pytest -q tests/unit/test_sb_lfx_008_presets.py` — `2 passed, 1 warning`.
- Real runtime command: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_presets_integration_suite.gd` — `SB-LFX-008-C001 PRESETS integration PASS`.
- Corrections during implementation: canonical generated wrappers expose `result` rather than `cells`, so Apply now accepts the wrapper contract; Godot JSON parses numbers as floats, so integration request comparison handles integer/float equivalence without weakening Python schema validation. Rerun passed.
- `git diff --check` and empty `TASKS.md` diff will be recorded before publication.
