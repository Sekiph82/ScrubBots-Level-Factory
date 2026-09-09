# PAG-M06-C001 — Hybrid Generator Router

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09  
Auditor: ChatGPT  
Cycle: `PAG-M06-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited builder boundary:
- cycle base / prompt-ready state: `c4682b0eab42f5f577f6d58a3ecd6ceab832f8e1`
- implementation commit: `f7dd1ae3f15eb5d265b341c694a2e028b4337cb5`
- builder-log publication / terminal builder-era HEAD: `318b97b9c33a3b35a2ef6bbde9b348331cf74b83`

Post-builder control-plane migration:
- `279f978dd9e73f08abe2ab3f8b2f313c84260ef2` — GitHub-first v3 tracking migration.
- This migration is not part of the M06 product implementation diff.

## 1. VERDICT

**FAIL**

M06 contains a valid deterministic router and two robust accepted hybrid strategies, but four acceptance/contract findings remain.

Open findings:

- **F-PAG-M06-C001-001 — MAJOR — WFC-detail hybrid strategies overwrite WFC source→target palette mapping with an outer-palette identity mapping, so valid non-identity exemplar palettes fail.**
- **F-PAG-M06-C001-002 — MAJOR — `reproduce_hybrid()` does not reproduce and verify every recorded stage from stage metadata as required by PAG-0616.**
- **F-PAG-M06-C001-003 — MAJOR — required AUTO fallback/selection acceptance evidence is incomplete, especially `fallback_on_failure=true` cyclic fallback and fixed-seed mode diversity.**
- **F-PAG-M06-C001-004 — MAJOR — M06 review/golden evidence is incomplete: no before/after topology masks are committed and no WFC-detail golden exists despite stable WFC-detail examples.**

M07+ remains blocked.

A bounded `PAG-M06-C002` remediation is required.

## 2. CONTRACT RECOVERY

M06 was required to:

- route explicit MASK/RULES/WFC/HYBRID deterministically;
- add deterministic AUTO with explicit fallback policy;
- preserve accepted engine behavior;
- compose four hybrid strategies;
- preserve exact outer dimensions/palette;
- derive independent child stage seeds and feed each accepted engine a canonical root RNG;
- record actual stage engine/version/request/result/geometry evidence;
- allow every hybrid stage to be reproduced from metadata;
- reject topology/palette/component drift rather than repair it;
- produce at least two deterministic accepted hybrid strategies;
- include >=12 review examples with topology evidence;
- include deterministic goldens, including WFC detail if stable;
- never resize/interpolate.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent compare of the builder boundary shows exactly:

1. `f7dd1ae3f15eb5d265b341c694a2e028b4337cb5`
   - AUTO request-mode extension;
   - router/hybrid production package;
   - M06 tests;
   - M06 goldens;
   - M06 review evidence;
   - pre-edit-created builder log.

2. `318b97b9c33a3b35a2ef6bbde9b348331cf74b83`
   - builder-log completion publication.

The later v3 migration commit modifies only control-plane files.

No M07+ production implementation was found.

No main ScrubBots mutation was found.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Task / criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0601 MASK/RULES/WFC/HYBRID modes | PASS | Existing explicit modes preserved; AUTO additionally added. |
| PAG-0602 deterministic explicit routing | PASS | Router dispatch is direct and has no explicit-mode fallback. |
| PAG-0603 AUTO implemented | PASS | AUTO parser/router exists. |
| PAG-0604 AUTO seed-deterministic selection | PASS / TEST GAP | Source uses `root.child("auto/selection")`; same-request behavior is deterministic. |
| PAG-0605 actual selected engine/version recorded | PASS | AUTO metadata/result and stage metadata carry IDs/versions. |
| PAG-0606 hidden failure forbidden unless explicit fallback | **PARTIAL** | Source policy appears correct, but required `fallback=true` acceptance path is not tested. |
| PAG-0607 MASK_GEOMETRY_RULE_COLOR_REGIONS | PASS | Accepted across robust matrix. |
| PAG-0608 RULE_GEOMETRY_MASK_SYMMETRY | PASS | Accepted across robust matrix. |
| PAG-0609 RULE_BASE_WFC_DETAIL | **PARTIAL** | Identity-palette exemplar works; non-identity source palette mapping is broken. |
| PAG-0610 MASK_BASE_WFC_DETAIL | **PARTIAL** | Same mapping defect. |
| PAG-0611 fixed dimensions through stages | PASS | Child requests receive explicit outer W×H; independent review grid lengths all exact. |
| PAG-0612 canonical/exact palette | PASS | 14/14 committed review candidates use exact recorded palette and C01..C16 only. |
| PAG-0613 stage provenance/sub-seeds | PASS | Stage seeds/request/result/geometry metadata exists. |
| PAG-0614 topology/quality rejection | PASS | Final validation rejects dimension/palette/topology/singleton drift. |
| PAG-0615 >=2 deterministic hybrid strategies | PASS | 24-case robust acceptance matrix across 4 difficulties, rectangles, 3 seeds. |
| PAG-0616 metadata reproduces every stage | **FAIL** | Helper only re-runs whole HYBRID request and compares final digest + stage seeds. |
| PAG-0617 no interpolation/resizing | PASS | No production resize/resample/interpolation path found. |
| >=12 review candidates | PASS | 14 committed candidates. |
| all four strategies in review | PASS | 6 + 6 + 1 + 1. |
| before/after topology masks in review | **FAIL** | No topology mask data/rendering exists. |
| WFC-detail golden if stable | **FAIL** | WFC-detail is stable in tests/review but 0/4 goldens use a WFC-detail strategy. |
| full regression | PASS / builder-supported | Builder reports 241 PASS; no source contradiction found. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: all four hybrid strategy paths work

Repository truth confirms all four paths exist.

Committed review evidence includes:

- MASK_GEOMETRY_RULE_COLOR_REGIONS: 6 cases
- RULE_GEOMETRY_MASK_SYMMETRY: 6 cases
- RULE_BASE_WFC_DETAIL: 1 case
- MASK_BASE_WFC_DETAIL: 1 case

Independent review-manifest checks found:

- grid-length mismatches: **0**
- exact-palette failures: **0**
- off-canonical cells: **0**
- invalid stage-seed lengths: **0**
- recorded failed stages in accepted examples: **0**
- MASK geometry topology vs final topology digest mismatch: **0**
- RULE symmetry after-topology vs final topology mismatch: **0**
- WFC-detail base geometry vs final topology digest mismatch: **0**

However WFC-detail works only for the test exemplar whose source palette is already identical to the outer palette.

Disposition: **PARTIAL**

### Claim: WFC detail honors M05 palette mapping

Current code unconditionally replaces nested WFC palette mapping with:

`{source: target for source, target in zip(palette, palette, strict=True)}`

where `palette` is the outer requested target palette.

M05 requires explicit mapping keys to equal the exemplar source palette.

Therefore with a legal exemplar using, for example:

- source = C11,C12,C13
- target = C01,C02,C03

the hybrid generates an explicit mapping whose keys are C01,C02,C03 rather than C11,C12,C13.

M05 correctly rejects that mapping.

The same defect also overwrites a caller-supplied valid `wfc_options.palette_mapping`.

Disposition: **REJECTED**

### Claim: hybrid metadata can reproduce every stage

Current `reproduce_hybrid()`:

1. calls `generator.generate_candidate(request)`;
2. compares final logical-grid digest;
3. compares tuple of stage seeds;
4. returns.

It does **not**:

- reconstruct each child request from recorded stage metadata;
- compare recorded child request digests;
- compare stage result digests;
- compare stage geometry digests;
- compare engine ID/version;
- verify MASK family/mask digest;
- verify RULES recipe/canvas/region digest;
- verify WFC exemplar/pattern-table digest.

It also relies on the current implementation/defaults rather than replaying the recorded stage contract.

Disposition: **REJECTED for PAG-0616**

### Claim: AUTO acceptance is complete

Source behavior is promising:

- deterministic initial selection;
- default candidates MASK/RULES;
- cyclic candidate order;
- fallback is opt-in;
- attempts record mode/seed/result/engine/failure code.

Independent source-level recomputation of the project RNG shows fixed seeds do select both indices across a small seed set.

But committed tests contain:

- no `fallback_on_failure=true` test;
- no test proving cyclic fallback reaches the next candidate;
- no test proving failed-attempt metadata is retained on successful fallback;
- no fixed-seed assertion that AUTO selects at least two modes;
- no explicit HYBRID router-vs-direct equality test.

Disposition: **PARTIAL / ACCEPTANCE EVIDENCE INCOMPLETE**

### Claim: review/golden evidence meets M06 prompt

Review:

- 14 candidates;
- all four strategies;
- all four difficulties;
- 9 rectangles;
- multiple seeds;
- stage metadata present.

But the prompt explicitly required before/after topology masks where applicable.

Manifest contains topology **digests**, not topology masks.

Contact sheet renders final colored grids only.

Goldens:

- 4 entries;
- robust strategies only;
- rectangle and VERY_HARD covered;
- WFC-detail golden count: **0**.

Yet WFC-detail strategies are demonstrated stable in integration tests and review.

Disposition: **PARTIAL / REJECTED for evidence gate**

## 6. FILE / SYMBOL EVIDENCE

### `core/request.py::GeneratorMode`

AUTO is added without changing existing mode string serialization.

Result: **PASS**

### `router/router.py::GeneratorRouter`

Positive:

- explicit direct dispatch;
- canonical root RNG validation;
- deterministic AUTO selection;
- opt-in fallback architecture;
- original AUTO request is used for final AUTO result.

Evidence gap:

- fallback=true path not exercised by committed tests.

Result: **PASS source / PARTIAL acceptance**

### `router/hybrid.py::_stage_seed`

Derives a seed string from a named child domain, then child engines receive `DeterministicRNG(stage_seed)` as a root stream.

This correctly preserves M03-M05 canonical-root requirements.

Result: **PASS**

### `router/hybrid.py::_compose_attempt`

Robust strategies preserve topology and outer dimensions/palette.

WFC-detail defect:

- forcibly writes an identity mapping over the outer palette rather than mapping actual exemplar source symbols to the outer palette.

Result: **FAIL for WFC-detail generality**

### `router/hybrid.py::_validate_final`

Checks:

- exact grid length;
- C01..C16;
- exact palette set;
- exact base/non-base topology;
- no same-color singleton components.

Result: **PASS**

### `router/hybrid.py::reproduce_hybrid`

Does not implement recorded stage-by-stage replay.

Result: **FAIL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- focused M06 suites passed;
- deterministic acceptance matrix: 24 accepted robust outputs;
- full repository: 241 PASS;
- review: 14 accepted examples.

Independent audit inspected test source and found gaps:

1. no AUTO fallback=true cyclic success;
2. no fixed-seed AUTO mode-diversity test;
3. no explicit HYBRID router/direct equality test;
4. no non-identity WFC exemplar palette-remap hybrid test;
5. no stage-by-stage metadata reconstruction test;
6. no corruption test proving reproduction fails on altered stage result/geometry/engine metadata;
7. no WFC-detail golden;
8. no topology-mask review assertion.

## 8. REGRESSION EVIDENCE

M03/M04/M05 generator source was not modified.

M02 request test only removed the obsolete assertion that AUTO is invalid.

Existing explicit serialized mode values remain unchanged.

No M07+ code exists.

Builder reports 241 full-suite PASS.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no network/API/cloud;
- no new runtime dependency;
- no global random;
- no Python hash canonical behavior;
- no subprocess/eval/exec in production M06;
- no resize/resample/interpolation;
- default WFC production registry remains empty;
- no fabricated owner exemplar.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

The architecture is appropriate:

```text
outer request/root RNG
 -> deterministic route or HYBRID strategy
 -> derived stage seed strings
 -> canonical-root child engine requests
 -> logical-grid composition
 -> fail-closed topology/palette/quality validation
 -> outer GenerationResult + sidecar metadata
