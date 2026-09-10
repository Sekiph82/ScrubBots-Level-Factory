# PAG-M06-C002 — WFC Remap, Stage Replay & Router Evidence Remediation

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-10  
Auditor: ChatGPT  
Cycle: `PAG-M06-C002`  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Branch: `main`

Audited builder boundary:
- cycle base: `5ad81886669e4f8cfa2247a689439a2186ad1b50`
- implementation commit: `2c786e47aea8ce7b3fc10fa4877f264605fb77f2`
- builder-log publication / terminal builder-era HEAD: `9cc8f4b4ca8757427fbbe88d239e1acb6092a764`

Previous audit:
- `PAG-M06-C001_HYBRID_GENERATOR_ROUTER_STRICT_AUDIT.md`

Authoritative remediation prompt:
- `PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_PROMPT.md`

## 1. VERDICT

**FAIL**

C002 fixes the substantive WFC remap defect and replaces the old whole-request reproduction helper with a genuine stage-by-stage replay verifier. The AUTO implementation remains architecturally sound and the review pack now carries actual topology arrays/panels. However, two mandatory C002 evidence gates are still incomplete, so M06 cannot receive unconditional PASS.

Open findings:

- **F-PAG-M06-C002-001 — MAJOR — The required WFC-detail golden/review evidence contract is incomplete.** The committed WFC-detail golden does not record or validate stage geometry/topology digests or the WFC pattern-table digest, and review validation does not prove all prompt-required topology relationships/digest bindings.
- **F-PAG-M06-C002-002 — MAJOR — Required AUTO acceptance evidence remains incomplete.** The committed tests do not directly prove the required same-seed selection repeat, multi-candidate `fallback=false` no-next-engine behavior, successful-fallback outer dimension/palette plus selected engine/version assertions, or all-fail global cyclic attempt order.

M07+ remains blocked.

A bounded `PAG-M06-C003` evidence-closure remediation is required. No architecture rewrite is authorized.

## 2. CONTRACT RECOVERY

C002 was required to close exactly four C001 findings while preserving the validated M06 architecture:

1. preserve M05 source→target WFC palette remapping in both WFC-detail strategies;
2. implement metadata-driven stage replay and corruption rejection;
3. complete AUTO fallback/selection acceptance evidence;
4. complete topology review evidence and add a fully specified WFC-detail golden.

The C002 prompt also explicitly required the WFC-detail golden to record and validate strategy, outer request, exemplar ID/ownership, stage seeds, engine/helper IDs/versions, child request digests, child result/output digests, geometry/topology digests, WFC pattern-table digest, final grid digest, and final `GenerationResult` digest.

The review validation contract required array lengths, digest binding, WFC-detail before==final topology, MASK_GEOMETRY before==final topology, and symmetry after==final topology.

The AUTO test contract required deterministic repeatability, seeded diversity, a real multi-candidate no-fallback failure case, successful cyclic fallback with retained failure provenance and preserved outer contract, bounded all-fail cyclic order, and explicit HYBRID route equality.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub compare from `5ad81886669e4f8cfa2247a689439a2186ad1b50` to `9cc8f4b4ca8757427fbbe88d239e1acb6092a764` shows exactly two commits and nine changed paths:

- C002 builder log;
- `src/scrubbots_pixel_factory/generators/router/hybrid.py`;
- M06 router/review/golden tests;
- M06 review builder, manifest and contact sheet;
- M06 hybrid golden data.

