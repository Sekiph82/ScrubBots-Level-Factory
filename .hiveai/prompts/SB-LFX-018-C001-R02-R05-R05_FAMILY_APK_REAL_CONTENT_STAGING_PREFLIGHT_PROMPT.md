# SB-LFX-018-C001-R02-R05-R05 — Family APK: REAL Content Batch + R2 STAGING Preflight

**Implementer:** Codex. **Sole root TASKS.md and independent audit writer:** ChatGPT.
**Repo:** `Sekiph82/ScrubBots-Level-Factory` ONLY, branch `main`.
**Builder log:** APPEND one R05-R05 entry to EXISTING `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`.
**Audit criteria:** `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-R05_FAMILY_APK_REAL_CONTENT_STAGING_PREFLIGHT_AUDIT_CRITERIA.md`.
**Priority:** Family APK / Cloudflare R2 real content, not Pixel Art 4th provider.

## Authority and intent

Owner chose option **1 (Family APK / Cloudflare R2)** as the next task. This authorizes this bounded *real-content selection, preflight and readiness* work, **NOT approval to mutate STAGING or PRODUCTION** and **NOT exact approval of any production manifest SHA/content version**. No public content publication without separate owner review.

Already technically audited and reusable:
- `.hiveai/audits/M18_CPX004_R2_R03_STRICT_REAUDIT_V01.md`: R2 adapter + CPX-004 handoff **TECHNICAL PASS**, live credentials, real owner batch, STAGING/PRODUCTION proof pending.
- M14 `SB-CP03-001..012` and CPX-002 locked publisher; do **not** rebuild a second publisher.
- R05-R01/R02 production history bridge and lost-ack handling technically accepted **narrowly**, but actual live CP03-008/009 and history receipts NOT verified and require exact operator authority.
- R05-R04/R01 Factory Studio 3-tab layout, real PNG imports, bounded preview and thumbnails **OWNER WINDOWS VISUAL PASS / CLOSED** (2026-10-12). Installed Studio displays **9 imported sources** in Level Factory; screenshots show **`Solver: Awaiting pipeline`** and **`Release Pool: READY levels: 0`**. **Imported != solved != READY != production published.** The 9 imported PNGs do NOT certify nine shippable levels.
- Cloudflare locked bucket: `scrubbots-content-prod`; read base: `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev`. Physical prefixes `staging/`, `production/`, `_control/`. Published Family Test manifest location (only after authorized real activation): `production/manifests/current.json`; packs under `production/`.
- Scrubbots family game-side CP04/M15+CP05/M16 is previously accepted. **Never edit `Sekiph82/Scrubbots` in this task.**

## Hard disk, safety and Git policy

