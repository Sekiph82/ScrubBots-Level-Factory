# PAG-M09-C001 — CLI & Local Batch Generation
Document role: CODEX BUILDER LOG

## Start

- Timestamp: 2026-09-11T00:30:30+03:00.
- Repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting synchronized HEAD: `ed5d2c307c2abab14088f6997365085481661ae8`.
- Starting `origin/main`: `ed5d2c307c2abab14088f6997365085481661ae8`; divergence `0 0`.
- Initial worktree contained only preserved pre-existing local changes: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, modified `docs/migration/legacy-task-trackers/PROJECT.json`, and untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`. These remain outside this cycle and unstaged.
- No sibling `C:\Users\sekip\Desktop\ScrubBots` repository was used.

## Authority and scope

Read directly from GitHub `main`: the M09 C001 authoritative prompt, the M08 C003 closing strict audit, root `TASKS.md` as the sole current tracker, `AGENTS.md`, `GOVERNANCE.md`, the current `CYCLE_INDEX.md`, `pyproject.toml`, and the accepted M00-M08 core/request/result/RNG, router, WFC, quality and output contracts plus relevant tests/fixtures. The current GitHub control-plane migration means `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, and `.hiveai/EVENTS.jsonl` are not present on `origin/main`; legacy local copies/dirt are not task authority and were not revived or modified.

This cycle is limited to `PAG-M09-C001`, covering `PAG-0901` through `PAG-0930`: a standard-library Windows-friendly offline CLI for single generation, exact reproduction, deterministic finite batch generation, canonical resumable manifests, duplicate detection, quality handling, review output, local-only exemplar loading, and preservation of M08 rich provenance. M10/M11, tracker/task acceptance, audits, and the main ScrubBots repository are out of scope.

## Required pre-edit boundary

This matching M09 builder log was created before the first M09 source, test, fixture, manifest, or documentation edit. The synchronized GitHub state and pre-existing local changes above were preserved.

## Implementation record