No M07+ production implementation is in the C002 diff. No main `ScrubBots` repository mutation is part of this boundary.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| F-C001-001 WFC default source→target remap | PASS | M06 no longer synthesizes outer-palette identity mapping; M05 default mapping is allowed to operate. |
| F-C001-001 caller explicit mapping preserved | PASS | Nested WFC mapping is passed through; non-identity fixture tests exist. |
| PAG-0609 RULE_BASE_WFC_DETAIL | PASS | Non-identity source exemplar succeeds with default and explicit mapping evidence. |
| PAG-0610 MASK_BASE_WFC_DETAIL | PASS | Same remediation is exercised for MASK base. |
| F-C001-002 true stage-by-stage replay | PASS | Recorded child requests are reconstructed; engine/helper stages are rerun and compared. |
| PAG-0616 metadata reproduces stages | PASS | Source now verifies stage identity/order, seed, request, engine/version, result/geometry and engine-specific metadata plus final digests. |
| Required replay corruption classes | PASS / TEST-STRENGTH NOTE | Required corruption fields are represented. Tests corrupt the serialized copy while `candidate.stages` remains unchanged, so some failures can occur at the mirror-consistency guard before the field-specific guard. Source still contains the specific guards. |
| AUTO seed diversity | PASS | Fixed seed range demonstrates both default modes. |
| AUTO same-request/same-seed repeated selection | **PARTIAL** | Deterministic source exists, but the specifically required repeat assertion is absent. |
| AUTO fallback=false no hidden next mode | **PARTIAL** | Existing test uses a one-candidate list, so it cannot prove a second configured candidate is not invoked. |
| AUTO fallback=true success evidence | **PARTIAL** | Failed attempt and successful next mode are shown, but required outer dimensions/palette and selected engine/version assertions are incomplete. |
| AUTO all-fail cyclic exhaustion | **PARTIAL** | Bounded byte-stable failure is shown; global inter-engine cyclic order is not directly asserted. |
| Explicit HYBRID router==direct | PASS | Direct canonical-byte equality test exists. |
| >=12 review candidates / four strategies | PASS | Committed review remains >=12 and covers all four strategies. |
| Actual topology arrays/panels | PASS | before/after/final arrays and visual panels are committed. |
| Review topology validation contract | **PARTIAL** | Final digest is checked, but not all before/after bindings; MASK_BASE_WFC_DETAIL before==final is not explicitly asserted. |
| WFC-detail golden exists | PASS | A synthetic RULE_BASE_WFC_DETAIL golden is committed. |
| WFC-detail golden full evidence schema | **FAIL** | Geometry/topology digest evidence and WFC pattern-table digest are absent from the golden and its test assertions. |
| No interpolation/resizing | PASS by source/diff inspection | No C002 path introduces resizing/interpolation. |
| Full regression | UNVERIFIED independently | Builder reports `247 passed, 1 warning`; no GitHub Actions run exists for the implementation commit. |
| `pip check` | KNOWN ENVIRONMENT FAILURE | Builder reports pre-existing pytest/pytest-asyncio version mismatch; C002 did not hide it by changing dependencies. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### WFC remap

Builder claim: default and caller-supplied source→target remaps are preserved.

Repository truth: **CONFIRMED**. WFC child options are copied without injecting an identity mapping. The generated WFC candidate's actual mapping is then recorded as stage evidence. The focused fixture uses source IDs `C11/C12/C13` against target `C01/C02/C03` and exercises both WFC-detail strategies plus a caller-supplied non-identity mapping.

Disposition: **PASS**

### Metadata replay

Builder claim: replay is metadata-driven and verifies every engine/helper stage.

Repository truth: **CONFIRMED in source**. `replay_candidate()` reconstructs the canonical child request, rederives the stage seed, calls the recorded stage kind, validates engine/helper identity and output/geometry evidence, checks engine-specific metadata, reconstructs WFC-detail composition, and validates final topology/grid/result digests.

The corruption tests are useful but not maximally adversarial because the candidate keeps two copies of stage metadata; modifying only one copy can be rejected by the earlier duplicate-consistency guard. This is a test-strength note, not a finding that the implementation is still whole-request replay.

Disposition: **PASS with test-strength note**

### AUTO acceptance

Builder claim: AUTO selection/fallback/explicit-HYBRID evidence is complete.

Repository truth: **NOT FULLY CONFIRMED**. The implementation is deterministic and opt-in fallback is structurally correct. Tests do prove seeded diversity, one failed then successful fallback, byte-stable bounded all-fail behavior, and explicit HYBRID equality. They do not implement every assertion explicitly mandated by C002, especially the multi-candidate fallback=false sentinel case and global cyclic-order proof.

Disposition: **PARTIAL**

### Review/golden evidence

Builder claim: review/golden evidence now satisfies C002.

Repository truth: **PARTIAL / REJECTED for the exit gate**. The review manifest and contact sheet now contain real topology evidence. A WFC-detail golden exists. But that golden omits two categories the C002 prompt explicitly required: per-stage geometry/topology digest evidence and WFC pattern-table digest. The golden test therefore cannot validate them. Review validation also does not bind every required before/after topology to its corresponding recorded digest/relationship.

Disposition: **FAIL for the evidence exit gate**

## 6. FILE / SYMBOL EVIDENCE

### `src/scrubbots_pixel_factory/generators/router/hybrid.py::_compose_attempt`

