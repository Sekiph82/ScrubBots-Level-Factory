# SB-LFX-018-C001-R02-R05-R05 — Independent Strict Audit V01

**Date:** 2026-10-12  
**Repository:** `Sekiph82/ScrubBots-Level-Factory`, `main`  
**Verdict: R05-R05 NARROW ENGINEERING PASS / CLOSED; REAL FAMILY APK RELEASE BATCH BLOCKED — `AWAITING_OWNER_RELEASE_BATCH` + `SCRUBBOTS_MAIN_UNAVAILABLE`.**  
**Parent R05 and M18 live R2/FAMILY APK operations OPEN. NO STAGING/PRODUCTION PUBLICATION.**

## Material actually independently reviewed

- Existing R05 builder log `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md` as published to `main` (blob `c54dd274bc7737e00e858f2973e3e5d36ddc7301`).
- Implementation/test commit `bf50ac5b4b1d66767b20b9c8b128b79711ed72cb` (four files only): `scripts/scrubbots_publish_handoff.py`, `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py`, `src/scrubbots_pixel_factory/supply_pipeline/scrubpack_identity.py`, and `tests/unit/test_sb_lfx_018_r05_ready_auto_publisher_authority.py`; log-only evidence commits `96a81d1dbd24df30f0031cf1fc8bcf762efc1d41`, `aaf6106cee91ea0944fbc46fec3c576cefbbac22`.
- Traced current `main` `release_pool.enter_release_pool / release_entries`, `scrubbots_publish_handoff._valid_pool_entry / publish_preflight`, `current_solver_proof_for_candidate / revalidate_current_solver_proofs`, and `studio_extensions.validate_owner_source / _derive_owner_candidate / run_pipeline`. No tests, remote calls or local owner filesystem inspections were run by ChatGPT; Windows Release inventory/parity remain Codex builder-reported.

## READY_AUTO authority correction: narrow technical PASS

Existing owner D9-D12 legitimately creates canonical `READY_AUTO` Release Pool records with `review_id:null` without mandatory owner ACCEPT; a separate explicit selected candidate list/publication action is still required. Previous publisher `_valid_pool_entry` rejected these outright, while final pack revalidation required ACCEPT even when the selected proof came from the current canonical Release Pool.

Accepted corrections:
1. `release_entries()` now tests eligibility: READY_AUTO with null review and no current REJECT; OWNER_ACCEPT with exact latest current ACCEPT review identity. Unknown eligibility rejected. Existing release-entry digest, pipeline, candidate and artifact byte-hash checks remain in the original `release_entries` path.
2. Publisher `_valid_pool_entry` accepts explicitly selected READY_AUTO with null review, retains OWNER_ACCEPT with review, refuses unknown eligibility, missing pipeline READY or bad pipeline SHA shape. Actual pool membership still comes through the canonical reader; `_valid_pool_entry` by itself is only structural, **NOT a cryptographic validator**.
3. Final `revalidate_current_solver_proofs` re-fetches current pool authority and exact pipeline bytes; checks immutable pool entry digest, level/supply byte identity, current candidate/run, and latest review/REJECT. Legacy non-pool fallback still needs explicit current ACCEPT.
4. `publish_preflight` still requires explicit nonempty, nonduplicate `candidate_ids`; no auto-selection or STAGING/PRODUCTION consent was added. M14 publisher and cloud paths were not changed.

**Evidence limit:** New focused module reports **3 PASS** on a Windows offline mocked authority. The first attempt was **2 PASS, 1 FAIL** due to the new fixture's Windows path separator, corrected before the final 3 PASS. The tests use fake reader, synthetic pack evidence, synthetic current-game identity and an in-memory `Path.read_bytes` double; **they do not prove a real Release Pool READY_AUTO roundtrip, true pack build, live provider credentials or remote preflight.** No previously passing suite was rerun; these narrower tests and source inspections are adequate for the specifically authorized READY_AUTO compatibility change, not for the broader R05 closure.

## Genuine user content / Family APK state: truthful external blocker

Codex read-only report of the installed local Release: **12 immutable owner-upload records**, of which **9 are gameplay 32x32 PNGs** with matching source SHA and **3 are 1536x1024 Studio master images**. Nine valid source byte hashes are `SOURCE_ONLY`, not canonical-ready content. The installed Release has **0 candidate bundle manifests, 0 owner-review records, 0 Release Pool entries, 0 READY pipelines**, with 11 historical runs (7 PARTIAL/STOPPED, 4 UNAVAILABLE). The latest named owner source `002_32x32px.png` is stopped at `DERIVED_ARTIFACT_REQUIRED`; `SCRUBBOTS_PROJECT` is unset, so a current game rules/VOID/load-check authority is not available. R2 live manifest/version/current-state **NOT CHECKED** and no real pack/preflight manifest SHA/next version/current Scrubbots `main` SHA was computed.

**Important next-action nuance:** Setting `SCRUBBOTS_PROJECT` is **necessary but not by itself sufficient**. Current `validate_owner_source()` requires exact canonical palette/alpha, dimensions, color-count and current-game VOID capability to derive via `_derive_owner_candidate()`. `run_pipeline(source_id)` on `exact_logical_source == false` simply records a `DERIVED_ARTIFACT_REQUIRED` stop and does **not** invoke an automatic palette remap or solver. Therefore the suggested 'click Run Pipeline' cannot be promised to produce READY for unchanged noncanonical PNG. Determine the exact rejection codes and request owner-controlled **derived-copy** treatment rather than silently editing immutable original source. No such derivation/solver/new batch was authorized by this task.

No evidence of secure R2 writer credentials, successful live STAGING upload/readback, owner-selected true READY batch, separately approved exact manifest SHA/version PRODUCTION promotion, or current R2 version N. `AWAITING_OWNER_RELEASE_BATCH`, `SCRUBBOTS_MAIN_UNAVAILABLE`, `R2_REMOTE_STATE_NOT_VERIFIED` are the correct states; **no real R2 publication PASS**.

## Safety and publication

Codex reports canonical Desktop LF checkout only, safe fast-forward from old head, product/test commit `bf50ac5`, log-only commits `96a81d1` and `aaf6106`, last verified `HEAD == origin/main == aaf6106cee91ea0944fbc46fec3c576cefbbac22` (0/0, tracked clean). Only those four tracked product/test files and the pre-existing single R05 builder log were changed. All 57 owner-untracked status roots, local Release installation, PS1/shortcut and separate Scrubbots repository reported untouched. No TEMP, 148 solver batch, full regression, credential print or actual remote write. These are credible published builder records, not independent reads of the user's private desktop.

## Disposition / next owner decision

**Close R05-R05 as truthful engineering handoff and READY_AUTO narrow technical fix PASS, with real batch/readiness external blocker; DO NOT close parent R05.** Do not request another test of the unchanged source/tests. Next practical user-controlled action: (1) resolve a **verified** game authority for installed Studio without changing the owner's Scrubbots game checkout; (2) inspect source `002_32x32px.png` exact palette/alpha/VOID rejection codes; (3) if noncanonical, ask owner whether to make a **new canonical derived candidate copy while preserving the original immutable PNG**; (4) explicitly run one bounded solver only after that setup and owner choice; (5) review real SOLVED/WIN/Difficulty V1/load-check/READY and then the actual release identity. No new production/write permission is conferred by this report.

**DO NOT** mark imported PNGs as ready, fabricate a preflight, stage cloud objects, repeat prior tests, run large solver batches or silently perform derivations.
