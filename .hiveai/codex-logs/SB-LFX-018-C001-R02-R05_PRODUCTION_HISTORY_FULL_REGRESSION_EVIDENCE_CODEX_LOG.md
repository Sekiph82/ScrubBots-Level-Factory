# SB-LFX-018-C001-R02-R05 — Preserve R04; Close Production History, Full Regression and Evidence

Document role: CODEX BUILDER LOG

## Desktop-only continuation — 2026-10-10

- First recorded task timestamp: 2026-10-10 21:14:52 Europe/Istanbul; turn start preceded this timestamp and was not captured.
- Canonical root verified: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `main`.
- After `git fetch --prune origin`, Desktop started at `3f0a139fb6219c4df61d3e3839b546f59eba27ab`; `origin/main` was `de7deae60b8772689d0948eb960a1d4d81925253` (0 ahead / 5 behind). Incoming file list contained only R05-R01 prompt/audit, M17 audit, and owner-owned `TASKS.md`; no overlap with local untracked paths. Fast-forwarded with `git merge --ff-only origin/main` to `de7deae60b8772689d0948eb960a1d4d81925253` (0/0).
- Initial Desktop status: 57 untracked paths, no tracked modifications. The 57 are preserved unchanged; none are staged, ignored, moved, renamed, rewritten, or cleaned. Existing `Release/` remains untouched. No TEMP worktree was used for execution. Historical R05 builder log was absent from this Desktop checkout; no registered R05-specific worktree was available for recovery.
- Read the live Desktop-only R05-R01 prompt and audit criteria, original R05 prompt and criteria, R04 continuation prompt, root task state, `AGENTS.md`, `GOVERNANCE.md`, standing sync/publish standard, R04 builder log, CP03-008/009 contracts/logs, M14 publisher, M13 manifest-history API, M18 R2 provider, LF handoff and current focused handoff tests.

### KEEP / ADAPT / ADD before implementation

| Disposition | Decision |
|---|---|
| KEEP | R04 native three-screen UI, canonical M14/CP03-008/009 activation path, owner approval gate, CPX-002 replay gate, R03 source/pipeline evidence, and previously reported A/B/C/order/150-import evidence. Do not repeat completed tests or screenshots. |
| ADAPT | Replace LF handoff's existing-production hard stop and empty-history assumption with exact persisted M13 history readback, prior-manifest binding, and successor-history persistence through the canonical provider. |
| ADD | A provider-facing M13 history read/write connection using the existing serialized `ManifestHistoryV1`, plus bounded stateful tests for exact current-manifest binding and successive history readback. |

- Current code finding: `scripts/scrubbots_publish_handoff.py` rejects any existing production manifest because no provider history read API is available, and supplies `ManifestHistoryV1()` for production activation. `r2_provider.py` stores canonical M11 release events but has no M13 history storage API. CP03-009 already verifies canonical M13 history and returns exact successor history in its activation receipt; that authority will remain in use.
- Existing evidence reused without rerun: R04 log reports A READY / B structural REJECTED / C READY, Levels 11→12 contiguous and stable retry-plan hash; 150 distinct PNG import identities with 2 actual SOLVED/WIN/READY and 148 NOT RUN; M17 7/63 and F02 R01 3 PASS. Native Windows chooser, final installed captures, full LF regression, Alpix live gate and live R2 production chain remain unverified/open as reported by source evidence.
- Planned verification is limited to new/changed M13 provider-to-LF handoff tests only. No full pytest, prior focused suites, 150 solver runs, LF19 rerun, screenshots, installer, Godot import or disk cleanup will be repeated.

## R05 implementation and bounded verification