- 2026-09-11: Added the dependency-free `src/scrubbots_pixel_factory/cli/` package with `argparse` commands `generate`, `reproduce`, and `batch`, plus `python -m scrubbots_pixel_factory.cli` support. Added the installed entry point `scrubbots-pixel = scrubbots_pixel_factory.cli.main:main` in `pyproject.toml`.
- 2026-09-11: M09 contract decisions: canonical decimal integer seed tokens (`0` or a non-zero decimal with optional leading `-`) parse as integer seeds; every other explicit token remains a string seed. Omitted single-generation seeds use local `secrets.randbits(128)` at the CLI boundary and are printed/recorded. Batch seeds are mandatory. Default single IDs are `candidate-` plus the canonical request SHA-256; batch IDs include deterministic batch identity and zero-padded attempt index. Exit codes are `0` success, `2` argparse usage, `3` invalid request/config, `4` generator failure, `5` quality rejection, `6` reproduce mismatch/unsupported metadata, `7` batch exhausted, and `8` filesystem/output failure.
- 2026-09-11: Implemented strict local JSON exemplar loading into the existing immutable `Exemplar` and `ExemplarRegistry` contracts, including duplicate-ID, malformed, ownership, palette, and provenance validation. No network lookup or production fixture substitution is possible. The router is constructed with the supplied local WFC registry and all generation paths call `GeneratorRouter.generate_candidate()`.
- 2026-09-11: Implemented single generation through M07 `QualityPolicy`/`evaluate_grid` and M08 `export_candidate`, preserving rich WFC/HYBRID/AUTO wrappers and fail-closed provenance. Reproduction strictly parses the recorded M02 request, rebuilds through the router, compares exact logical-grid hash/cells, and compares regenerated M08 bundle bytes before optional output.
- 2026-09-11: Implemented versioned `scrubbots-batch-manifest` v1 canonical JSON with immutable request/config identity, typed root/attempt seeds, quality policy, ordered attempt records, distinct generator-failure/quality-rejection/duplicate/accepted statuses, accepted bundle paths, terminal state, and deterministic IDs. Attempt seeds derive from `DeterministicRNG(root_seed).retry_seed(index)` independently of outcomes. Manifest writes use same-directory temporary files, fsync, and atomic replace. Resume validates schema, immutable batch identity/config, exemplar identities, safe relative paths and prior bundles, then continues at `next_attempt_index`; COMPLETE resume is a byte no-op and EXHAUSTED resume remains exhausted.
- 2026-09-11: Implemented exact duplicate detection using M07 logical-grid hashes followed by exact dimensions/cell equality, without grid mutation. Added deterministic M09 batch HTML report and reused M07 review manifest/contact-sheet generation for accepted logical grids. No bulk manual outputs or generated fixtures were added to the repository.
- 2026-09-11: First M09 test run reported two test-harness failures: a monkeypatch path resolved the package-level `main` function instead of the CLI module, and the duplicate test called `GenerationResult.success()` with unsupported `used_palette`. Corrected only those tests by importing the module explicitly and relying on the existing result contract; rerun passed `10 passed, 1 warning`. The failures and corrections were not hidden.
- 2026-09-11: Added focused tests for controlled entropy, seed parsing, local-only paths, single/reproduce/invalid requests, WFC local exemplar matching/missing/wrong cases, deterministic batch manifests and completed-resume no-op, interrupted/resumed byte convergence, exact duplicate records, bounded generator failure, cross-process help, and network-blocked CLI execution. M09 focused command passed `14 passed, 1 warning in 4.16s`.
- 2026-09-11: M08 preservation command passed: `$env:PYTHONPATH='src'; python -m pytest tests/unit/test_m08_output.py tests/integration/test_m08_export_integration.py tests/golden/test_m08_export.py -q` — `19 passed, 1 warning in 1.70s` when run before the final M09 additions; the final full run below includes these tests.
- 2026-09-11: Combined M09/M08 focused command passed `32 passed, 1 warning in 7.10s`; the final full run below includes the later network-blocked CLI test.
- 2026-09-11: PowerShell/module evidence passed: `python -m scrubbots_pixel_factory.cli --help`; editable install without dependencies via `python -m pip install --no-deps -e .`; installed `scrubbots-pixel --help`; and installed `scrubbots-pixel generate --difficulty EASY --mode MASK --width 20 --height 20 --seed 56 --output <temporary local directory>` returned exit `0` and an accepted M08 bundle.
- 2026-09-11: Manual batch evidence passed in a temporary directory: deterministic MASK batch `count=2,max_attempts=10,seed=1000,width=20,height=20` completed with `accepted=2, attempts=2`; completed `--resume` returned success without changing manifest bytes. Test-driven interrupted/resumed batch and a clean uninterrupted batch converged byte-for-byte, including manifest, bundles and review files. A forced constant-grid run recorded one `ACCEPTED` then one exact `DUPLICATE` and terminated at the explicit bound; a no-exemplar WFC batch recorded `GENERATOR_FAILURE` and returned exit `7`.
- 2026-09-11: Final full regression command passed: `$env:PYTHONPATH='src'; python -m pytest -q` — `305 passed, 1 warning in 233.88s (0:03:53)`. The warning is the existing pytest cache permission warning. This includes M00-M08 regression, M09 CLI/reproduce/batch/resume/duplicate/path-safety/offline/cross-process coverage, rectangular output, 59x59 and rich provenance preservation.
- 2026-09-11: Final verification passed: `python -m compileall -q src tests`; standalone package import printed `import ok`; `git diff --check` passed. Source scans over the M09 package and `pyproject.toml` found no `urllib/requests/httpx/urlopen/fetch/telemetry/socket`, resize/resample/interpolation, or `random/uuid/time` references. No dependency/license change was introduced; `pip check` reports only the pre-existing `pytest-asyncio 0.24.0` requirement conflict with installed pytest `9.1.1`.
- 2026-09-11: Final intended changes are limited to `README.md`, `pyproject.toml`, `src/scrubbots_pixel_factory/cli/__init__.py`, `src/scrubbots_pixel_factory/cli/__main__.py`, `src/scrubbots_pixel_factory/cli/main.py`, `tests/unit/test_m09_cli.py`, `tests/integration/test_m09_cli_integration.py`, and this new builder log. No M00-M08 production generator/output/quality code, task/tracker/audit/prompt state, sibling repository, or committed generated output was modified. The pre-existing local control-plane dirt remains unstaged.

## Publication record

- Implementation commit: `23f27f3e73dc4a6ef34338378139aac842f3fde6` (`Implement M09 offline CLI and batch generation`). It contains only the M09 CLI package, entry point/docs, M09 tests, and this matching builder log.
- `git push origin main` succeeded; remote advanced `ed5d2c3..23f27f3`.
- Completed-log publication commit: `5f1324dade158315dfc062a079d4dbde716fd409` (`Complete M09 C001 builder log`), pushed successfully to `origin/main`.
- Terminal post-completed-log equality verification: after `git fetch origin main`, local `HEAD` was `5f1324dade158315dfc062a079d4dbde716fd409`, `origin/main` was `5f1324dade158315dfc062a079d4dbde716fd409`, and `git rev-list --left-right --count HEAD...origin/main` returned `0 0`.