```

The main architecture is not rejected.

The remaining defects are:

- one cross-engine WFC palette integration bug;
- incomplete metadata replay semantics;
- incomplete acceptance/review evidence.

Result: **PARTIAL**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log is chronological enough to identify:

- initial local state;
- synchronization;
- failed command corrections;
- implementation/test evidence;
- implementation commit/push;
- final full regression.

Builder did not edit acceptance/audit state.

### Post-builder v3 migration observation

After the builder completed, commit:

`279f978dd9e73f08abe2ab3f8b2f313c84260ef2`

migrated current H!veAI truth to:

- `.hiveai/PROJECT.json`
- `.hiveai/TASKS.md`
- `.hiveai/RULES.md`
- `.hiveai/EVENTS.jsonl`

At audit start, the authoritative v3 `.hiveai/TASKS.md` still reported:

- current milestone PAG-M05;
- current task PAG-M05-C002;
- PASS_CLOSED.

That state was stale relative to repository truth:

- PAG-M06 prompt existed;
- M06 implementation/log existed;
- `.hiveai/CYCLE_INDEX.md` already named PAG-M06-C001 active.

This is a **control-plane migration inconsistency**, not an M06 builder product defect.

The independent auditor must correct v3 current-state truth after recording this verdict.

## 12. FINAL REPOSITORY STATE

Terminal builder-era HEAD:

`318b97b9c33a3b35a2ef6bbde9b348331cf74b83`

Current repository HEAD at audit start includes later control-plane migration:

`279f978dd9e73f08abe2ab3f8b2f313c84260ef2`

No unauthorized M07+ source found.

M06 implementation is published but not accepted.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M06-C001-001 — MAJOR

**WFC-detail palette mapping assumes source palette == target palette.**

Required target:

- do not synthesize identity mapping from outer target palette;
- preserve a valid explicitly supplied WFC mapping if provided;
- otherwise allow M05 default deterministic source→target mapping;
- test an exemplar whose source C-IDs differ from the outer palette;
- both RULE_BASE_WFC_DETAIL and MASK_BASE_WFC_DETAIL must succeed deterministically with that valid remap.

### F-PAG-M06-C001-002 — MAJOR

**Hybrid reproduction helper does not replay recorded stages.**

Required target:

- reconstruct every recorded child request;
- verify derived seed;
- rerun each real engine/composition stage;
- compare child request digest;
- compare engine ID/version;
- compare child result/output digest;
- compare geometry/topology digest;
- compare engine-specific extra digest;
- verify WFC exemplar ID + pattern-table digest where applicable;
- compare final topology/grid/result digest;
- fail if any recorded stage metadata is corrupted;
- do not depend only on current defaults.

### F-PAG-M06-C001-003 — MAJOR

**AUTO fallback/selection acceptance evidence is incomplete.**

Required target tests:

- same AUTO request -> same selection/result;
- fixed seed set -> at least two modes selected;
- fallback=false -> exactly selected engine attempted;
- fallback=true -> deterministic cyclic next candidate;
- failed attempt code retained in AutoCandidate on later success;
- all-fail fallback produces stable bounded summary;
- explicit HYBRID route equals direct HybridGenerator result.

### F-PAG-M06-C001-004 — MAJOR

**Review/golden evidence lacks required topology views and WFC-detail golden.**

Required target:

- review manifest includes before/after topology masks or exact row-major boolean/bit representations for applicable hybrid stages;
- contact sheet renders topology before/after beside final colored output;
- review validation asserts topology-mask sizes/digests;
- add at least one stable WFC-detail golden using an injected synthetic test-only exemplar;
- golden replay validates WFC exemplar/pattern-table digest and all stage metadata.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- F-PAG-M06-C001-001
- F-PAG-M06-C001-002
- F-PAG-M06-C001-003
- F-PAG-M06-C001-004

### MINOR

None in product scope.

### NOTE

- H!veAI v3 current-state tracker was stale at audit start and must be corrected by ChatGPT.
- Exact owner-machine 241-test execution remains builder evidence.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after remediation:

- move generic stage replay serialization into a small reusable orchestration helper before M08 metadata/export work;
- consider giving composition-only stages an explicit `COMPOSITION` stage kind instead of presenting `rule-colorize` as if it were a full generator;
- M07 can later score cross-strategy diversity and quality, but should not repair M06 topology failures.

## 16. UNVERIFIED ITEMS

Exact Windows full-suite execution was not independently rerun.

No accepted robust-strategy dimension/palette/topology invariant remains unverified from committed source/review evidence.

AUTO fallback=true behavior remains unverified because no committed test exercises it.

## 17. REGRESSION RISK

**LOW to MEDIUM**

Required remediation should be localized to:

- WFC-detail option preparation;
- metadata replay helper/tests;
- AUTO tests and possibly narrow failure metadata handling;
- M06 review/goldens.

Core M03-M05 engines should remain unchanged.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct GitHub commit/diff inspection;
- full router/hybrid source review;
- focused test-source review;
- independent review-manifest invariant analysis;
- golden coverage analysis;
- independent M05 palette-mapping contract comparison;
- current v3 tracker inspection.

## 19. FINAL VERDICT

**FAIL**

`PAG-M06-C001` is not accepted.

Validated M06 work should be preserved.

PAG-M07+ remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M06-C002 — WFC Remap, Stage Replay & Router Evidence Remediation`

Required work only:

1. fix WFC-detail non-identity source→target palette mapping;
2. implement true recorded stage-by-stage hybrid replay/verification;
3. complete AUTO fallback/selection acceptance tests;
4. add explicit HYBRID router/direct equality test;
5. add topology before/after review evidence;
6. add a stable WFC-detail golden;
7. regenerate M06 review/golden evidence;
8. rerun M06 acceptance and full regression;
9. preserve M03-M05 source behavior;
10. do not begin M07.
