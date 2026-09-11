# PAG-M10-C002 — Executed Property Corpus, Performance Methodology & Release Evidence Remediation
Document role: CODEX BUILDER LOG

## Start checkpoint

- Actual start timestamp: 2026-09-11T12:24:07.1331417+03:00.
- Canonical authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`, branch `main`.
- Authorized local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Local HEAD at start: `2496e9299cbe9e073789c5c2276f11737d9999c8`.
- `origin/main` at start: `2496e9299cbe9e073789c5c2276f11737d9999c8`.
- Divergence at start: `git rev-list --left-right --count HEAD...origin/main` = `0 0`.
- Remote: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial local dirt, preserved and excluded from C002 scope: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl` and `docs/migration/legacy-task-trackers/PROJECT.json`; untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`.
- Stashes and the single local worktree were inspected. No sibling repository was accessed.
- This matching log was created before any C002 source, test, report, or review-artifact edit and its existence was verified before continuing.

## Authority and scope read

- Read directly from GitHub: the authoritative C002 remediation prompt, the C001 strict audit, the C001 builder log, and root `TASKS.md`.
- Read local builder/governance instructions relevant to this cycle: `AGENTS.md`, `GOVERNANCE.md`, and the current repository files required by the prompt. Root `TASKS.md` was not edited. Hidden legacy tracker files were not used as authority.
- C002 scope is limited to executed validation evidence, distinct benchmark methodology, review metrics/selection evidence, PAG-1035..PAG-1049 gate evidence, attribution re-audit depth, focused tests, and this log. Accepted M03-M09 production algorithms and the main `C:\Users\sekip\Desktop\ScrubBots` repository are out of scope.

## Planned execution

- Revise the M10 tool to execute every advertised valid corpus request and invalid/batch case.
- Replace repeated-request measurements with deterministic distinct seed/config manifests, including 20-case RULES 59x59 and bounded WFC/WFC-bearing HYBRID coverage beyond EASY.
- Preserve the existing 100 logical review grids where possible while binding the declared root seed and selection formula truthfully; publish the required metrics reports and complete PAG-1035..PAG-1049 matrix.
- Run focused C002 tests, full regression, compile/import/CLI/offline checks, commit/push, and record final equality/divergence.

## 2026-09-11 — First execution attempt

- `python -u tools/m10_prepare.py` was started to execute the full revised corpus. The initial distribution (900 MASK, 900 RULES, 120 HYBRID, 80 AUTO plus technical/59x59 cases) was too slow on the actual laptop because it still devoted 900 cases to the more expensive RULES path. The bounded run was stopped before artifact publication; no production contract failure was observed.
- This is recorded as a methodology correction. The corpus will be reweighted toward the fast MASK path while retaining >=2,000 executable valid requests, every mode/difficulty, explicit square/rectangular/auto coverage, synthetic WFC coverage, and explicit 59x59 cases. Distinct benchmark requirements remain unchanged.
- The reweighted full run was also stopped after approximately four minutes while it was still executing repeated deterministic replays. The tool was corrected to execute every advertised corpus request exactly once, validate every successful result directly, and perform two replay probes per mode/difficulty. This keeps the required >=2,000 execution evidence practical without claiming an unexecuted corpus; the replay-probe counts and any mismatch are reported explicitly.
- The corrected full corpus completed and wrote its execution report; the distinct benchmark phase completed and wrote its 404-case matrix/raw samples. Review-pack regeneration then stopped at deterministic slot `EASY/18` with bounded `RETRY_EXHAUSTED`. This is a valid generator outcome, not a contract defect. The selector is being corrected to advance through deterministic per-slot retry seeds and retain the failed attempt in the required attempt ledger.

## 2026-09-11 — C002 implementation and evidence completion

- The review selector was corrected to derive `slot/{difficulty}/{slot:02d}/attempt/{attempt:02d}` seeds from `DeterministicRNG("m10-review-root-v2")`, to select the first acceptable non-duplicate result within eight bounded attempts, and to retain every rejected attempt in `M10_METRICS_REPORT.json`. Mode selection is truthfully `(slot + attempt) modulo 4`; no grid is mutated or resized.
- A first focused verification run exposed seven repository-test compatibility defects in the newly generated evidence: literal unexpanded HTML placeholders, an invalid-case fixture that was still accepted, two representative tests choosing a known-rejecting HYBRID strategy, an old performance-field expectation, and an owner-gate compatibility shape. These were corrected in the C002 evidence generator/tests; no M03-M09 production algorithm was changed. The invalid corpus was then rebuilt and actually executed again, with all nine cases rejected without traceback.
- `review/m10/M10_PROPERTY_CORPUS.json` contains `2018` valid cases and the execution report records `2018/2018` executed, `1988` successful results, `30` bounded `RETRY_EXHAUSTED` results, zero successful-result contract mismatches, and `9/9` invalid cases rejected without traceback. Counts cover MASK, RULES, HYBRID, AUTO and synthetic technical WFC across all four difficulties.
- `review/m10/M10_BENCHMARK_MANIFEST.json` contains `404` distinct request/config cases across `29` groups. Each MASK, RULES and robust non-WFC HYBRID difficulty group has 20 cases; each WFC difficulty group has 10 technical cases; each WFC-bearing HYBRID strategy/difficulty group has 3 cases beyond EASY; and the RULES 59x59 PAG-0441 group has 20 distinct cases. `M10_PERFORMANCE_REPORT.json` records nearest-rank p95, peak tracemalloc memory, quality/failure/retry rates, raw samples, and proposed-only budgets derived from each measured distribution. PAG-0441 measured median is `2746502400 ns`, nearest-rank p95 is `9900434500 ns`, and peak memory is `806102` bytes; no budget was self-approved.
- The regenerated review pack contains exactly 100 logical candidates: EASY 25, MEDIUM 25, HARD 25 and VERY_HARD 25. All remain `PENDING_OWNER_REVIEW`, exact grid hashes are unique, and the pack covers MASK (35), RULES (25) and HYBRID (40). WFC visuals remain skipped with `WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR`.
- The generated owner-review selection ledger contains `122` attempts: 100 accepted, 22 retry rejections (`RETRY_EXHAUSTED`), and zero duplicates. The metrics report includes per-attempt seed, request digest, status, rejection code, dimensions, family/recipe/strategy counts, M07 structural summaries, deterministic nearest-neighbor occupancy/color evidence, and the zero-grid-mutation statement. `M10_METRICS_REPORT.json` and `.md`, complete PAG-1035..PAG-1049 gate evidence, and the per-pinned-reference attribution re-audit were regenerated.

## Verification results

- Focused C002 and retained M10 evidence tests: `31 passed`.
- Full repository regression: `python -m pytest -q` -> `378 passed, 1 warning in 214.05s`; the warning was the pre-existing Windows pytest-cache permission warning under `.pytest_cache`.
- `python -m compileall -q src tests`: passed.
- Standalone `scrubbots_pixel_factory` import: passed.
- `python -m scrubbots_pixel_factory.cli --help`: passed.
- Installed `scrubbots-pixel --help`: passed.
- `git diff --check`: passed; only expected Git LF-to-CRLF working-copy warnings were emitted.
- Offline/source scan found no runtime network dependency markers in product source; the existing `offline.py` socket guard is intentional boundary code. No dependency or license change was made.

## Files changed in C002 scope

- Updated `tools/m10_prepare.py` and retained M10 compatibility assertions in the M10 test modules.
- Added C002 execution, distinct benchmark and review-evidence tests under `tests/`.
- Regenerated the deterministic corpus, execution report, distinct benchmark manifest/performance report, 100-candidate review manifest/HTML/metrics, attribution re-audit, and full gate matrix under `review/m10/`.
- This builder log is the only `.hiveai` file in scope. Root `TASKS.md`, hidden legacy tracker files, audit files and the pre-existing unrelated dirty files were not edited.

## Publication checkpoint

- Implementation/artifact commit: `36c9640` (`Implement M10 C002 validation evidence remediation`).
- `git push origin main`: succeeded, updating GitHub from `76a5375` to `36c9640`.
- Immediately after that push, `git fetch origin` and `git rev-list --left-right --count HEAD...origin/main` recorded local `HEAD=36c9640`, `origin/main=36c9640`, divergence `0 0`.
- The completed builder log is published in the following log-only commit; the terminal equality check is repeated after that publication and reported in the final response. No task, acceptance, tracker, audit, or legacy control-plane state was modified.

## Post-publication terminal verification

- After the completed log publication at `737a6da55c853fe29ec65574dab71cbea739cc4f`, `git fetch origin` recorded `HEAD=737a6da55c853fe29ec65574dab71cbea739cc4f`, `origin/main=737a6da55c853fe29ec65574dab71cbea739cc4f`, and `git rev-list --left-right --count HEAD...origin/main` = `0 0`.
- This equality record is published with the final log checkpoint below; the same commands are rerun after that publication. The only remaining local dirt is the pre-existing unrelated legacy-migration modifications and untracked legacy files listed at the start.