- Work **only** in original Desktop checkout `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; safe `git fetch --prune origin`, verify ancestry/dirty overlap and `git merge --ff-only` only if safe, then publish tracked LF implementation + SAME builder log to GitHub `main`. No clones, no TEMP/AppData worktrees, no duplicate project/archive, no wide scratch; do not touch the user's local Scrubbots game checkout. If exact-current game authority cannot be obtained safely without a new clone/TEMP source, **record gate not available** instead of inventing authority or using wrong checkout.
- Preserve all **57** original owner-local untracked status roots, including Release, ICON, addons, UID and two M17 directories. This task does **NOT** authorize additional Release installation or PS1/shortcut modification; R04 is closed. No delete/cleanup/move/rename/stage of these items. Existing local Release and import records are READ ONLY unless the user explicitly takes a separate action.
- No secret values, no new credentials, no Cloudflare admin change, no API billing, no real STAGING or PRODUCTION write, no current manifest CAS, no promotion, no publish-to-phone, no live `R2` integration object, no unapproved review/ACCEPT action. Never log sensitive `R2_` env values; at most check their **presence** without printing hashes/lengths. Credentials must NEVER enter GitHub or APK.
- **No 148 remaining solver paths, no 150-file batch, no full LF pytest, no big Godot import, no Route A game clone, no repeated M18/M14/M17/R05 tests.** Run ONLY genuinely new small targeted tests ONCE after actual code change; reuse old successes. No test-only status masquerading as real live publication.

## One practical execution cycle

### A. Reconcile the REAL locally available publication inputs, before coding

Read existing local canonical `src/scrubbots_pixel_factory/studio_extensions.py` source/candidate/pipeline authority, `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py`, `scripts/build_accepted_factory_output_pack.py`, `scripts/scrubbots_publish_handoff.py`, `content_pipeline/src/scrubbots_content_pipeline/`, existing M18 audit and owner visual R04 final audit.

**Read-only** inspect BOTH relevant **existing** Factory Studio content roots and their configuration (source Desktop and installed Release) to determine which actual persistent owner-import library and Release Pool the running application uses. Do not infer 9 READY levels from 9 PNG thumbnails; report actual:
- imported source records/source SHA identities and local evidence location, if accessible;
- canonical generated candidate IDs, solver SOLVED/replay WIN, Difficulty V1, QA/load-check and immutable file hashes;
- current `release_entries()` truth and owner REJECT/ACCEPT/READY_AUTO dispositions;
- which (if any) entries form an **actually publishable batch** under the current strict CPX-004/M14 revalidation;
- physical existing R2 current production manifest status only **if accessible by an existing safe read-only method**. If not, mark `R2_REMOTE_STATE_NOT_VERIFIED`; never guess version N.

If ready batch absent, deliver **precise `AWAITING_OWNER_RELEASE_BATCH`** with the *actual candidate/source IDs*, which canonical prerequisites are missing, and one minimal owner-visible way to obtain a genuinely READY source by using existing `Run Pipeline` for a chosen PNG (NOT by Codex solving unrequested batches). Do not run any solver or auto-ACCEPT/READY on the owner's behalf. Do not fabricate owner choices or accept synthetic M18 fixtures as real family content.

### B. Resolve the identified READY_AUTO to publisher authority mismatch only if genuine

A source contract discrepancy exists on current `main`:
- `release_pool.enter_release_pool(candidate,pipeline,review=None)` legitimately creates `eligibility_source: "READY_AUTO"` with `review_id: null` under owner decision `docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md` (D9-D12);
- but `scripts/scrubbots_publish_handoff.py::_valid_pool_entry` still insists on a nonempty string `review_id`, which could silently reject all READY_AUTO entries even if all canonical solver/replay/QA gates PASS.
- `build_accepted_factory_output_pack.py` calls `current_solver_proof_for_candidate`, whose review/owner requirements might similarly reject this legitimate source type. **Inspect the full transitively used revalidator first** and determine the actual conflict, not just the field check.

**If mismatch is genuine:** implement a **minimal fail-closed alignment** from actual `READY_AUTO` entries to canonical owner-selected publication:
- a true identity-bound READY_AUTO entry can be displayed in Release Pool and included in a mutation-free exact preflight **only after the owner explicitly selects that candidate for publishing**;
- reject stale/corrupt/rejected/missing-proof and mismatched SHA/source/pipeline, forged READY_AUTO without real canonical immutable Release Pool evidence, and stale/replaced current authority;
- do not auto-publish, synthesize `review_id`, insert false ACCEPT evidence, delete old owner review, or treat OWNER_REJECT as eligible;
- preserve explicit **separate** owner decision to execute STAGING, and later **separate exact** production promotion consent for manifest SHA, content_version, target;
- if historical M14/CPX-001 evidence insists explicit review instead of owner's newer READY_AUTO decision and cannot be reconciled safely in a narrow change, **STOP at `RELEASE_AUTHORITY_CONTRACT_CONFLICT`**, report exact call site, no widening/rerunning broad tests.
- Unit tests for this previously untested mismatch: genuine READY_AUTO valid; owner-rejected excluded; fake no-solver/QA or bad pipeline hash rejected; spoofed or stale identity rejected; explicit owner-selected publication gating; OWNER_ACCEPT path unchanged; wrong production SHA/version disallowed. Tests may use injected small deterministic fixtures, explicitly labeled **OFFLINE**, not counted as live levels.

### C. Prepare ONE real bounded release candidate for owner decision

If `release_entries()` supplies one or more **real, current, complete** eligible candidates, select **up to two already-existing verified READY** (do not rerun their solvers), and produce mutation-free deterministic preflight using existing trusted CPX-004 handoff. Do not manufacture default IDs, future version, Scrubbots main SHA or pack hashes. Check canonical `pack_id`, timestamp `YYYY-MM-DDTHH:MM:SSZ`, source SHA, LevelData, supply, solver proof, replay WIN, Difficulty V1, load-check, exact bound current-game authority, content_version and pack bytes. Keep every deterministic `candidate_ids` choice **provisional until owner reviews the exact list**. No pack upload.

The deliverable must be a concise **secret-free, human-readable OWNER RELEASE DECISION CARD** in the SAME builder log: actual count of imported/READY/publishable, real candidate IDs and source art hashes (or exact missing gate), ordered level IDs, proposed pack ID and SHA/bytes **only if the true preflight computed them**, exact game-main SHA **only if verified**, current remote version **only if verifiable**, proposed next version only if proven, the current `READY_AUTO` vs ACCEPT disposition, and a one-line owner decision needed next. If preflight is blocked, report actual `AWAITING_OWNER_RELEASE_BATCH` / `OWNER_R2_WRITE_CREDENTIAL_REQUIRED` / `SCRUBBOTS_MAIN_UNAVAILABLE` / `RELEASE_HISTORY_UNAVAILABLE` (as appropriate), with `mutation_performed:false`.

Owner-selected content, secure publisher credentials, and exact follow-up STAGING/production authorizations are **distinct**. **This prompt grants none of them**. If existing `Release Pool=0`, report that and the next concrete owner Run Pipeline action rather than creating a fake pack or starting more Codex evidence-only iterations.

### D. Publish actual completed engineering deliverable, no duplicate loops

If code fix B is genuinely required: edit minimal tracked source + new narrowly focused tests; run them once after stable changes; `git diff --check` + secret pattern check, normal implementation commit then append SAME existing R05 builder log and publish to GitHub `main`. If there is no genuine product defect, **do not change product or tests**; append exact meaningful real-batch/operational decision card only. Do not write second tracker, coordination index, standalone log or docs dump; ChatGPT writes independent audit/root TASKS after reviewing log.

Return the existing GitHub R05 builder log URL + exact gate. **Stop after the real owner decision card.** Do not launch production, stage, full regression, or another task. R05 parent remains OPEN; the intended next **separate** phase is owner-reviewed STAGING write/readback then explicit manifest-bound PRODUCTION promotion and actual Family APK runtime verification.
