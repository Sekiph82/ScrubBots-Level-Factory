# SB-CP00-007-C001 - Publisher Dry-Run / Validation Gate

Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-04 15:04:01 +03:00 — Child start

- Active authority: live M11 master prompt authorizes this child seventh, after CP001..006 have implementation and regression evidence published.
- Execution root: %TEMP%\ScrubBots-Level-Factory\M11-CP00-003-009-MASTER; starting SHA 5cf395f98b2ef102e3d59bb96316c753183157e4 equals origin/main. Persistent Desktop checkout remains untouched.
- Read child-007 prompt and criteria; scope is a deterministic pre-mutation plan and validation gate based on content evidence, target, replayed release state, non-secret capability, and explicit approval. No live mutator is authorized.
### 2026-10-04 — CP007 implementation and focused verification

- Added a versioned local publication plan with fixed serialization, content digest binding, target/capability identity, deterministic operation and check ordering, replay snapshot binding, explicit owner approval, and a permanent `remote_mutation_performed=false` result.
- Production planning requires an accepted replay and exact staged staging record matching content ID and digest; it represents promotion only. The plan API accepts a non-secret capability data model, not a provider or mutator object.
- Added a stale-plan recheck against current target, replayed state, and digest. Secret-like material in descriptor, payload bytes, target, or capability identity causes plan rejection; fixed-schema serialization excludes caller mappings and does not echo their values.
- Added fail-closed `--dry-run` CLI report. Since no CLI event-evidence format is defined, missing descriptor/payload/replay/approval evidence is reported as rejected, remote mutation false, and exit code 1. The existing `--validate-only` command remains.
- Added the versioned plan JSON schema, README contract notes, public API exports, and CP007 tests.
- Initial focused command `python -m pytest tests/unit/test_sb_cp00_007_publication_plan.py -q`: 7 passed. Expanded CP007 + CP001..006 + governance command: 122 passed in 1.48s.
- No remote provider or network code was added; no `TASKS.md` or audit path was edited.
- After adding the final stale replay and payload-secret cases and recording the complete non-secret capability tuple, the expanded CP007 + CP001..006 + governance suite passed again: 122 passed in 2.40s.
- `python -m compileall -q content_pipeline/src/scrubbots_content_pipeline`: PASS.
- `python -m json.tool content_pipeline/schemas/v1/publication-plan.schema.json`: PASS.
- `git diff --check`: PASS (Git emitted expected LF-to-CRLF working-copy notices only).
- Full repository regression command started: `python -m pytest -q`.
- Final review tightened state eligibility: a staging plan with an existing record now requires that exact record to be replayed as `VALIDATED`; production promotion requires its exact staging source as `STAGED`. An initial full run on the pre-tightening code passed 1284/3 in 1102.96s; it is superseded by the final run below.
- Final CP007 + CP001..006 + governance regression after the state gate: 123 passed in 1.59s. Compileall, JSON schema parse, and `git diff --check` passed again.
- Final full regression command started on the final implementation: `python -m pytest -q`.
- Final full repository regression on the state-gated implementation: `python -m pytest -q` -> 1285 passed, 3 skipped, 0 failed in 1037.58s (17:17). Skips: `tests/integration/test_maint_supply_pipeline_v01.py:232` (`SCRUBBOTS_SLOW=1`); `tests/unit/test_sb_lf03_002_compact_solver_state.py:274` (canonical ScrubBots capability not supplied); `tests/unit/test_sb_lf04_012_regression.py:222` (canonical ScrubBots capability not supplied; no bridge exercised).
- No runtime network, provider operation, credential retrieval, or mutation canary call occurred. The CLI test verifies rejected missing-evidence report, `remote_mutation_performed=false`, nonzero exit, and empty stderr.
- Final input-hardening review also requires `current_state` to be a typed snapshot present in the accepted replay before it can satisfy the currentness gate. Invalid state inputs are represented by a non-sensitive invalid sentinel and are not echoed.
- Final focused CP007 + CP001..006 + governance run after this hardening: 124 passed in 0.92s. Compileall, JSON schema parse, and diff check passed.
- Full repository regression rerun started against the exact final implementation: `python -m pytest -q`.
- Final full repository regression on the exact committed candidate: `python -m pytest -q` -> 1286 passed, 3 skipped, 0 failed in 968.79s (16:08). Skips: `tests/integration/test_maint_supply_pipeline_v01.py:232` (`SCRUBBOTS_SLOW=1`); `tests/unit/test_sb_lf03_002_compact_solver_state.py:274` (canonical ScrubBots capability not supplied); `tests/unit/test_sb_lf04_012_regression.py:222` (canonical ScrubBots capability not supplied; no bridge exercised).
- Implementation files: README, public API exports, `publication_plan.py`, the `--dry-run` CLI report, publication-plan v1 schema, and CP007 tests.
- Implementation commit: `96652d5610855a9a46a9a2352088c5bfea06c704`.
- Push result: normal non-force `HEAD:main` push succeeded. After fetch/prune, local HEAD and `origin/main` both equal `96652d5610855a9a46a9a2352088c5bfea06c704`; divergence `0 0`.
- Protected tracker/audit paths were not edited. Execution checkout remains detached in the authorized master worktree; persistent Desktop checkout remains untouched.
