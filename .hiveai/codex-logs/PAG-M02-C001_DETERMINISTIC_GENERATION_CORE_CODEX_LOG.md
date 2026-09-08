# PAG-M02-C001 — Deterministic Generation Core
Document role: CODEX BUILDER LOG

## 2026-09-08T22:57:53+03:00 — Start and authority

- Canonical authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Authoritative prompt was fetched directly from GitHub before implementation:
  `https://raw.githubusercontent.com/Sekiph82/ScrubBots-Level-Factory/main/.hiveai/prompts/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_PROMPT.md`.
- Previous strict audit: `.hiveai/audits/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_STRICT_AUDIT.md`.
- Prompt SHA-256 in the synchronized checkout: `E6E5E8A0C37E9FF0ADBE9BB0FDEE513EE43054FAF1DA9811577EC3E1F9EC1B9A`.
- Previous-audit SHA-256 in the synchronized checkout: `3A2B02B736AFE0BD7821B72673F9AD3A6FDC5358E32B5E7E1084BADE6D9D789B`.

## Starting repository evidence

- Canonical root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- `origin`: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Branch: `main`.
- Starting HEAD after synchronization: `71628ca822689be3d1305580a631981bac909c0c`.
- `HEAD...origin/main`: `0 0`.
- Initial status: `## main...origin/main` plus pre-existing unstaged ` M .hiveai/PROJECT.json`.
- The pre-existing PROJECT edit changes only the repository field from the short identity to the full GitHub URL. It is preserved and is outside this cycle's commits.
- No stash entries were present; the only worktree listed was the canonical Level Factory mirror.

## Synchronization and required reads

