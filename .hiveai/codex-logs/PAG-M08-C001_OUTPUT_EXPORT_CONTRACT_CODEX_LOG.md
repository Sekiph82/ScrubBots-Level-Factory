# PAG-M08-C001 — Output / Export Contract
Document role: CODEX BUILDER LOG

## Start

- Timestamp: 2026-09-10T16:35:33+03:00.
- Repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting synchronized HEAD: `8790113f55c4b43bfd4939dd3c37c4959f5fbd64`.
- Starting `origin/main`: `8790113f55c4b43bfd4939dd3c37c4959f5fbd64`; divergence `0 0`.
- Pre-existing local control-plane changes were preserved and remain outside this cycle: modified `.hiveai/EVENTS.jsonl`, modified `.hiveai/PROJECT.json`, and untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`. No sibling ScrubBots repository was used.

## Authority and scope

Read from GitHub `main` before implementation: `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, the v3 machine block in `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `tasks.md` including M08 tasks and the global Definition of Done, `.hiveai/CYCLE_INDEX.md`, `AGENTS.md`, `GOVERNANCE.md`, the M07 C003 closing strict audit, the M02 request/result/RNG contracts, M01 palette/difficulty contracts, M03-M06 representative generator/router outputs and metadata, M07 quality/hash APIs and tests, `pyproject.toml`, `.gitignore`, package exports, offline guard, and the authoritative M08 prompt.

This cycle implements only `PAG-M08-C001`, covering `PAG-0801` through `PAG-0830`: deterministic versioned logical JSON, metadata/provenance binding, exact logical-resolution PNG and strict project-profile decoder, optional integer preview, filesystem bundle write/read/round-trip validation, corruption/negative cases, golden evidence, and representative M01-M07 integration. M09-M11 are out of scope. ChatGPT-owned tracker/task/audit state is read-only.

## Required pre-edit boundary

This matching log was created before any M08 implementation, test, golden, or documentation edit.

## Initial implementation/debug record

- Initial smoke export exposed a nested immutable-provenance serialization defect (`mappingproxy` was not recursively canonicalized); `_mapping_copy` was applied to GenerationResult provenance.
- The next smoke round trip exposed a preview validation defect: expected rows repeated a complete source row instead of each source cell horizontally. Preview validation was corrected to expand each cell into an exact integer block.
- The first dedicated M08 test run reported `6 passed, 2 failed`: one test incorrectly assumed every candidate wrapper exposed `logical_grid` (AUTO stores it in its result), and the quality-negative fixture swapped two identical border cells so no grid difference existed. Both were corrected in tests; no production contract was weakened.
- The corrected focused run reported `7 passed, 1 failed` because the test asserted an outdated synthetic exemplar identifier; it was corrected to the repository fixture's actual `wfc-synthetic-easy-3` ID.

## Implementation record

- Added `src/scrubbots_pixel_factory/output/artwork.py`: immutable versioned logical-artwork JSON, explicit candidate identity validation, exact dimensions/difficulty contract, ascending actual-used C-ID palette, row-major cells, and the existing M07 logical-grid hash. Quality state is deliberately absent from this immutable artifact.
- Added `src/scrubbots_pixel_factory/output/png.py`: standard-library deterministic 8-bit RGB encoder/decoder, one logical cell per PNG pixel, filter-0 rows, canonical palette-only RGB, strict CRC/chunk/IHDR/IDAT/profile checks, exact raw RGB bytes, and bounded integer preview replication.
- Added `src/scrubbots_pixel_factory/output/bundle.py`: deterministic metadata binding for successful `GenerationResult` request/result digest, generator identity, typed seed, RNG/provenance, WFC/HYBRID/AUTO metadata, and recomputed M07 quality state; fail-closed JSON/PNG/preview round trips; stable conflict-safe filesystem writes; identical rewrites are allowed and conflicting rewrites are rejected.
- Added package exports in `src/scrubbots_pixel_factory/output/__init__.py` and the top-level package initializer, plus `output/README.md` documenting the contract and offline/source-art invariants.
- Added unit, integration, and golden coverage in `tests/unit/test_m08_output.py`, `tests/integration/test_m08_export_integration.py`, and `tests/golden/test_m08_export.py`. Coverage includes malformed PNG/schema/palette/hash/failed-result cases, rectangular output, all difficulty bands, 59x59, quality rejection without artwork mutation, representative MASK/RULES/WFC/HYBRID/AUTO provenance, cross-file corruption, conflict writes, cross-process stability, and exact committed JSON/PNG bytes.
- Generated committed golden pair `tests/golden/fixtures/m08/golden-easy.json` and `golden-easy.png`. Final SHA-256 values: JSON `51cee47d86ae632532576a305c8cb65095bbaeec0ebae4056caa8288dd991700`; PNG `b02fb0566bda9bb3c632b64501b8e589eac7cf2dc2b1171ee323b7f04c65b791`.
- Debug correction: initial smoke export exposed nested immutable-provenance serialization (`mappingproxy`); recursive JSON canonicalization was added. Preview validation initially repeated whole rows instead of exact cell blocks; row/cell expansion was corrected.
- Debug correction: the first dedicated M08 run reported `6 passed, 2 failed` because a test assumed every wrapper exposed `logical_grid` and its quality-negative fixture swapped identical border cells. Tests were corrected without weakening production code. The next run reported `7 passed, 1 failed` due to an outdated synthetic exemplar identifier; it was corrected to `wfc-synthetic-easy-3`.
- Debug correction: the first combined M08 collection exposed a pytest module-name collision between the golden and integration modules. The integration module was renamed to `test_m08_export_integration.py`.
- Debug correction: after read-side binding hardening, a focused run reported `2 failed` because validation looked for `generator` at the flattened metadata level rather than inside the canonical GenerationResult. The validator was corrected to bind the canonical nested generator and full RNG object; the focused suite then passed.

### Required evidence

- Final focused M08 command: `$env:PYTHONPATH='src'; python -m pytest tests/unit/test_m08_output.py tests/integration/test_m08_export_integration.py tests/golden/test_m08_export.py -q` — `12 passed, 1 warning` (pytest cache permission warning only).
- Final full repository command: `$env:PYTHONPATH='src'; python -m pytest -q` — `284 passed, 1 warning in 190.58s`; the warning was the same pytest cache permission warning.
- The full suite includes the required M01-M07 regression, acceptance, golden, deterministic, offline, and cross-process coverage; the M08 integration suite separately exercises all difficulty bands, rectangular output, 59x59, and cross-process JSON/PNG byte stability.
- `python -m compileall -q src tests` passed. `git diff --check` passed.
- Static/source-policy checks found no runtime network or telemetry imports in the M08 output package. The output path contains no resizing/resampling/interpolation operation; logical PNG encoding remains one cell per pixel and preview scaling is positive-integer presentation replication only. The committed JSON/PNG contain no BG01, C17, timestamps, absolute paths, or runtime-generated metadata.
- `python -m pip check` reported the pre-existing environment mismatch `pytest-asyncio 0.24.0 has requirement pytest<9,>=8.2, but pytest 9.1.1 is installed`. M08 adds no dependencies and does not alter the environment.
- No task/tracker/audit state was modified. The pre-existing `.hiveai/EVENTS.jsonl`, `.hiveai/PROJECT.json`, `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json` changes remain preserved and outside the implementation commit.

### PAG task coverage mapping

- `PAG-0801..PAG-0807`: versioned immutable logical-artwork JSON, candidate identity, difficulty/dimensions, ascending actual-used palette, row-major cells/index rule, M07 grid hash, and strict round-trip validation.
- `PAG-0808..PAG-0814`: deterministic metadata, successful-result digest/request binding, generator identity/mode/version, typed seed/RNG/stage provenance, generator-specific metadata, quality binding, and separation of artwork truth from ACCEPT/REJECT state.
- `PAG-0815..PAG-0819`: exact logical-resolution canonical RGB PNG, project-owned deterministic encoder, no alpha/palette/interlace, filter-0 rows, CRCs, and canonical C-ID/RGB enforcement.
- `PAG-0820..PAG-0821`: optional positive-integer preview with exact nearest-neighbor block replication and no logical-artwork mutation.
- `PAG-0822..PAG-0828`: strict decoder corruption/profile/off-palette rejection, dimension/pixel correspondence, raw RGB byte truth, and fail-closed cross-file bundle checks.
- `PAG-0829`: committed deterministic JSON/PNG golden pair and round-trip evidence.
- `PAG-0830`: deterministic repeated-write and cross-process byte stability with conflict-safe filesystem publication.

## Publication record

- Implementation/evidence commit: `3612cc2e58917c40d430fa2de3b6a2e4e02beb4c` (`Implement M08 deterministic output export contract`).
- Push command: `git push origin main` — succeeded; remote advanced `8790113..3612cc2`.
- Post-push equality checkpoint: after `git fetch origin main`, local `HEAD` was `3612cc2e58917c40d430fa2de3b6a2e4e02beb4c`, `origin/main` was `3612cc2e58917c40d430fa2de3b6a2e4e02beb4c`, and divergence was `0 0`.
- The completed builder log is published in the following log-publication commit. Immediately after pushing that commit, local `HEAD` and `origin/main` are verified equal; the terminal verification is reported with this published log.
