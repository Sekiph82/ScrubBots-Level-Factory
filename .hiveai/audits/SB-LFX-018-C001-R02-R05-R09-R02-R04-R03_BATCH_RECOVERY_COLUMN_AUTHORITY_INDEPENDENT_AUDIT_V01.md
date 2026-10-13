# SB-LFX-018-C001-R02-R05-R09-R02-R04-R03 — R04-R02 Independent Strict Source Audit V01

2026-10-13. **Verdict: R04-R02 PARTIAL CODE IMPLEMENTATION / FAIL REQUIRED BATCH CORRECTNESS GATES / INSTALLED OWNER VISUAL PENDING.** Reviewed published GitHub `main` product `b5cc1b815eb7638dea54ed1ce37355dfc3b5e54f` and final reported head `f27bcb51711dd23a4a869ebb9418a7b153874e6d`, existing R05 builder log, full new `src/scrubbots_pixel_factory/png_batch.py`, source `studio_extensions.py`, Level Factory Godot UI relevant functions and new focused Python/Godot test code. Live Windows Release NOT updated (installed sourceRevision `6e1065ce...`; Studio PID 16292 still running); ChatGPT did not execute Windows tests or inspect Release bytes. Builder reports initial 10/10 Python, 3 affected rechecks, Godot suite PASS and zero real native solver. Those counts are builder reports, not independent execution.

## Scope that is code-real and should be preserved

- Responsive `responsive_geometry()` and `_apply_responsive_layout()` no longer center a 1536×1024 letterbox; new in-card `LevelFactoryInlineResults` has scrollable source-bound Supply/Replay, compact right details, two- and three-button horizontal rows. Static structural and headless geometry tests cover multiple window sizes. No screenshots of this NEW layout exist yet: no owner UI PASS.
- `png_batch.py` establishes deterministic 45/40/15 largest-remainder assignment (9=4/4/1, 40=18/16/6, 150=68/60/22), sequential one-job `_job_lock`, SHA-bearing jobs and atomic checkpoint files, explicit `png-batch-run` invocation, process control, and canonical solver gateway; no implicit start on PNG import. Focused new Python tests cover fake batch and 150 items.
- Original 002 ready/Release Pool evidence and historical source remain untouched by this new code according to builder, no native solve/replay/load-check and no cloud; no installation attempted because Studio was open.

## Failing or unproven mandatory business gates

### F01 — Critical deterministic source/attempt recovery mismatch (source verified; FAIL)

In `studio_extensions._run_pipeline_impl` (~1077-1089) real imported-source work calls `_run_canonical_artwork_route(source_kind="CANDIDATE")`, which **persists** its immutable run at ~909-911 with top-level `source_id=None` and the correct imported source under `request.source_id`; only AFTER persistence does wrapper add `payload["source_id"]=source_id` for the in-memory returned result. In new `png_batch._recover_attempt` (~339-370), scan requires `payload.get("source_id") == item.source_id`. A user batch interrupted **after the genuine SOLVED/READY saved run but before the batch job checkpoint** cannot find its valid run, and will invoke native solver **again**. New recovery test uses a hand-built payload with top-level source_id and thus misses this real producer shape. Violation: exact completed run once, restart recovery. Repair new **future** persisted run source identity (without rewriting existing immutable runs) and legacy recovery by strict request.source_id with exact immutable PNG SHA, candidate lineage, unique matching job/attempt ID, QA, solver/supply and Pool SHA/readback checks. Negative tests: forged source/run, multiple runs, missing full proof all blocked.

### F02 — Critical reused solution may silently violate assigned 45/40/15 columns (source verified; FAIL)

`png_batch._reuse_existing_ready` (~373-396) calls `restore_source_run`, tests READY/source SHA/QA/pool but **does not compare stored `primary.column_count` to scheduled `item.column_count`**. Then `run_png_batch` (~470-477) counts the item as READY under *planned* 3/4/5 without ever checking the actual reused supply column count. Example real 002 already 4-col READY: if deterministic batch slot assigns 3, program may reuse 4-col and falsely report 3-col. Require bound column equality through result, primary, saved export plan, pool entry (and any exact immutable replay proof) prior to reuse; mismatched old 4-col must not count as 3-col. Explicitly documented safe policy: either create a new genuinely solved requested-mode run ONLY after owner starts the real batch, or mark item as reusable *outside quota* with truthful actual mix and owner decision; default to canonical assigned mode. Add negative tests and real code-shape fixtures for 002.

### F03 — Selected single-source preflight improperly gates whole batch (source verified; FAIL)

`factory_studio_exact_ui.gd::_run_png_batch` (~1582-1592) requires `_pinned_source_preflight_ok` for **the currently selected one thumbnail** before even creating the multi-source job. Batch-owned source validation already happens independently in `png_batch._verify_sources` and per-item revalidation; an unsupported/invalid selected PNG must be REJECTED individually and not block all other valid PNGs. Remove batch-global dependency on selected single source; retain attested per-item trust validation and precise invalid reasons. No native solve during preflight.

### F04 — Resumed job may be detached from its import batch (source verified; FAIL risk)

Godot `_restore_imported_sources` chooses `_batch_import_id` from `owner-pages.batches[0]` and separately chooses `_batch_job_id` from arbitrary `png-batch-latest.job`; it never requires restored job.import_batch_id == selected import batch ID / batch_digest. Thus after restart with several imported batches, displayed Run/Resume may operate the wrong job while the selected thumbnails represent another. `_run_png_batch` does not perform a cross-match when `_batch_job_id` already set. Enforce job-to-import exact ID/digest binding, show truthful action, and refuse mismatches rather than silently run another batch; add restart + two-batch test.

### F05 — UI/installation is still unverified, and tests under-cover live integration

- New UI has only headless geometry and inline mock/002 read-only fixture test, not an installed real renderer screenshot at 1536×864/1920×1080. Owner sign-off pending.
- Source `_has_ready_pipeline_proof` checks field presence, backend pool verification mitigates this, but tests fake returning true `readback_verified` without positive actual canonical persisted imported-source shape. F01+F02 make the batch engine not independent PASS despite reported green mocks.
- Installed Release remains previous revision, so **no claimed new layout/batch is yet present in owner Desktop Studio**.
- `--basetemp` path used was new R02 according to builder; protected old `.m17` parity remains independently unverified. Do not reuse any existing temp output. No full regression done.

## Verdict and handoff

**R04-R02 NOT CLOSED.** Authorize **one** surgical R04-R03 remediation `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R04-R03_RECOVERY_QUOTA_BATCH_BINDING_AND_SAFE_RELEASE_INSTALL_MASTER_PROMPT.md` with tests for actual canonical persisted payload, exact reused column and restarted two-batch UI. Keep 45/40/15, existing panel layout, original 002 POOL, official difficulty and source attestation. Builder NO native solver; after source-fix audit, can install only after owner closes Studio normally; NEVER force close or hot patch. New owner screenshot and a future explicitly owner-initiated controlled batch remain separate gates. Parent R05/CPX-002 shipping/R2 OPEN.
