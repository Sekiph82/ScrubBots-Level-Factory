# PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: `2026-09-13T09:52:13.4146057+03:00`
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Branch: `main`
- Starting local HEAD: `03ea6dd28dc44dad752a1d71e040db4868fe7fc8`
- Starting `origin/main`: `03ea6dd28dc44dad752a1d71e040db4868fe7fc8`
- Starting divergence: `0 0`
- Preserved user-owned worktree dirt: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, modified `docs/migration/legacy-task-trackers/PROJECT.json`, untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and untracked `review/m10.zip`. These paths are not task authority and will not be staged, removed, or rewritten.

## Authority and scope

The SP03-C001 implementation prompt, current root `TASKS.md`, and the
repository `AGENTS.md`/`GOVERNANCE.md` were read from GitHub. The prompt also
requires the SP02 live smoke evidence, SP02-C003 audit, conversion plan,
semantic/provider authority documents, accepted SP01/SP02 contracts, current
M07-M09 contracts, and `CLAUDE.md`; these will be read before implementation.
Root `TASKS.md` is the only current status tracker. Hidden legacy `.hiveai`
tracker/control-plane files remain outside scope.

This cycle implements only SP03-C001: the raw semantic artifact boundary,
deterministic local decode and 24x24 normalization foundation, explicit
background/alpha and palette-policy boundaries, and tests/tooling required by
the prompt. It will not begin SP03-C002, SP04, SP05, M11, Studio work, provider
qualification, LEVEL_ART palette integration, or live provider execution.

No Magnific or PixelLab calls, credentials, network access, or provider credits
will be used. Synthetic image fixtures may be used only for local tests.

This builder log was created before any SP03 source, test, fixture, or
documentation edit.

## Planned implementation

1. Inspect existing output/image helpers and dependency policy.
2. Add a small `semantic.normalization` package with immutable raw artifacts,
   versioned requests, normalized artifacts, reports, and one deterministic
   normalizer entry point.
3. Use a documented deterministic local decoder/resampler with explicit bounds,
   exact-size no-resize behavior, alpha/background policy, crop/pad policy, and
   `PRESERVE_SOURCE_RGBA` asset palette policy.
4. Keep LEVEL_ART requests fail-closed without future canonical palette policy.
5. Add focused raw/normalization/security tests and a minimal offline local-file
   CLI path if compatible with the existing CLI architecture.

## Implementation chronology

- Added `semantic.normalization` with `SemanticRawArtifact`,
  `SemanticNormalizationRequest`, `SemanticNormalizationReport`,
  `SemanticNormalizedArtifact`, typed errors, and deterministic normalizer
  aliases. Raw artifacts preserve immutable bytes, hashes, successful-candidate
  provenance, requested/returned dimensions, media type, and path-free input
  descriptors.
- Implemented a strict standard-library PNG decoder for 8-bit non-interlaced
  grayscale, RGB, grayscale-alpha, and RGBA images with CRC, filter, zlib,
  dimension, pixel-count, and input-size validation. JPEG/WebP and palette or
  ancillary/color-management chunks are explicitly rejected in C001.
- Implemented exact-size RGBA preservation, `PRESERVE_ALPHA` and
  `OPAQUE_AS_IS`, deterministic integer-weighted `AREA_AVERAGE_V1` resampling,
  centered `FIT_CENTER_LETTERBOX_V1`, and the ASSET_ART-only
  `PRESERVE_SOURCE_RGBA` palette boundary. LEVEL_ART remains fail-closed until
  the future C01..C16 normalization policy exists. Normalized artifacts retain
  raw/provider/request provenance and cannot be exported as M08 LEVEL_ART.
- Added the offline `semantic-normalize` CLI command. It accepts only a local
  file, requires explicit output class and dimensions, writes a deterministic
  JSON manifest, and rejects output paths that would overwrite the source.
- No runtime dependency was added; `pyproject.toml` remains `dependencies = []`.
  No provider SDK is imported or invoked by normalization.
- `python -m pytest -q tests/unit/test_sp03_normalization.py` initially found
  two defects: the area-resampling denominator was incorrect for downsampling,
  and the aspect-fit branch distorted wide sources. Both were corrected. The
  next run found the report validator incorrectly applying the 1024 logical
  bound to raw dimensions; that was corrected to use the existing 8192 raw
  bound. The subsequent SP03 focused run passed all 10 tests.
- `python -m pytest -q tests/unit/test_sp03_normalization.py tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp01_semantic_contracts.py` passed 74 tests.
- `python -m compileall -q src tests` passed after the SP03 implementation.
- `python -m scrubbots_pixel_factory.cli semantic-normalize --help` passed and
  exposed the explicit local-file policy surface.

## Final verification and scoped diff

- Final `python -m pytest -q` passed 455 tests in 249.47 seconds. Pytest
  emitted one non-blocking cache-permission warning for `.pytest_cache`.
- Final `python -m compileall -q src tests` passed.
- Standalone package import passed for the package and all public SP03 types,
  including `SemanticNormalizer`.
- `python -m scrubbots_pixel_factory.cli --help`,
  `python -m scrubbots_pixel_factory.cli semantic-normalize --help`, and the
  installed `scrubbots-pixel --help` all passed. The CLI exposes only a local
  normalization path and never calls a provider.
- The scoped normalization/CLI network/provider scan returned no matches, and
  the credential-pattern scan returned no matches.
- `git diff --check` passed. Git reported only expected LF-to-CRLF warnings for
  changed files on this Windows checkout.
- SP03 scoped changed paths are the normalization package, semantic exports,
  semantic CLI, semantic README, and `tests/unit/test_sp03_normalization.py`,
  plus this builder log. `TASKS.md`, audit/prompt/cycle files, M00-M10
  production algorithms, provider bridges, and the main ScrubBots repository
  were not changed. Existing unrelated worktree dirt remains preserved and
  unstaged.

## Publication checkpoint

- The implementation and completed builder log will be committed to `main`
  and pushed normally. Final local `HEAD`, `origin/main`, divergence, commit
  SHA, and push result will be recorded after publication below.

## Publication result

- Implementation commit: `448b88a7562e55d3b8dd32b5eac0b06f8b26c9a7`.
- `git push origin main` completed successfully, advancing `main` from
  `03ea6dd28dc44dad752a1d71e040db4868fe7fc8` to the implementation commit.
- Post-implementation publication checkpoint at
  `2026-09-13T10:15:31.3079601+03:00`: local HEAD and `origin/main` were both
  `448b88a7562e55d3b8dd32b5eac0b06f8b26c9a7`; divergence was `0 0`.
- This final log publication is a log-only follow-up commit; it does not
  modify source, tests, product artifacts, task state, or the preserved
  unrelated worktree dirt. A final fetch/equality check is performed after
  pushing this log publication.