- Added the provider's M13 manifest-history control object at `_control/manifest-history/current.json`, using only the existing `ManifestHistoryV1` parser/serializer and record chain. Reads fail closed when unavailable or malformed. Writes require the exact current production manifest bytes, exact prior history tip, a full valid successor chain, and conditional `If-Match`/`If-None-Match`; no alternative history schema or CP03 publisher was introduced.
- The LF production handoff now reads the M13 history and requires its tip to equal the exact current production manifest/precondition before supplying history to CP03-009. After canonical activation succeeds, the handoff persists the returned exact history and reads it back byte-model-equal before reporting activation complete. A post-activation persistence/readback error reports `mutation_performed=true` and `ACTIVATED_HISTORY_INCOMPLETE` so it cannot be mistaken for a clean rollback.
- Added `tests/unit/test_sb_lfx_018_r05_manifest_history_handoff.py`: a stateful S3-shaped in-memory provider fixture proves N, N+1, N+2 history persistence/readback, monotonic versions, exact current-manifest binding and stale-tip rejection. This is a provider/adapter fixture only; it is not live R2 or a full CP03-008/009 integration run. Updated the existing exact-approval handoff test so an accepted mock without an activation history receipt is correctly treated as post-mutation history-incomplete.
- Files changed: `content_pipeline/src/scrubbots_content_pipeline/provider.py`, `content_pipeline/src/scrubbots_content_pipeline/r2_provider.py`, `scripts/scrubbots_publish_handoff.py`, `tests/unit/test_sb_cpx_004_scrubbots_publish.py`, and new `tests/unit/test_sb_lfx_018_r05_manifest_history_handoff.py`, plus this builder log. No dependencies/licenses, game project, root `TASKS.md`, prompt, audit, or `.hiveai/HANDOFF.md` changes.
- Exact focused command: `python -m pytest -p no:cacheprovider tests/unit/test_sb_lfx_018_r05_manifest_history_handoff.py tests/unit/test_sb_cpx_004_scrubbots_publish.py::test_production_handoff_requires_exact_owner_confirmation_before_assembly -q` with `PYTHONDONTWRITEBYTECODE=1` — **4 passed in 0.22s**. It ran only the three newly added tests and the one directly affected existing test; no project basetemp, cache, external API or live provider call was used.
- `git diff --check` passed. No compileall, full pytest, Godot import/runtime, LF19, native picker, screenshot, installer or Release mutation was run because these are unchanged prior gates or require a separate owner/runtime/live provider gate; no attempt was made to repeat them.
- Security/offline note: provider credentials remain process-only; no credential values were read or logged. The R2 adapter continues to make no runtime call until its configured client is used. This session used only an injected in-memory provider test client and made no network request.

## Evidence matrix and open gates

| Gate | R05 status | Evidence / boundary |
|---|---|---|
| Canonical production history | Focused fixture PASS; live chain NOT RUN | New provider fixture reads back N→N+1→N+2 (versions 3, 4, 5). Real owner-approved R2 CP03-008/009 activation and live provider readback are not claimed. |
| Per-PNG identity and solver binding | PREVIOUS PASS REUSED / 148 NOT RUN | R04 evidence reports distinct real PNG identities and A READY / B structural REJECTED / C READY; only two actual SOLVED/WIN/READY outcomes among 150. No PNG was re-imported or solved here. |
| Contiguous publication order | PREVIOUS PASS REUSED | R04 evidence reports successful levels 11→12 and stable retry plan hash. |
| Source→supply→replay→Difficulty | PREVIOUS PASS REUSED / 148 NOT RUN | Existing A/C success and B structural rejection evidence reused; no cross-binding rerun. |
| Exact-current ScrubBots LF19/VOID | PREVIOUS PASS REUSED | R04 log reports 20 parity tests including the seven required LF19 cases. No game repo access or rerun. |
| Native UI / Windows chooser | UI geometry PREVIOUS PASS REUSED; native Windows picker NOT VERIFIED | No repeated Godot UI run or screenshot. R04 progress states the native chooser visual interaction was not verified. |
| Final R05 durable Release screenshots | NOT RUN | R04 screenshots were tied to the prior installed R04 build. No R05 install/capture or copy was performed after these code changes. |
| Installer/runtime | Prior R04 install PASS REUSED; R05 install NOT RUN | Existing untracked `Release/` preserved byte-for-byte and not overwritten. |
| Full LF pytest / prior solver hang | NOT RUN | The R04 full run did not terminate under authority; its log records unbounded canonical solver calls and an earlier no-authority failure run. No full-suite rerun. |
| Alpix live plugin | NOT RECHECKED; prior R04 report says absent | No plugin install, paid API, or fabricated smoke. Current live plugin availability remains an external gate. |
| Live production owner approval / R2 | NOT RUN | No credentials were inspected and no R2/network mutation or approval was attempted. |

R05 remains `R05_PARTIAL_IMPLEMENTED / OPEN_GATES`; this builder log does not claim audit, milestone acceptance, full technical pass, or production activation. The remaining real provider/live approval and inherited regression/native evidence gates require separately available owner authority and safe bounded acceptance conditions.

## Publication

- Implementation/tests commit: `6b68ce4f4e1b2bfcb42fc818ee60079d80121fb4` (`R05: connect durable production manifest history`). Before push, fetched/pruned `origin`; confirmed `origin/main` was an ancestor of local `HEAD`. `git push origin HEAD:main` succeeded as a normal fast-forward from `de7deae` to `6b68ce4`.
- Builder log/evidence is being committed separately. Final post-log fetch, parity, ahead/behind and tracked-status verification will be recorded after that push.
