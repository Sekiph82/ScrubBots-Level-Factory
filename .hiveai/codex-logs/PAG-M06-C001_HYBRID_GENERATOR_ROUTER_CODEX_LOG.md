# PAG-M06-C001 — Hybrid Generator Router
Document role: CODEX BUILDER LOG

## 1. Start

- Start timestamp: 2026-09-09T18:00:00+03:00 (Europe/Istanbul; recorded at cycle start).
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical repository URL: https://github.com/Sekiph82/ScrubBots-Level-Factory
- Authoritative prompt URL: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M06-C001_HYBRID_GENERATOR_ROUTER_PROMPT.md
- Previous independent audit URL: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Main ScrubBots repository was not accessed or modified.

## 2. Initial repository checkpoint

- Branch: `main`.
- Starting local HEAD before the required GitHub synchronization: `de4f2556a51e9b2fa49c215c3afea0d087ab3468`.
- `origin`: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting `origin/main`: `c4682b0eab42f5f577f6d58a3ecd6ceab832f8e1`.
- Starting relation: local was 0 ahead and 7 behind `origin/main`.
- Initial status: pre-existing dirty control-plane files `.hiveai/EVENTS.jsonl`, `.hiveai/HANDOFF.md`, `.hiveai/PROJECT.json`, `.hiveai/STATE.json`, plus untracked `.hiveai/EVENT_INDEX.json`; these are preserved and excluded from implementation commits.
- Existing stashes were inspected and preserved; the top preservation stash was `stash@{0}: On main: codex-preserve-preexisting-controls-and-M05-C002-work-before-sync`.

## 3. Authority and required reads

Read directly from the authorized checkout and GitHub authority:

- `.hiveai/PROJECT.json`
- `.hiveai/RULES.md`
- `.hiveai/STATE.json`
- `.hiveai/HANDOFF.md`
- `tasks.md`
- `AGENTS.md`
- `GOVERNANCE.md`
- `.hiveai/PROJECT_DASHBOARD.md`
- `.hiveai/CYCLE_INDEX.md`
- M06 authoritative implementation prompt
- M05-C002 independent strict audit

The local control plane reports stale/reconciled historical state; this cycle follows the explicit GitHub M06 prompt and does not modify task, tracker, handoff, cycle-index, or audit state.

## 4. Synchronization

