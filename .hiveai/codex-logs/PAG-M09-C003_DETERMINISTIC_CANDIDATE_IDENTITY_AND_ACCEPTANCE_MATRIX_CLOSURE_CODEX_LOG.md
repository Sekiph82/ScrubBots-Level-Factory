# PAG-M09-C003 — Deterministic Candidate Identity & Acceptance Matrix Closure
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-11T10:24:53.2625005+03:00.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Authorized local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Starting HEAD: `a10c77232f577a1d8c3f05d7855e318e5f0829e3`.
- Starting `origin/main`: `a10c77232f577a1d8c3f05d7855e318e5f0829e3`.
- Starting divergence: `0 0` (ahead/behind).
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial status preserved as pre-existing user dirt:
  - modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`
  - modified `docs/migration/legacy-task-trackers/PROJECT.json`
  - untracked `.hiveai/EVENT_INDEX.json`
  - untracked `.hiveai/HANDOFF.md`
  - untracked `.hiveai/STATE.json`
- Synchronization was non-destructive: origin was fetched, the fast-forward was applied, and pre-existing dirt was restored. No reset, rebase, force-push, clean, sibling repository, or task-state edit was used.

## Authority and scope

- Read directly from GitHub `main`: the authoritative PAG-M09-C003 prompt, the PAG-M09-C002 strict audit, the PAG-M09-C002 builder log, and root `TASKS.md`.
- Read locally after synchronization: `AGENTS.md`, `GOVERNANCE.md`, `tasks.md`, `.hiveai/CYCLE_INDEX.md`, the current M09 CLI/tests, and accepted M08 bundle/artwork contracts.
- The GitHub-first migration does not provide `.hiveai/PROJECT.json` or `.hiveai/RULES.md` in the current checkout; this absence is recorded and no legacy local control-plane file was used as current authority.
- Scope is limited to PAG-M09-C003 and F-PAG-M09-C002-001/F-PAG-M09-C002-002. Root `TASKS.md`, task acceptance state, prompts, audits, prior logs, M03-M08 production algorithms, M10, M11, and the main ScrubBots repository are out of scope.

## Planned work

- Centralize and enforce the deterministic accepted batch candidate-ID/path formula during generation, manifest validation, accepted-record validation, bundle binding, and replay.
- Complete the named direct reproduce, deterministic acceptance, path, corruption, seed, quality, and cross-process evidence matrix without weakening M08 validation.

## Chronological record

Implementation decisions, commands, failures/corrections, tests, changed files, dependency/offline/security checks, commits, publication, and final `HEAD == origin/main` verification will be appended truthfully as work completes.

## Implementation record

- Added `_batch_candidate_id()` as the single deterministic `<batch-id>-<zero-padded-attempt-index>` helper. New accepted candidates, accepted-attempt validation, accepted-record validation, bundle/path binding, and deterministic replay all use this helper.
- Accepted IDs and paths are now required to match the validated immutable batch ID and attempt index, in addition to existing syntax, uniqueness, request, seed, hash, dimension, policy, and M08 checks.
- Added direct C003 evidence for the coordinated internally-valid M08 candidate-ID/path rewrite, all remaining reproduce corruption classes, exact single-request byte stability/default IDs, auto dimensions, invalid mode/options, exact single quality rejection, every attempt seed, unique deterministic multi-accepted IDs, different root accepted sets, absolute/non-portable paths, bundle hash/seed cross-binding, forged terminal states, and duplicate accepted identities.
- Preserved C002's separate-process batch byte-equality test under two `PYTHONHASHSEED` values and added the C003 deterministic helper assertions.

### Focused test checkpoint

- Initial command: `python -m pytest -q tests/unit/test_m09_cli.py tests/integration/test_m09_cli_integration.py`
- Initial result: 3 fixture failures (chosen roots `914/915` did not both reach two accepted candidates; seed `917` produced a bounded generator failure; changed-grid fixture supplied an unsupported `used_palette` argument and then an invalid six-color grid).
- Corrections: selected known bounded seeds with accepted candidates, used a successful explicit seed, and built the changed-grid result through the existing `GenerationResult.success()` contract with a valid color count. No production algorithm was changed for these corrections.
- Corrected command result: PASS — 56 tests passed (one pre-existing Windows pytest cache permission warning).

### Required verification

- Command: `python -m compileall -q src tests`
- Result: PASS.
- Command: `python -c "import scrubbots_pixel_factory as package; print('IMPORT_OK', package.__name__)"`
- Result: PASS — `IMPORT_OK scrubbots_pixel_factory`.
- Command: `python -m scrubbots_pixel_factory.cli --help`
- Result: PASS — standard-library CLI help listed `generate`, `reproduce`, and `batch`.
- Command: `scrubbots-pixel --help`
- Result: PASS — existing installed console command produced the same CLI help.
- Command: `git diff --check`
- Result: PASS (only expected CRLF conversion warnings from Git for edited text files).
- Command: `python -m pytest -q tests/unit/test_m08_output.py tests/integration/test_m08_export_integration.py tests/golden/test_m08_export.py tests/integration/test_m03_generator.py tests/integration/test_m04_generator.py tests/integration/test_m05_wfc_generator.py tests/integration/test_m06_router.py tests/integration/test_m07_generator_compatibility.py tests/integration/test_offline_boundary.py tests/unit/test_m09_cli.py tests/integration/test_m09_cli_integration.py`
- Result: PASS — 128 tests passed in 2:32.65 (one pre-existing pytest cache permission warning).
- Command: `python -m pytest -q`
- Result: PASS — 347 tests passed in 3:34.10 (one pre-existing pytest cache permission warning).
- The M09 integration suite directly covers every C003 named acceptance/reproduce/path/corruption case, including the coordinated internally-valid M08 candidate-ID rewrite and real two-`PYTHONHASHSEED` batch byte equality.

### Files and boundaries

- Product file changed: `src/scrubbots_pixel_factory/cli/main.py` only; no M03-M08 production algorithm changed.
- M09 evidence changed: `tests/integration/test_m09_cli_integration.py`.
- M09 documentation changed: `README.md`.
- This C003 log is the only new control-plane artifact; root `TASKS.md`, prior prompts, audits, logs, `.hiveai/CYCLE_INDEX.md`, and legacy tracker files were not modified.
- Runtime dependencies remain zero; no network, telemetry, API key, unsafe deserialization, resizing, interpolation, third-party asset, or runtime dependency was introduced.

### Final pre-commit scoped check

- Command: `git diff --check`
- Result: PASS; only Git’s expected LF/CRLF conversion warnings were emitted.
- Scoped working diff before commit: `README.md` (2 insertions), `src/scrubbots_pixel_factory/cli/main.py` (26 insertions/changes), and `tests/integration/test_m09_cli_integration.py` (216 insertions). The C003 log is a new file. Pre-existing modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, `docs/migration/legacy-task-trackers/PROJECT.json`, and untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json` remained outside the scoped change.

## Publication and terminal checkpoint

- Implementation commit: `9d29c46ffad083158e33ae227191a72920445a86` (`Close M09 C003 candidate identity and acceptance matrix`).
- `git push origin main`: PASS — `a10c772..9d29c46` published normally without force-push.
- After publication, executed `git fetch origin`, `git rev-parse HEAD`, `git rev-parse origin/main`, and `git rev-list --left-right --count HEAD...origin/main`.
- Observed checkpoint: local HEAD `9d29c46ffad083158e33ae227191a72920445a86` == `origin/main` `9d29c46ffad083158e33ae227191a72920445a86`; divergence `0 0`; branch `main`.
- Final status retained only the pre-existing user changes listed above; all C003 scoped files were committed.
- Builder evidence only: no audit, acceptance declaration, task/tracker state change, M10/M11 work, legacy tracker revival, M03-M08 production change, or main ScrubBots repository access occurred.
