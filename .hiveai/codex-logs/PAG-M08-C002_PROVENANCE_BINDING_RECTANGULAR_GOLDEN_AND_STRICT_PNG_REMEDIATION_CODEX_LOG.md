# PAG-M08-C002 — Provenance Binding, Rectangular Golden & Strict PNG Remediation
Document role: CODEX BUILDER LOG

## Start

- Timestamp: 2026-09-10T21:30:12+03:00.
- Repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting synchronized HEAD: `760042785d81abf95c3d19ff422e514a3af46c65`.
- Starting `origin/main`: `760042785d81abf95c3d19ff422e514a3af46c65`; divergence `0 0`.
- Pre-existing local control-plane changes were preserved through the GitHub synchronization and remain outside this cycle: modified migrated legacy `docs/migration/legacy-task-trackers/EVENTS.jsonl` and `PROJECT.json`, plus untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`. The synchronization also preserved the GitHub control-plane migration to root `TASKS.md`; no sibling ScrubBots repository was used.

## Authority and scope

Read from GitHub `main` before implementation: the authoritative C002 remediation prompt, the C001 strict audit, the C001 builder log, current root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `.hiveai/CYCLE_INDEX.md`, the current M08 output package and tests/goldens, and the existing WFC/HYBRID/AUTO, GenerationResult/request/RNG, and M07 quality contracts. The C002 mission is limited to `F-PAG-M08-C001-001` through `F-PAG-M08-C001-003`: fail-closed rich WFC/HYBRID/AUTO provenance, genuine rectangular known-answer and committed golden evidence, and strict rejection of non-empty IEND payloads. M09+ and ChatGPT-owned tracker/audit/task acceptance state are out of scope.

## Required pre-edit boundary

This matching log was created before the first C002 source, test, or golden edit. Existing C001 implementation and evidence are preserved until focused C002 tests establish a required correction.

## Implementation record

- Preserved the accepted C001 output architecture and limited production changes to `output/bundle.py`, `output/png.py`, and the output README. Added explicit `generator_metadata=` support; raw successful WFC/HYBRID/AUTO results now fail closed without an authoritative wrapper or metadata input, while raw MASK/RULES exports remain supported.
- Added mode-specific fail-closed metadata validation. WFC metadata now binds namespace/schema, exemplar/style, target/source palettes and one-to-one mapping, request options, output dimensions, attempt bounds, and contradiction history. HYBRID metadata now binds strategy/master seed, dimensions/palette, ordered child stage seeds/requests/digests, final logical/result/topology digests, and topology evidence. AUTO metadata now binds configured order/fallback, root-seed initial selection, deterministic attempt stage seeds/order, failure prefix, selected engine identity, and exported result identity. These checks cross-bind only reconstructible fields and do not duplicate replay engines.
- Added a strict PNG parser gate requiring the single final IEND chunk to have exactly an empty payload; CRC and ordering checks remain intact.
- Replaced the misleading square row-major unit evidence with a legal 20x21 known-answer fixture whose first row, second row, and later coordinate distinguish `index = y * width + x` directly.
- Added committed deterministic rectangular goldens `tests/golden/fixtures/m08/golden-rectangular.json` and `golden-rectangular.png`, with exact canonical JSON/PNG/RGB/dimension/cell/palette/row-boundary assertions. Rectangular golden hashes: JSON `6f703e844d259f44c80ba49876193add9794a54739b19a7c8a0e072e21a7a7df` (grid hash); PNG fixture SHA-256 `02bed53fe7dede163783d298301adba502683fa400b3488c2bf5f4060a0472ed`.
- Added focused rich-provenance rejection/equivalence/tamper tests and the valid-CRC non-empty-IEND negative test.
- Correction recorded: the first rectangular test fixture made `(0,1)` a border C01, contradicting its intended known-answer C02 assertion. The fixture was corrected to use a distinct first row, and both rectangular goldens were regenerated deterministically.
- Correction recorded: a standalone WFC/HYBRID/AUTO rich round-trip smoke check initially rejected valid AUTO metadata because validation required all configured fallback attempts after an early success. Validation now accepts the deterministic attempt prefix through the first success, and the focused regression covers wrapper/read and explicit-metadata equivalence for all three rich modes.

### Verification

- Final focused command: `$env:PYTHONPATH='src'; python -m pytest tests/unit/test_m08_output.py tests/integration/test_m08_export_integration.py tests/golden/test_m08_export.py -q` — `16 passed, 1 warning` (pytest cache permission warning only).
- Earlier focused run after initial C002 edits: `12 passed, 1 warning`; subsequent correction runs and the final 16-test run are recorded above. No focused production failure was hidden or removed.
- Final full repository command after the last production hardening: `$env:PYTHONPATH='src'; python -m pytest -q` — `288 passed, 1 warning in 190.18s (0:03:10)`; the warning was the pytest cache permission warning only. This includes M01/M02 contract tests, M03 MASK, M04 RULES, M05 WFC, M06 router/hybrid/replay/AUTO, M07 quality/diversity, and all M08 tests.
- `python -m compileall -q src tests`, standalone package import, deterministic golden decode/hash checks, `git diff --check`, and static source-policy checks passed. No runtime network/API/telemetry/cloud references or logical resize/resample/interpolation code exists in the output Python package; no M09+ implementation was added; goldens contain no BG01/C17+/timestamps/absolute paths.
- `python -m pip check` reports the previously documented environment mismatch: `pytest-asyncio 0.24.0 has requirement pytest<9,>=8.2, but pytest 9.1.1 is installed`. C002 adds no dependencies.
- No ChatGPT-owned tracker, audit, task acceptance, prompt, or C001 log file was modified.

## Publication record

Pending. Record the implementation/evidence commit, completed-log publication, push results, and exact final local `HEAD == origin/main` verification.

## Publication record

Pending. Record the implementation/evidence commit, completed-log publication, push results, and exact final local `HEAD == origin/main` verification.