- `git stash push --include-untracked -m "codex-preserve-preexisting-controls-and-M06-C001-log-before-sync"` preserved the dirty control-plane files, the untracked event index, and this newly created log.
- `git merge --ff-only origin/main` fast-forwarded `main` from `de4f2556a51e9b2fa49c215c3afea0d087ab3468` to `c4682b0eab42f5f577f6d58a3ecd6ceab832f8e1`.
- First `git stash apply --index stash@{0}` attempt failed because PowerShell interpreted the unquoted stash selector; no repository content was changed by that failed command.
- Retried as `git stash apply --index 'stash@{0}'`; it restored the preserved files and reported expected conflicts only in `.hiveai/EVENTS.jsonl`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`.
- Resolved those exact conflicts in favor of the preserved pre-existing local versions, then unstaged them. `.hiveai/PROJECT.json`, `.hiveai/EVENTS.jsonl`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and untracked `.hiveai/EVENT_INDEX.json` remain outside the M06 implementation scope.
- Post-sync branch: `main` tracking `origin/main`; no ahead/behind divergence.

## 5. Implementation plan and contracts

- Read the current M00-M05 source contracts, including `GenerationRequest`, `GenerationResult`, `DeterministicRNG`, `MaskCandidate`, `RuleCandidate`/`RuleCanvas`, `WFCCandidate`/`ExemplarRegistry`, and the independent generator entry points.
- Added `GeneratorMode.AUTO` while retaining the existing canonical request schema/version and existing mode serialization behavior.
- Added `generators/router/` with `GeneratorRouter`, `HybridGenerator`, `HybridStrategy`, immutable stage/attempt metadata, and a reproduction helper.
- Explicit routes return the underlying accepted engine candidate/result without fallback. HYBRID child requests resolve outer dimensions/palette once, derive independent stage seed strings from named root domains, and invoke each accepted engine with `DeterministicRNG(stage_seed)` whose domain is `root`.
- Implemented all four required strategies: `MASK_GEOMETRY_RULE_COLOR_REGIONS`, `RULE_GEOMETRY_MASK_SYMMETRY`, `RULE_BASE_WFC_DETAIL`, and `MASK_BASE_WFC_DETAIL`. Composition is logical-grid-only; exact topology, palette, dimension, and component-quality gates reject rather than repair invalid output.
- AUTO uses strict `auto` options, preserves candidate order, deterministically selects through `auto/selection`, and only cycles fallback candidates when explicitly enabled. The final result wraps the original AUTO request and retains outer-root provenance.

## 6. Commands, tests, and evidence

- Initial import probe without `PYTHONPATH=src` failed with `ModuleNotFoundError`; reran with the repository's `src` path and import succeeded. This was an environment invocation correction, not a product failure.
- First M06 focused test run found one incorrect test assumption: a valid MASK seed may return `RETRY_EXHAUSTED`; the test was corrected to compare the explicit router result with the direct engine result and preserve truthful failure propagation.
- First full-suite run found two issues: the new topology-test fixture did not contain a singleton region, and the pre-existing M02 request test still asserted that AUTO must be rejected. The fixture was corrected and the obsolete AUTO rejection case was removed because M06 intentionally adds AUTO.
- Focused M06 run after corrections: 10 passed; subsequent cross-process/offline additions: 8 M06 router tests passed.
- After strict nested-option validation was added, the regenerated M06 evidence and focused suites passed: 11 tests passed (including the 24-case acceptance matrix, golden checks, review validation, cross-process, and offline checks).
- Review builder regenerated `review/m06/m06_review_manifest.json` and `review/m06/M06_HYBRID_CONTACT_SHEET.html`; JSON validation passed and the manifest contains 14 accepted candidates across all four strategies, all four difficulties, and rectangular cases.
- `tests/golden/test_m06_hybrid_golden.py` validates four deterministic hybrid goldens, including both robust strategies, a rectangle, and VERY_HARD dimensions.
- `tests/acceptance/test_m06_hybrid_acceptance.py` validates 24 accepted deterministic replays across the two robust strategies, four difficulties, rectangles, and three seeds per case.
- Standalone package import passed. M06 source-policy scan found no resize/resample/interpolation, subprocess, eval/exec, global-random, or Python-hash use. `git diff --check` passed.
- `pip check` reported the pre-existing environment mismatch `pytest-asyncio 0.24.0 requires pytest<9,>=8.2 but pytest 9.1.1 is installed`; M06 adds no dependency and this was not changed.
- Full repository regression before the final strict nested-option validation patch: **241 passed, 1 warning** in 184.41 seconds. The warning is the pre-existing pytest cache permission warning on this Windows checkout. A final full regression is pending after that source patch.
- Final full repository regression after all source, test, and evidence changes: **241 passed, 1 warning** in 184.82 seconds. The warning is the pre-existing pytest cache permission warning on this Windows checkout.

## 9. Safety and publication

- No runtime dependency, network access, cloud service, owner-approved exemplar, subprocess, eval/exec, global random source, Python hash behavior, resize/resample/interpolation, or M07+ implementation was added.
- The main ScrubBots repository was not accessed or modified. Task, tracker, H!veAI acceptance, prompt, audit, and cycle-index state remain untouched.
- Pending: stage only M06 implementation/tests/review/golden files and this matching log, commit the implementation, push `main`, then publish the completed log in a log-only commit. The log-only commit will not be amended merely to place its own final SHA inside itself; final local/origin equality will be checked and recorded as the terminal publication checkpoint.

## 7. Files changed

- This builder log (created before source, test, golden, review, or documentation edits).
- `src/scrubbots_pixel_factory/core/request.py`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/generators/__init__.py`
- `src/scrubbots_pixel_factory/generators/router/__init__.py`
- `src/scrubbots_pixel_factory/generators/router/hybrid.py`
- `src/scrubbots_pixel_factory/generators/router/router.py`
- `tests/unit/test_m02_request.py` (removed the obsolete pre-M06 AUTO rejection assertion only).
- `tests/integration/test_m06_router.py`
- `tests/integration/test_m06_review_evidence.py`
- `tests/acceptance/test_m06_hybrid_acceptance.py`
- `tests/golden/test_m06_hybrid_golden.py`
- `tests/golden/m06_hybrid_goldens.json`
- `review/m06/build_review.py`
- `review/m06/m06_review_manifest.json`
- `review/m06/M06_HYBRID_CONTACT_SHEET.html`

## 8. Final publication checkpoint

Pending implementation, verification, commit, push, and final local/origin equality check.
