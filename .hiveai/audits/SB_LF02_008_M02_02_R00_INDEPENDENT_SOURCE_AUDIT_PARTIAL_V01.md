# SB-LF02-008 M02.02 | GPT independent source audit R00 V01

Date: 2026-10-15 Europe/Istanbul
Repository: `Sekiph82/ScrubBots-Level-Factory`
Decision: **SOURCE PARTIAL / OPEN F01 (post-fix regression not proven and deterministic TEST rejection contract disrupted)**.
Scope: builder code SHA `95da9a26001ece2e1191ee5b7fe362810fecc4c8`, log-only final main `05e7b63aea02cb3509f5ba2d944e7608fa74ae87`; prior GPT main `22b7defb77a4fc94e306b7c9541ed1b4d5540315`.

## Independently retrieved and verified

1. Fetched GitHub main exactly at `05e7b63aea02cb3509f5ba2d944e7608fa74ae87`, compared the seven code/test files and builder log against `22b7def...`, inspected source and current focused tests, and inspected the actual completion receipt. Implementation `95da9a2`; builder log commit `0144499601dba532087838aa602595b48a84c2d6`; final log-only `05e7b63`. No workflow changed in the compared source. **No new GitHub Actions/CI initiated.**
2. Builder reports initial targeted pytest run **22 PASSED / 2 FAILED** at intermediate code, then a Pool correction without rerunning that same targeted pytest selection; subsequent direct functional checks WFC+source/Pipeline and AST/diff passed. These are **builder-local results**, not GPT independently executed tests; no final `24/24` claim is warranted.
3. Builder reports 16 new task `.pytest-scratch-sb-lf02-008-20261015/` untracked paths, normal deletion denied by policy. Original 3,204 preserved; current 3,220 untracked from builder. GPT has not seen Windows file bytes or verified clean local status. Treat those 16 entries as known task scratch, **not automatically owner-authored**, but do not delete, circumvent the denial, relabel, or spend on cleanup.

## Source-backed improvements (PASS in implemented boundaries)

- `contracts/candidate_provenance.py::build_candidate_classification` no longer upgrades caller-shaped `owner-upload` metadata to `PRODUCTION_CANDIDATE`: ordinary provenance projections remain TEST. Separate `build_verified_owner_upload_classification` contract requires structurally coherent verified hash and metadata. Its `verified_source_sha256` argument is **caller-supplied** at this low-level function; treat that helper only as a projection, never stand-alone source authority.
- `output/bundle.py::_verified_owner_upload_sha256` performs the actual canonical source-record/byte verification via existing Studio `verify_owner_source`, strict `_owner_source_grid` decoder, exact grid, dimensions, seed and lineage. `_metadata_for` and `_validate_metadata` call it before adopting/revalidating production class. Forged owner-upload metadata with no actual source fails to export.
- `generators/wfc/model.py` removes user-provided `OWNER_APPROVED` as an admissible ownership class and rejects unverified `approved_by`, while only synthetic fixtures remain WFC generation-eligible. `generators/wfc/generator.py` protects direct exemplar selection. This is conservative and does **not** establish an authenticated owner-exemplar route.
- `supply_pipeline/release_pool.py::validate_pool_candidate_provenance` now performs actual existing source/artwork byte match before using the verified production classification, retains exact owner ACCEPT requirements. The source-backed positive synthetic check reported by builder is encouraging but **not final 24-case pytest verification**.
- Existing semantic/raw AI provenance remains not an attested original creator identity. No use of owner-original, actual owner acceptance, real 140 PNGs, game, installed Release, R2 or high-cost CI was independently certified.

## F01: deterministic no-owner TEST rejection regression (OPEN; code/test mismatch)

Current `tests/unit/test_sb_lf01_009_010_candidate_and_semantic_contracts.py::test_generated_candidate_defaults_to_test_and_is_request_bound` continues to assert:
```
with pytest.raises(ReleaseError, match="TEST candidate"):
    validate_pool_candidate_provenance(candidate, None)
with pytest.raises(ReleaseError, match="TEST candidate"):
    enter_release_pool(candidate, ...)
```
The `candidate` here is constructed using `_candidate(owner_source=False)`, which has `generator_id="provenance-fixture"`, no owner-upload source lineage, and a TEST bundle classification. But current `release_pool.py::validate_pool_candidate_provenance` invokes `_verify_candidate_source_grid_binding(candidate, classification)` **before** rejecting the already-known TEST class. The verification calls `_candidate_source_lineage(candidate)`, which requires an on-disk owner candidate bundle and owner-upload lineage; the TEST fixture has neither. Instead of the established immediate `TEST candidate cannot enter...` result, the new implementation can raise an unrelated missing-path/owner-lineage `ReleaseError`. This breaks the test's documented negative-path contract, and can trigger unnecessary source I/O for synthetic TEST items. Source inspection supports this mismatch; GPT did not execute that test, so exact runtime traceback must be obtained locally, not invented.

**Required narrow repair:** Restore an early **negative-only** rejection for the already present, canonical `candidate_class != "PRODUCTION_CANDIDATE"` without ever granting authority on the basis of a claimed positive production string. Retain unconditionally full source bytes/grid + current ACCEPT verification for all candidate records that *claim* `PRODUCTION_CANDIDATE`. A forged positive still cannot reach Release Pool without source truth. Add focused in-memory regressions both TEST and forged PRODUCTION_CANDIDATE no-source; do not waive/rename existing TEST expectation.

## Decision and remaining boundaries

**SB-LF02-008: PARTIAL / OPEN (F01)**. Most requested source-origin security controls are implemented, but preexisting TEST rejection contract is disrupted, and the reported 22 pass/2 fail pytest run was NOT rerun after Pool correction. There is no independent basis for full test acceptance. Owner cost lock is in force, so no GitHub CI or hosted tool should be invoked. An exact, bounded R01 local-only repair can close source scope after GPT inspects revised diff, targeted evidence and unchanged workflow.

Separate outstanding work: native Windows symlink real-world test remains NOT RUN; AI upstream provider creator attestation remains UNVERIFIED; R05 game/native production remain DEFERRED_OPEN. These are not implicitly waived by LF02-008. `SB-LF02-004` remains previously closed in its narrower reviewed-imported-art scope.