- WFC mapping is no longer replaced by an outer identity map.
- caller WFC option values are preserved;
- M05 remains responsible for validating/defaulting the mapping;
- `RULE_COLOR_REGIONS` and `MASK_SYMMETRY_COLOR_REGIONS` are truthfully marked `COMPOSITION`;
- topology evidence is returned as actual occupancy sets.

Result: **PASS**

### `src/scrubbots_pixel_factory/generators/router/hybrid.py::replay_candidate`

- validates outer strategy/attempt/master seed/dimensions/palette;
- validates stage order/name/kind;
- rederives each stage seed;
- reconstructs child requests from recorded canonical metadata;
- reruns MASK/RULES/WFC engines or composition helpers;
- validates required engine-specific metadata;
- validates final topology/grid/result digests.

Result: **PASS**

### `src/scrubbots_pixel_factory/generators/router/router.py::_auto`

The source has deterministic initial selection, cyclic opt-in fallback, bounded candidate attempts, retained failed-attempt failure codes, and original AUTO result wrapping.

Result: **PASS source / PARTIAL acceptance evidence**

### `tests/golden/m06_hybrid_goldens.json`

The WFC-detail entry contains:

- request;
- strategy;
- palette;
- stage seeds;
- stage engine/version pairs;
- child request digests;
- child result digests;
- final grid/result digest;
- exemplar ID/ownership;
- palette mapping.

It does **not** contain:

- stage geometry/topology digests;
- WFC pattern-table digest.

Result: **FAIL against explicit C002 golden schema**

### `tests/golden/test_m06_hybrid_golden.py`

No assertion validates stage geometry/topology digests or WFC pattern-table digest.

Result: **FAIL against explicit C002 golden validation gate**

### `tests/integration/test_m06_review_evidence.py`

Positive: validates count, strategy/difficulty coverage, row-major lengths, final topology digest, and offline contact sheet.

Gap: WFC-detail equality assertion explicitly names RULE_BASE only; MASK_BASE falls through to an `after == final` assertion. It also does not bind each applicable before/after topology digest to the stage evidence that claims it.

Result: **PARTIAL**

## 7. FOCUSED TEST EVIDENCE

Repository test source independently confirms new focused coverage for:

- explicit HYBRID router equality;
- seeded AUTO diversity;
- fallback success;
- bounded all-fail repeatability;
- default and explicit non-identity WFC mapping in both detail strategies;
- invalid WFC mapping rejection;
- replay corruption fields;
- all four hybrid strategy paths;
- topology/review evidence;
- WFC-detail golden generation.

Missing exact acceptance assertions are captured in findings F-PAG-M06-C002-001 and F-PAG-M06-C002-002.

Builder reports focused M06 suites at 16 PASS and combined M06 acceptance/focused suites at 17 PASS. These are builder evidence, not independently executed results.

## 8. REGRESSION EVIDENCE

Builder reports:

- full repository: `247 passed, 1 warning`;
- robust M06 matrix retained: 24 accepted cases;
- standalone import: PASS;
- `git diff --check`: PASS;
- offline/source policy scans: PASS;
- M07+ scope scan: no matches.

No GitHub Actions workflow run is attached to implementation commit `2c786e47...`, so the full test run is **UNVERIFIED independently** in this audit environment. Direct source/diff inspection found no contradiction suggesting an M03-M05 regression.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

No C002 diff introduces:

- runtime network/API/cloud dependency;
- credential handling;
- subprocess/eval/exec generation path;
- non-project randomness;
- resizing/resampling/interpolation;
- production owner artwork masquerading as a test fixture.

The WFC review/golden exemplar is explicitly synthetic/test-only.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

The M06 architecture remains coherent:

```text
outer GenerationRequest + root RNG
 -> explicit route or deterministic AUTO
 -> bounded HYBRID strategy
 -> canonical child GenerationRequests
 -> real engine/composition stages
 -> exact topology/palette validation
 -> provenance + replayable metadata
```

C002 does not require architectural rollback. Remaining work is targeted evidence closure.

Result: **PASS**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The C002 builder correctly left ChatGPT-owned tracker/audit/cycle files unchanged. That means the authoritative v3 tracker still shows C002 as `READY_FOR_IMPLEMENTATION` at audit start; this is stale relative to repository product truth but consistent with the builder ownership rule.

The independent auditor must now advance tracker truth by recording this FAIL and activating C003.

