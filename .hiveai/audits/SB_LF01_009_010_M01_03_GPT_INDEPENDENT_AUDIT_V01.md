# M01.03 independent GPT source audit | SB-LF01-009 / SB-LF01-010

Date: 2026-10-15 (Europe/Istanbul)
Scope: implementation `45b19569ef26fd336ef876c2c696efc0b694f440`, final published evidence `352f9cf5baa2854097bb15719295f20f59a0f0b0`, prompt and M01.03 criteria.
Method: independent GitHub fetch of the actual 8-file implementation commit, the current source files, source-level promotion/publish call chain, semantic contract, tests, TASKS and the existing builder log. This is **static code review**, not an independently executed test, Windows/Studio session or external production proof.

## Verified improvements

1. `contracts/candidate_provenance.py` introduces a deterministic versioned class, request hash, generator ID/version, seed and candidate/attempt bindings. `output/bundle.py` writes and revalidates it; `studio_extensions.list_candidates` exposes it. Normal new generated bundles receive `TEST`.
2. `release_pool.enter_release_pool` calls `validate_pool_candidate_provenance` before promotion and then checks canonical owner source record/bytes and current review. A `TEST` cannot pass this new-entry gate by changing only its `candidate_class` field.
3. `semantic/contracts.py` changes LEVEL_ART resolution to independent owner-approved 20..59 axes; difficulty remains metadata. `SemanticGenerationRequest.from_dict` now permits only exact v1/v2 schema keys, explicit v1 LEVEL_ART dimensions, canonical typed seeds and matching resolved dimensions. Unknown/unversioned/obsolete fields reject. ASSET_ART remains distinct.
4. Added tests cover synthetic TEST and eligible owner-classification shapes, negatives at the real new-entry Pool call, and semantic v1/v2 decoding. Builder reports initial **39 passed / 1 failed**, with a test expectation correction, followed by **56 passed** (memory-only targeted tests). The 56-result is **builder-reported, not independently rerun**. No Actions verification at source `45b19569`, native Studio, owner-source solver, full regression, game, R2 or publication was executed.

## Blocking finding F01 | legacy Pool publication still eligible

`release_pool.release_entries()` (approximately lines 375-435) explicitly skips classification validation for stored entries lacking `candidate_classification`, and `_eligibility_matches_current_review` still accepts `READY_AUTO` without an owner ACCEPT. These records are returned by `release_entries()`. Both `build_release_plan()` and `validate_release_plan()` consume that same list, and `approve_release_plan()` sends the selected items to `publish_batch()` (approximately lines 574-627). Therefore the old unclassified/READY_AUTO path is **still selectable for new release publication** without an explicit authorized migration gate. Keeping legacy records *readable* is not equivalent to blocking their production *reuse*. This violates the M01.03 audit criteria's fail-closed migration/publish condition. Source-trace finding; no historical entry was modified or published for the audit.

## Blocking finding F02 | exact source-to-artwork derivation not independently established

The classification builder trusts generator identity and `source_lineage` supplied in bundle metadata. Pool preflight verifies that the referenced owner PNG exists with matching hash, but does not itself recompute the canonical logical grid from that PNG and compare it to the candidate grid/artwork, nor prove that the generation-result claims came from that exact derivation. A self-consistent but misattributed candidate may therefore claim an owner-upload derivation while a *different* genuine owner-source file passes existence/hash verification. Genuine owner ACCEPT is still separately required, so this is **not** proof of an end-to-end exploit or a release mutation. It is an unproven provenance invariant at the production boundary. Add a bounded synthetic negative with consistent forged metadata and different source pixels, then fail closed through the real entry/publish path.

## Coverage and decision

- **SB-LF01-009: PARTIAL / OPEN.** New candidate classification/new-entry gate is real, but F01 and F02 prevent full literal TEST-vs-PRODUCTION acceptance. No checkbox closure or production authorization.
- **SB-LF01-010: PASS / CLOSED (source-contract scope).** The owner V02 semantic 20..59 and v1/v2 strict ingestion requirements are source-backed with focused builder-reported tests and this independent code inspection. This does **not** certify live semantic-provider interoperability, old external game semantics, full regression or native production Release.
- **R05 / SB-LFX-018: DEFERRED OPEN.** Preserve R09 1848 PASS at its original SHA and R10 63 focused PASS at its original SHA, with 19 deselected, 19 skipped and six ignored modules not waived. No 140 owner PNG solver, Windows TEMP test, owner-path mutation or remote publication.
- Existing nine genuinely READY / 4-4-1 evidence, accepted 002, 3,204 owner-untracked paths and installed Studio/shortcut remain **builder-reported preserved**, not independently read from Desktop.

**Next action:** one limited M01.03 F01+F02 source/test correction, then independent review. Keep legacy evidence available read-only; do not fabricate owner READY/ACCEPT or retrofit old records. Once SB-LF01-009 actually passes, proceed to the first source-feasible M02 task rather than reopening R05 by default.
