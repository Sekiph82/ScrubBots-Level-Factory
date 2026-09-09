# PAG-M06-C002 — WFC Remap, Stage Replay & Router Evidence Remediation
Document role: CODEX BUILDER LOG

## 1. Start and authority

- Start timestamp: 2026-09-09T23:49:09+03:00 (Europe/Istanbul).
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Repository URL: https://github.com/Sekiph82/ScrubBots-Level-Factory
- Branch: `main`.
- Authoritative remediation prompt read directly from GitHub: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_PROMPT.md
- Previous independent strict audit read directly from GitHub: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M06-C001_HYBRID_GENERATOR_ROUTER_STRICT_AUDIT.md
- Canonical local execution workspace: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- The main `ScrubBots` repository was not accessed or modified.

## 2. Initial Git checkpoint

- Starting local HEAD: `318b97b9c33a3b35a2ef6bbde9b348331cf74b83`.
- `origin`: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Fetched `origin/main`: `5ad8188` (full SHA to be recorded after synchronization).
- Starting relation after fetch: local `main` was 0 ahead and 11 behind `origin/main`.
- Initial status: pre-existing dirty legacy workspace projections `.hiveai/EVENTS.jsonl`, `.hiveai/HANDOFF.md`, `.hiveai/PROJECT.json`, `.hiveai/STATE.json`, plus untracked `.hiveai/EVENT_INDEX.json`. These are preserved, not used as task authority, and excluded from C002 commits.
- Existing stashes were inspected and preserved.

## 3. Required GitHub-first v3 reads

Read completely from the authorized GitHub branch:

- `.hiveai/PROJECT.json`
- `.hiveai/RULES.md`
- the machine block in `.hiveai/TASKS.md`
- `.hiveai/EVENTS.jsonl`
- `tasks.md`
- `.hiveai/CYCLE_INDEX.md`
- `AGENTS.md`
- `GOVERNANCE.md`
- C001 builder log
- C001 strict audit
- current M06 router/hybrid source, tests, review manifest/contact sheet, and goldens
- this C002 remediation prompt

The v3 GitHub machine block is the sole current-state authority. Removed legacy `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and `.hiveai/PROJECT_DASHBOARD.md` are not used for task selection or acceptance state.

## 4. Synchronization

- Preserved pre-existing dirty control-plane projections and untracked legacy files with an include-untracked stash before synchronization.
- Fast-forwarded `main` non-destructively from `318b97b9c33a3b35a2ef6bbde9b348331cf74b83` to `5ad81886669e4f8cfa2247a689439a2186ad1b50`, with no rebase, reset, force-push, or discard operation.
- Applying the preservation stash produced expected conflicts only in `.hiveai/EVENTS.jsonl`, `.hiveai/PROJECT.json`, and upstream-deleted legacy `.hiveai/HANDOFF.md`/`.hiveai/STATE.json`; restored the stashed versions, staged only to mark conflict resolution, then unstaged them. The legacy files remain local untracked files and are not authority.
- Post-sync origin and local `main` matched at `5ad81886669e4f8cfa2247a689439a2186ad1b50`; pre-existing projections remain excluded from all C002 commits.
- No tracker, task, event, cycle-index, prompt, or audit file was edited.

## 5. Bounded C002 scope

- Implemented only the four audited findings: preserved caller/default WFC source-to-target palette remapping for both WFC-detail strategies; implemented metadata-driven replay and corruption rejection for every engine/helper stage and final digest; added complete AUTO selection/fallback/explicit-HYBRID evidence; and added actual before/after/final topology review data/panels plus a WFC-detail golden using a synthetic test-only exemplar.
- WFC detail now leaves `palette_mapping` absent when omitted so M05 performs its canonical mapping, while preserving supplied mappings unchanged. Composition stages are explicitly typed `COMPOSITION` with truthful helper IDs `rule-colorize` and `mask-symmetry-compose`.
- Replay reconstructs child requests from canonical metadata, rederives root-derived stage seeds, reruns each engine/helper, verifies stage order, engine identity/version, child request/result/geometry digests, engine-specific metadata including WFC pattern/mapping evidence, and final topology/grid/result digests.
- Review output contains before/after/final occupancy arrays and three visual panels per candidate. The 14-entry review pack includes two WFC-detail entries with the synthetic fixture and explicit ownership classification; no production exemplar was added.

## 6. Commands, tests, and evidence

- Created this matching log before any C002 source, test, golden, review, or generated-evidence edit.
- Initial C002 focused run after implementation: `python -m pytest tests/integration/test_m06_router.py tests/golden/test_m06_hybrid_golden.py -q` had 1 expected stale-golden failure because the corrected composition helper ID changed from `rule-colorize` to `mask-symmetry-compose`.
- Added adversarial tests for non-identity/default WFC mappings, AUTO seeded diversity, fallback success with failed-attempt metadata, bounded all-fail behavior, explicit HYBRID route equality, and seven replay-corruption classes (stage seed, child request digest, engine version, child result digest, geometry digest, WFC pattern-table digest, and final grid digest).
- Regenerated `review/m06/m06_review_manifest.json` and `review/m06/M06_HYBRID_CONTACT_SHEET.html`; generated five M06 goldens including WFC-detail metadata, synthetic exemplar identity/ownership, and source-to-target mapping.
- Corrected generated JSON serialization of immutable topology metadata and tuple/list test comparisons. Focused M06 router/review/golden suite: `16 passed`.
- M06 acceptance plus focused suite: `17 passed`, including the 24-case robust strategy matrix.
- Full regression: `python -m pytest -q --disable-warnings` -> `247 passed, 1 warning` in `190.69s`.
- Standalone import check: `python -c "import scrubbots_pixel_factory; ..."` -> `import ok`.
- Offline/source-policy scan of `src/scrubbots_pixel_factory/generators/router` for resize/resample/interpolation, subprocess/eval/exec, non-project randomness, and built-in hash use: no matches.
- M07+ scope scan over M06 implementation, review, and tests: no matches.
- `git diff --check`: passed; only Git line-ending normalization warnings were emitted.
- Dependency check: `python -m pip check` failed on the pre-existing environment mismatch `pytest-asyncio 0.24.0` requiring `pytest<9,>=8.2` while installed pytest is `9.1.1`; no dependency files were changed to conceal or alter this unrelated environment condition.
- Safety observations: core generation remains offline-only; no network/runtime dependency, cloud API, credential, upstream artwork, upstream runtime, or main ScrubBots repository access was added.

## 7. Publication

- Staged only the eight implementation/review/test artifact paths listed by `git diff --cached --stat`; preserved `.hiveai/EVENTS.jsonl`, `.hiveai/PROJECT.json`, `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json` were not staged.
- Implementation commit: `2c786e4` (`remediate M06 WFC remap replay and evidence`).
- Implementation push: `git push origin main` succeeded, updating GitHub `5ad8188..2c786e4`.
- This completed log is being published in a separate log-only commit; its own terminal SHA is intentionally not inserted into the log. ChatGPT/H!veAI can independently record terminal repository HEAD.
- No task/tracker/event/cycle-index/audit state or prompt was modified, and the main ScrubBots repository was not touched.