The builder log is detailed and records the pre-existing `pip check` mismatch instead of concealing it.

Result: **PASS builder boundary / TRACKER UPDATE REQUIRED BY AUDITOR**

## 12. FINAL REPOSITORY STATE

Terminal C002 builder-era HEAD independently observed:

`9cc8f4b4ca8757427fbbe88d239e1acb6092a764`

Implementation commit:

`2c786e47aea8ce7b3fc10fa4877f264605fb77f2`

C002 product work is published. M06 is not accepted. M07+ remains blocked.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M06-C002-001 — MAJOR

**WFC-detail golden/review evidence contract remains incomplete.**

Affected paths:

- `tests/golden/m06_hybrid_goldens.json`
- `tests/golden/test_m06_hybrid_golden.py`
- `tests/integration/test_m06_review_evidence.py`
- review builder/manifest only if needed to expose missing digest bindings

Required target:

- every WFC-detail golden records and validates per-stage geometry/topology digest evidence;
- WFC_DETAIL records and validates `pattern_table_digest`;
- topology review tests explicitly validate both WFC-detail strategies before==final;
- topology arrays are bound to the corresponding recorded topology/geometry digest evidence, including symmetry before/after where applicable.

### F-PAG-M06-C002-002 — MAJOR

**AUTO required acceptance evidence remains incomplete.**

Affected path:

- `tests/integration/test_m06_router.py`

Required target:

- same AUTO request+seed is run at least twice and initial selection/order is identical;
- fallback=false uses at least two configured candidates with sentinels and proves only the selected failing engine was invoked;
- successful fallback explicitly asserts retained failed attempt, selected engine ID/version, original AUTO request/mode/master seed, exact outer dimensions and palette;
- all-fail test records/asserts the complete global cyclic attempt sequence and each candidate exactly once per run;
- preserve explicit HYBRID equality test.

## 14. DEFECTS BY SEVERITY

- BLOCKER: 0
- MAJOR: 2
- MINOR: 0
- NOTE: replay corruption tests could be strengthened by reconstructing both mirrored stage representations consistently before corrupting a single semantic field, ensuring the intended field-level verifier is what rejects the candidate.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Consider a small reusable test helper that reconstructs a `HybridCandidate` from one canonical metadata representation. This would reduce duplicate-copy ambiguity in replay corruption tests.
- The pre-existing `pytest-asyncio` / pytest environment mismatch should be repaired in the environment or dependency policy during a separately authorized maintenance/performance cycle; it must not be smuggled into this bounded M06 remediation.

## 16. UNVERIFIED ITEMS

- Builder-reported `247 passed, 1 warning` was not independently re-executed.
- Builder-reported command timing was not independently reproduced.
- Local Windows workspace/stash condition was not independently inspected; GitHub is current-state authority and published scope was independently compared.

## 17. REGRESSION RISK

**LOW to MODERATE** for C003 if it remains test/evidence-only.

Do not rewrite router/hybrid production logic unless a new focused test exposes a real contradiction. The functional WFC mapping and replay changes should be preserved.

## 18. AUDIT CONFIDENCE

**HIGH** for the FAIL verdict.

Reason: the primary blocking defect is a direct, text-level mismatch between the authoritative C002 golden evidence contract and the committed golden/test schema. AUTO evidence gaps are also directly visible in committed test source. Full-suite execution remains independently unverified, but that uncertainty cannot convert explicit missing acceptance evidence into PASS.

## 19. FINAL VERDICT

**FAIL**

C002 materially improves M06 and closes the core WFC remap and replay implementation defects, but the exact evidence contract is not complete. M06 remains open and M07+ remains blocked.

## 20. REQUIRED REMEDIATION

Create and execute only:

`PAG-M06-C003 — Replay, AUTO & Evidence Gate Closure`

C003 must be a narrow acceptance-evidence remediation:

1. complete the WFC-detail golden schema/assertions for stage geometry/topology and WFC pattern-table digest;
2. complete topology review digest/equality assertions for both WFC-detail strategies and applicable before/after stages;
3. add the missing exact AUTO acceptance assertions, especially a two-candidate fallback=false sentinel test and global cyclic-order all-fail proof;
4. strengthen replay corruption tests only if needed, without redesigning the accepted replay architecture;
5. rerun focused M06 acceptance and full regression;
6. do not begin M07+;
7. publish a matching C003 builder log and return for independent audit.
