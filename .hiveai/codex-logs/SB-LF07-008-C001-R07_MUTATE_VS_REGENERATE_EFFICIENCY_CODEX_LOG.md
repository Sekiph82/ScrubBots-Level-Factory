# SB-LF07-008-C001-R07 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-27T11:20:51+03:00.
- Canonical repository: https://github.com/Sekiph82/ScrubBots-Level-Factory.
- Canonical branch: `main`.
- Canonical Level Factory root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Starting HEAD after safe fast-forward to live `origin/main`: `bad960fbd0bb7a3f4e69641821bc1ec21de0c1d6`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; local HEAD equals `origin/main` at scope start.
- Initial tracked status: clean; pre-existing owner/untracked files were preserved and not staged.
- Protected-file proof at task start: no `TASKS.md` or `.hiveai/audits/**` diff.

## Authority and scope read

- Read the live R07 master prompt from the supplied GitHub URL, the R07 remediation index, and the dedicated SB-LF07-008 R07 prompt.
- Read root `TASKS.md`, `AGENTS.md`, and `GOVERNANCE.md`.
- Read the R06 strict re-audit for SB-LF07-008 and the prior R06 builder evidence.
- Scope is limited to SB-LF07-008. Frozen PASS/CLOSED tasks 001, 002, 003, 004, 005, 006, 007, and 009 remain untouched.

## Implementation

- Pending. R07 sealed producer-derived generation provenance, exact parent binding, forged-payload rejection, and retained seed/config mismatch coverage will be recorded chronologically below.

- 2026-09-27T11:24:00+03:00 — Initial focused collection command `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_008_efficiency.py tests/unit/test_sb_lf07_010_regression.py` failed during import because the new sealed dataclass used `field` without importing it. No test body ran; corrected the import in `mutation_base.py` immediately.

## Implementation and evidence

- Added factory-owned `SealedGenerationProvenance` in the immutable mutation substrate. Its only construction path accepts an actual successful `GenerationResult`, derives the exact `GenerationRequest` digest and `GenerationResult` digest internally, records generator id/version/mode, seed, config identity, and binds the seal to the exact `CandidateIdentity`.
- Added immutable parent binding APIs. `MutationCandidate` rejects unsealed or wrong-parent provenance; payload fields such as `generation_request_digest` are never consulted by workload authority. The shared workload constructor remains the sole route identity constructor.
- Rebuilt the aligned fixture through `GeneratorRouter().generate(generation_request)` and `parent.with_accepted_generation_result(result)`. The mutation route and regeneration route now match only through that accepted result-derived seal.
- Added R07 adversarial tests for forged raw payload SHA rejection, wrong-parent binding, tampered request/result digest rejection, and a sealed result for another request. R06 seed-A/workload-seed-B, same-seed configuration mismatch, missing provenance, accounting, source, safety, governance, and Palette V3 regressions remain retained.
- 2026-09-27T11:26:00+03:00 — Corrected focused R06/R07 suite: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_008_efficiency.py tests/unit/test_sb_lf07_010_regression.py` — `12 passed`.
- 2026-09-27T11:29:00+03:00 — Final focused R07 suite after adversarial additions — `17 passed`.
- 2026-09-27T11:31:00+03:00 — Affected M07 004–010 gate — `38 passed`.
- 2026-09-27T11:33:00+03:00 — Retained M03/M04/M05/M06/Palette V3 gate — `296 passed, 2 skipped`; both skips were accepted canonical ScrubBots capability gates.
- 2026-09-27T11:39:00+03:00 — Full repository pytest — `1044 passed, 2 skipped in 334.00s`; both skips were accepted canonical ScrubBots capability gates.
- 2026-09-27T11:40:00+03:00 — `python -m compileall -q src tests` passed.
- 2026-09-27T11:40:00+03:00 — `godot_console.exe --headless --path level_factory --editor --quit` passed on Godot 4.7.2.
- 2026-09-27T11:41:00+03:00 — `git diff --check` passed; protected-file proof `git diff --name-only -- TASKS.md .hiveai/audits` returned no paths.

## Publication state

- Product implementation commit: `773ac25042917f7f8fd57e9794f0c75373f9a4f7`.
- The shared implementation and SB-LF07-008 test changes were pushed with the sequential SB-LF07-010 test commit; final product HEAD before task-log publication was `0a44806b98b27fb634ad62d2f11497e6f2166fce`, equal to `origin/main`.
- Changed implementation/test files for this task: `src/scrubbots_pixel_factory/mutation_base.py`, `src/scrubbots_pixel_factory/mutation_workload.py`, `src/scrubbots_pixel_factory/m07_services.py`, `tests/unit/test_sb_lf07_004_revalidation.py`, and `tests/unit/test_sb_lf07_008_efficiency.py`.
- No dependency, license, runtime-network, provider-spend, TASKS, audit, or frozen-task changes were made. Existing owner/untracked files were preserved and not staged.
- This is builder evidence only. No task, milestone, sprint, or M07 status was self-promoted to PASS/CLOSED.
