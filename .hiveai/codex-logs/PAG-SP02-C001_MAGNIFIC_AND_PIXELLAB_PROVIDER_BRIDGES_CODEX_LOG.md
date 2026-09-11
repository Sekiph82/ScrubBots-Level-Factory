# PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-11T21:24:57.4851375+03:00
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Branch: `main`
- Starting local HEAD: `a29cd55d0e016140b8e2e640b01e81f10d039f06`
- Starting `origin/main`: `a29cd55d0e016140b8e2e640b01e81f10d039f06`
- Starting divergence: `0 0`
- Starting worktree: pre-existing user-owned dirt was preserved; it consists of modifications under `docs/migration/legacy-task-trackers/` and untracked legacy migration/control-plane files under `.hiveai/`.

## Authority and scope

The authoritative SP02-C001 prompt and the current GitHub-first tracker were read directly from GitHub. The repository identity, `main` branch, origin, worktrees, status, and synchronization state were checked before implementation. The current repository authority files read for this cycle are the root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/CYCLE_INDEX.md`, the SP02-C001 prompt, and the preceding SP01/provider-authority material required by that prompt.

This cycle implements only SP02-C001. M00-M10 infrastructure remains preserved. The main `ScrubBots` repository is not used for edits. Magnific remains an external job-spec/result-import bridge only; PixelLab is optional, lazy, injectable, and never called without explicit execution and owner-provided local credentials. No provider credits, live generation, network calls, or secrets are used by this builder run.

## Planned implementation

Implement isolated, lazily selected MAGNIFIC and PIXELLAB provider bridges with deterministic registries, canonical versioned job/result manifests, exact SP01 provenance binding, role/hash-checked local execution inputs, truthful capability declarations, typed unavailable/failure results, offline-safe tests, fixtures, and documentation. Add only an optional PixelLab dependency declaration; keep the default runtime dependency-free and avoid eager SDK imports.

Required verification will include provider registry and isolation tests, canonical identity/tamper tests, result-ingestion and dimension tests, injected PixelLab adapter tests, Magnific no-network tests, offline/source-policy scans, focused SP02 tests, M00-M10 regression tests, and the full repository suite. Failures and corrections will be recorded chronologically below.

## Chronological work log

### Log creation

This log was created before any SP02 source, test, fixture, or documentation edit.

### Authority and reference inspection

The pinned official PixelLab reference was inspected read-only. Its public
client uses `PIXELLAB_SECRET`/`PIXELLAB_BASE_URL`, and its public methods are
`generate_image_pixflux` and `generate_image_bitforge`; the documented control
vocabularies were used only through an explicit mapping table. No SDK source,
sample artwork, upstream runtime, or provider asset was copied into this
repository.

### Implementation

Added isolated `semantic/providers/` modules. The registry exposes only the
explicit IDs `MAGNIFIC` and `PIXELLAB` in deterministic order and lazily imports
the selected bridge. Magnific is a pure local external job/result bridge with
ordered role/hash-to-creation bindings, explicit model/aspect/count metadata,
logical dimensions and original seed provenance, and a provider-seed-
unsupported marker. Its importer verifies request/job/provider bindings, raw
bytes hash, media metadata, dimensions, and status before constructing the raw
SP01 candidate; it performs no normalization or network call.

PixelLab has separate PIXFLUX and BITFORGE engine selection, optional package
metadata (`pixellab>=1.0.8,<2`), env-only runtime credentials excluded from
repr/identity, deterministic project-owned non-negative provider seeds,
explicit official control mappings, exact `image_size`, local role/hash byte
bindings, injected-client execution, strict returned-dimension validation,
versioned result manifests, usage audit metadata, and typed unavailable/failure
results. The optional SDK import occurs only in explicit execution. The public
provider docs describe the offline boundary, lack of fallback, exact-size and
seed differences, and the SP03/SP04 handoff.

Added deterministic Magnific and PIXFLUX 16×16 wizard job fixtures and focused
tests covering registry isolation, canonical identity, request/seed/control
binding, reference/style/init/color role/hash validation, result corruption,
secret exclusion, fake-client method/kwargs/bytes/dimension behavior, typed
offline unavailability, and separate BitForge selection.

### Verification chronology

- `python -m compileall -q src` and `git diff --check`: passed.
- Initial focused run `python -m pytest -q tests/unit/test_sp02_provider_bridges.py`: 9 passed, 1 failed. The failure revealed that PixelLab byte-hash mismatch surfaced as the lower-level contract exception. Corrected the binding boundary to translate it to `SemanticProviderError`.
- Rerun of the focused SP02 suite: 11 passed.
- `python -m pytest -q tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp01_semantic_contracts.py`: 48 passed.
- Full `python -m pytest -q`: 429 passed in 251.48s. Pytest emitted one pre-existing cache-permission warning because the workspace `.pytest_cache` path is not writable; no test failed.
- `python -m compileall -q src tests`: passed.
- Standalone import `python -c "import scrubbots_pixel_factory; import scrubbots_pixel_factory.semantic.providers"`: passed and reported provider IDs `('MAGNIFIC', 'PIXELLAB')`.
- `python -m scrubbots_pixel_factory.cli --help`: passed.
- Installed `scrubbots-pixel --help`: passed.
- `git diff --check`: passed; Git reported only normal LF-to-CRLF working-copy warnings.
- Offline/source scan found no runtime HTTP/request import in the provider bridges. The only provider network URL is the documented PixelLab default endpoint, and the only SDK import is lazy inside explicit PixelLab execution. No credentials, credits, API calls, or live generation were used.

### Files changed by SP02

- `pyproject.toml` — optional PixelLab extra only.
- `src/scrubbots_pixel_factory/semantic/__init__.py` — lazy public SP02 bridge exports.
- `src/scrubbots_pixel_factory/semantic/providers/**` — registry, shared canonical helpers, Magnific bridge, PixelLab bridge, and provider documentation.
- `tests/unit/test_sp02_provider_bridges.py` — focused offline contract tests.
- `tests/fixtures/sp02/magnific_smoke_job.json` and `tests/fixtures/sp02/pixellab_pixflux_job.json` — deterministic no-call job fixtures.

The pre-existing dirty files under `docs/migration/legacy-task-trackers/` and
untracked legacy migration/control-plane files under `.hiveai/` were not
staged, changed, or removed. Root `TASKS.md`, `.hiveai/TASKS.md`, task ledgers,
events, cycle index, prompts, and audits were not modified.