- Executed non-destructive synchronization: `git fetch origin main`, `git rev-list --left-right --count HEAD...origin/main`, and `git merge --ff-only origin/main`.
- Synchronization fast-forwarded `4160191` to `71628ca822689be3d1305580a631981bac909c0c`; no local product changes were discarded.
- Read completely: `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, `tasks.md`, `AGENTS.md`, `GOVERNANCE.md`, `.hiveai/PROJECT_DASHBOARD.md`, `.hiveai/CYCLE_INDEX.md`, the active M02 prompt, and the M01 strict audit.
- Read the current M01 contract modules under `src/scrubbots_pixel_factory/contracts/`, the M00 runtime/offline modules and tests, `pyproject.toml`, and all existing tests.
- No main `ScrubBots` checkout was accessed. No task, tracker, H!veAI state, handoff, cycle-index, prompt, or audit file was modified.

## Planned M02 implementation boundary

Implement only the deterministic generation core: immutable validated request and versioned options, canonical request serialization, one project-owned SHA-256 counter RNG with stage/retry derivation, explicit generator interface, immutable validated success/failure result, a test-only deterministic probe, and four compact golden fixtures. Preserve M00/M01 contracts and the offline-only boundary. Do not add production generator engines, routing, rendering, CLI, network/API dependencies, or M03+ work.

The implementation will keep M01's narrow `_stable_select.py` helper unchanged and use the M02 RNG for new generation-stage derivation. Canonical JSON will be UTF-8, compact, sorted-key, finite-number-only JSON with typed seed representation. Result provenance will include reproducible stage identifiers and RNG metadata while logical grids remain exact row-major C-ID tuples.

This log will be appended chronologically with implementation decisions, commands, tests, corrections, changed files, commit/push checkpoints, and final repository evidence. The final log publication will not attempt to contain its own commit SHA; the terminal HEAD is intentionally left for ChatGPT/H!veAI to record.

## 2026-09-08T22:58–23:07+03:00 — Implementation and verification

### Implementation decisions

- Added `core/request.py` with frozen `GenerationRequest` and `GeneratorOptions`. Inputs are validated through the M01 difficulty/palette contracts, nested options are recursively converted to tuples/mapping proxies, and only finite JSON-compatible option values are accepted.
- Request serialization is compact sorted-key UTF-8 JSON with an explicit schema/version and typed integer/string seed representation. Omitted axes resolve through M02 stage seeds and M01 validators; explicit axes remain independently validated with no clamping.
- Added `core/rng.py` as the sole new core randomness authority: `SCRUBBOTS_SHA256_COUNTER_V1`. It provides fixed bytes/u64, rejection-sampled `randbelow`, ordered choice/shuffle, independent child/stage streams, named stage seeds, and attempt-indexed retry seeds. Stage/retry derivation depends on the root seed/domain rather than prior stream consumption.
- Added `core/generator.py` with a runtime-checkable `PixelGenerator` protocol requiring an immutable request and explicit project RNG.
- Added `core/result.py` with immutable success/failure results. Success validates dimensions, exact row-major cell count, canonical C-ID cells, actual used-color bands, requested-palette containment, mode/seed consistency, generator version, RNG identity, and five-stage provenance. Failure codes are stable generic values and cannot carry a grid.
- Exported only the M02 core contracts from the package root. No production generator engine, router, rendering/export, CLI, M03+ module, network dependency, or main ScrubBots dependency was added.
- Added only a test-only `DeterministicContractProbeGenerator` under `tests/support/`; it uses project-owned stage streams and emits complete legal grids solely for deterministic contract proof.
- Added four compact golden fixtures (EASY, MEDIUM, HARD, VERY_HARD) with request parameters, resolved dimensions, palette, stage-seed IDs, grid SHA-256, and canonical result SHA-256.

### Material commands and corrections

- `.venv\\Scripts\\python.exe -m compileall -q src` passed.
- The first inline import smoke command was malformed by PowerShell quoting and failed with `SyntaxError: '(' was never closed`; it was corrected and the standalone request import passed.
- Initial M02 focused run: `31 passed, 2 failed`. One failure was the placeholder RNG vector and one expected the wrong exception type for mode mismatch. The test vector was replaced with the recorded deterministic value `801623960106958567`, the assertion was corrected to `ResultContractError`, and the focused run then passed.
- After the probe stream correction and interface/59×59 coverage, focused M02 command:
  `.venv\\Scripts\\python.exe -m pytest tests/unit/test_m02_request.py tests/unit/test_m02_rng.py tests/unit/test_m02_result.py tests/unit/test_m02_interface.py tests/golden/test_m02_golden.py tests/integration/test_m02_determinism.py -q -p no:cacheprovider`
  Result: `39 passed in 0.44s`.
- Full regression command:
  `.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider`
  Result: `99 passed in 1.07s`.
- Standalone import smoke passed: package `0.1.0`, canonical request bytes produced without the main checkout.
- `.venv\\Scripts\\python.exe -m pip check` passed: `No broken requirements found.`
- The requested `.venv\\Scripts\\python.exe -m build --wheel --sdist --no-isolation` command could not start because the venv has no `build` module. A temporary-output `pip wheel . --no-deps --no-build-isolation` attempt also failed because that venv lacks `setuptools.build_meta`. Corrected build command using the available system Python 3.12 backend:
  `py -3.12 -m pip wheel . --no-deps --no-build-isolation --wheel-dir C:\\Users\\sekip\\AppData\\Local\\Temp\\scrubbots-m02-build`
  Result: wheel `scrubbots_pixel_factory-0.1.0-py3-none-any.whl`, size `21619`, SHA-256 `ee55fedb820a592d496508388aa537c2a6502686e33a68396f9a08c50a2dddd7`.
- Production-core static scan checked five `.py` modules and found no `random` import, network import, subprocess/shell execution, `eval`, `exec`, or `pickle`; existing offline/source-policy tests also passed in the full suite.
- `git diff --check` passed. Git emitted only its normal LF-to-CRLF working-copy warning for the package root file.
- Confirmed no `src` paths for `generators`, `output`, or `cli`; no M03+ production implementation exists.

### Files changed by this cycle

- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/core/__init__.py`
- `src/scrubbots_pixel_factory/core/request.py`
- `src/scrubbots_pixel_factory/core/rng.py`
- `src/scrubbots_pixel_factory/core/generator.py`
- `src/scrubbots_pixel_factory/core/result.py`
- `tests/support/__init__.py`
- `tests/support/deterministic_probe.py`
- `tests/unit/test_m02_request.py`
- `tests/unit/test_m02_rng.py`
- `tests/unit/test_m02_result.py`
- `tests/unit/test_m02_interface.py`
- `tests/integration/test_m02_determinism.py`
- `tests/golden/m02_fixtures.json`
- `tests/golden/test_m02_golden.py`
- this matching builder log

The pre-existing `.hiveai/PROJECT.json` modification remains unstaged and is intentionally excluded from the implementation commit. No task/H!veAI acceptance state, handoff, cycle index, prompt, audit, or prior log was modified.

## 2026-09-08T23:08+03:00 — Implementation publication checkpoint

- Staged implementation/test scope only and committed it as `c30227e264e1cc9c09daa80273eb14613bbb7b6d` (`Implement deterministic generation core`).
- Pushed implementation commit successfully: `71628ca..c30227e` to `origin/main`.
- Post-push verification: local `HEAD = c30227e264e1cc9c09daa80273eb14613bbb7b6d`; `origin/main = c30227e264e1cc9c09daa80273eb14613bbb7b6d`; ahead/behind `0 0`.
- At this checkpoint the only worktree changes were the intentionally preserved unstaged `.hiveai/PROJECT.json` edit and this untracked matching builder log.

The matching builder log is now complete for publication. Its own final publication commit SHA is intentionally not written into this file, per the M02 prompt's non-self-referential logging rule.
