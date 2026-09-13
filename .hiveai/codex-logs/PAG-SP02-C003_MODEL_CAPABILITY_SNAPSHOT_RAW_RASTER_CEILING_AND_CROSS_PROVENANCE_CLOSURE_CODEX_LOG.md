# PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-13T07:25:12.6746081+03:00
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Branch: `main`
- Starting local HEAD: `dad806aa397a43aee7b99a437725658d1fe069ad`
- Starting `origin/main`: `dad806aa397a43aee7b99a437725658d1fe069ad`
- Starting divergence: `0 0`
- Preserved user-owned worktree dirt: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, modified `docs/migration/legacy-task-trackers/PROJECT.json`, untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and untracked `review/m10.zip`. These files are not task authority and will not be staged or removed.

## Authority and scope

The authoritative C003 prompt, previous C002 strict audit, and root `TASKS.md`
were read directly from GitHub. The GitHub versions of the C002 prompt and
C001 audit, `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`,
`docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`, `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`,
`AGENTS.md`, `GOVERNANCE.md`, and `CLAUDE.md` were read. The accepted SP01
contracts and current SP02 provider code/tests/fixtures were inspected locally
only after the GitHub synchronization. Official public PixelLab SDK references
authorized by the earlier cycle remain read-only reference material.

Root `TASKS.md` is the only current project-status tracker. Hidden legacy
`.hiveai` files are not used as current status authority and will remain
untouched. This cycle implements only SP02-C003, closes the bounded C002
findings, preserves accepted C002 behavior, and does not begin SP03/SP04 or
modify M00-M10 algorithms, task/audit state, prompts, or the main ScrubBots
repository.

No Magnific credits, PixelLab credentials, live provider calls, browser/private
endpoints, or provider generation will be used.

## Planned bounded remediation

1. Introduce one explicit versioned raw semantic returned-raster ceiling of
   8192 while leaving request/logical dimension contracts unchanged.
2. Replace permissive global Magnific capability data with immutable pinned
   model snapshots for the observed `recraft-v4-1`, `seedream-5-pro`, and
   `imagen-nano-banana-2-lite` surfaces, including model-specific aspect ratios,
   reference roles, and explicit resolution/quality values.
3. Remove free-text failure diagnostics from both result-manifest identity
   digests while preserving them in full serialization.
4. Add fail-closed request/job/manifest and request/job/candidate/manifest
   cross-binding validation.
5. Keep Magnific failure actual-model provenance optional unless actually
   reported, while requiring exact model binding for successful results.
6. Add the full C003 sensitivity matrix, update the truthful smoke fixture and
   provider documentation, then run all required regressions and offline scans.

This log was created before any C003 source, test, fixture, or documentation
edit.

## Implementation and verification chronology

- Added `SEMANTIC_RAW_RASTER_MAX_DIMENSION = 8192`; requested/logical
  dimensions remain bounded by the existing 1024 contract, while returned
  provider raster dimensions accept 2048/4096/8192 and reject larger values.
  `as_m08_artwork()` continues to fail because provider rasters are not logical
  grids.
- Added immutable pinned `MagnificModelCapabilitySnapshot` records and a
  fail-closed lookup. The snapshots record the observed model-specific ratios,
  roles, resolution/quality support, snapshot version, and documentation-only
  observation date. Job construction, role bindings, option validation, result
  import, fixture data, and public exports now use the exact snapshot.
- Removed free-text `failure_reason` from Magnific and PixelLab result identity
  digests while retaining it in `canonical_dict()` and failure candidates.
  Magnific failure actual-model provenance is optional; successful results must
  match the requested model.
- Added fail-closed Magnific request/job/manifest validation for request and
  job digests, provider/config/version, model, dimensions, seed, role/hash
  bindings, snapshot, derived ratio, prompt, and provider-seed declaration.
  Added checked PixelLab candidate/request/job manifest construction covering
  all request, engine, workflow, seed, dimensions, control, input, and output
  bindings.
- Added focused tests for the raw-raster ceiling, exact model snapshots and
  roles/ratios/options, unknown models, cross-request/job mismatches, failure
  identity semantics, and PixelLab candidate/job tampering.
- `python -m pytest -q tests/unit/test_sp02_provider_bridges.py` initially
  found one test-construction error: the new test passed `provider_resolution`
  into `SemanticGenerationRequest`, which has no such field. The test was
  corrected to pass `resolution` to `MagnificJobSpec.from_request`; the rerun
  passed 26 tests.
- `python -m pytest -q tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp01_semantic_contracts.py`
  passed 63 tests, then passed 64 tests after the final cross-binding cases
  were added. Pytest emitted one pre-existing cache-permission warning because
  `.pytest_cache` could not be written; it did not affect test execution.
- `python -m compileall -q src tests` passed.
- Standalone import passed and printed package version `0.1.0`, raw-raster
  ceiling `8192`, the `recraft-v4-1` snapshot, and `PixelLabProvider`.
- `python -m scrubbots_pixel_factory.cli --help` passed. Installed
  `scrubbots-pixel --help` also passed with the same generate/reproduce/batch
  surface.
- The scoped provider network scan for HTTP/SDK generation imports returned no
  matches. The scoped credential-pattern scan returned no matches. `git diff
  --check` passed (Git only reported expected LF-to-CRLF normalization
  warnings for changed files).
- `python -m pytest -q` passed 444 tests before the final additional focused
  mismatch test; the final full-suite rerun is recorded below.
- Final `python -m pytest -q` passed 445 tests in 231.73 seconds, with the
  same single non-blocking `.pytest_cache` permission warning.

## Pre-publication checkpoint

- Final source/test/doc edits are limited to the SP02-C003 provider-contract
  scope and this C003 log. Preserved unrelated dirty legacy-migration files,
  untracked legacy `.hiveai` projections, and `review/m10.zip` remain unstaged.
- No task tracker, audit, prompt, cycle, acceptance, M03-M10 algorithm, or
  main ScrubBots repository file was modified. No live Magnific or PixelLab
  generation was performed and no provider credits were spent.

## Implementation publication

- Implementation and completed-log commit: `013d8a169ffa8f2ecd4c48052a10cdccbd92c53b`.
- `git push origin main` completed successfully, advancing GitHub `main` from
  `dad806aa397a43aee7b99a437725658d1fe069ad` to the implementation commit.
- Publication checkpoint immediately before this final log-only commit:
  timestamp `2026-09-13T07:44:32.7141286+03:00`; local HEAD and
  `origin/main` were both `013d8a169ffa8f2ecd4c48052a10cdccbd92c53b`, with
  divergence `0 0`. The final log-only publication commit is pushed without
  changing product or test scope; its terminal equality checkpoint is verified
  after push and returned with this log.
