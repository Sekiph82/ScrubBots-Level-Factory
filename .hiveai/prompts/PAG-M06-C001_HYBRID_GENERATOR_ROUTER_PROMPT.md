# PAG-M06-C001 — Hybrid Generator Router

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

## 1. Objective

Implement and prove **PAG-M06 — Hybrid Generator Router** only.

M06 must:

- route explicit MASK, RULES, WFC, and HYBRID modes deterministically;
- add AUTO only after explicit routing is independently testable inside the cycle;
- keep existing MASK/RULES/WFC generators independently usable and unchanged in behavior;
- implement all four named HYBRID strategies;
- produce at least two accepted deterministic hybrid strategies;
- preserve exact resolved dimensions and canonical palette throughout every stage;
- record actual selected engine/version and stage-by-stage reproducibility metadata;
- never silently hide an engine failure unless an explicit AUTO fallback policy permits it;
- reject any hybrid output that destroys required topology or M03/M04 quality invariants;
- never resize/interpolate.

Do not begin PAG-M07+, M08+, M09+, M10+, or Godot integration.

## 2. Existing accepted engines are dependencies, not rewrite targets

Accepted engines:

- MASK: `MaskSpriteGenerator`
- RULES: `RuleShapeGenerator`
- WFC: `WFCGenerator`

Preserve their accepted contracts.

Do not weaken:

- canonical root-RNG checks;
- M03 zero-singleton/semantic role behavior;
- M04 base↔negative geometry fidelity;
- M05 exemplar/palette/retry contracts.

M06 should compose these engines through public/internal candidate interfaces where appropriate, not duplicate their algorithms.

## 3. Mandatory builder log

Create **before the first source, test, golden, review, or documentation edit**:

`.hiveai/codex-logs/PAG-M06-C001_HYBRID_GENERATOR_ROUTER_CODEX_LOG.md`

Exact H1:

`# PAG-M06-C001 — Hybrid Generator Router`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- authority/audit URLs;
- branch/HEAD/origin/ahead-behind/status;
- synchronization;
- mandatory reads;
- router/AUTO architecture;
- hybrid stage-seed architecture;
- files changed;
- commands;
- failures/corrections;
- explicit-route tests;
- AUTO determinism/fallback tests;
- each hybrid strategy evidence;
- topology/palette/dimension evidence;
- stage provenance/reproduction evidence;
- acceptance/review evidence;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit or modify ChatGPT-owned acceptance/tracker state.

## 4. Mandatory reads

Before implementation read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. M05 C002 strict audit
9. M02 request/RNG/result/generator contracts
10. M03 MaskCandidate/MaskSpriteGenerator + color roles
11. M04 RuleCandidate/RuleCanvas/colorizer/RuleShapeGenerator
12. M05 WFCCandidate/WFCGenerator/ExemplarRegistry
13. this prompt

## 5. Package architecture

Create a project-owned orchestration package, conceptually:

```text
src/scrubbots_pixel_factory/generators/router/
  __init__.py
  model.py
  router.py
  hybrid.py
```

Exact filenames may differ.

Recommended public concepts:

- `GeneratorRouter`
- `HybridGenerator`
- `HybridStrategy`
- `HybridCandidate`
- `AutoCandidate`
- immutable stage metadata record.

Do not put routing logic inside the individual MASK/RULES/WFC engines.

## 6. PAG-0601 / PAG-0602 — explicit deterministic routing

`GeneratorRouter` must route:

- MASK -> MaskSpriteGenerator
- RULES -> RuleShapeGenerator
- WFC -> WFCGenerator
- HYBRID -> HybridGenerator

Explicit routing requirements:

- no random engine choice;
- same request uses the same engine;
- supplied root RNG remains canonical;
- engine result/failure is surfaced truthfully;
- no fallback for explicit modes;
- selected engine ID/version is observable.

For explicit MASK/RULES/WFC requests, returning the accepted engine's GenerationResult directly is preferred.

For HYBRID, return the HybridGenerator result.

Inject WFC registry/generator dependencies explicitly so tests can use synthetic fixtures while production defaults remain empty.

## 7. PAG-0603 / PAG-0604 — add AUTO after explicit routes are stable

Current M02 `GeneratorMode` intentionally excludes AUTO.

After explicit routing tests pass, extend the enum/parser with:

`AUTO = "AUTO"`

Requirements:

- existing MASK/RULES/WFC/HYBRID canonical request bytes remain unchanged;
- old M02 request/golden behavior does not drift;
- AUTO becomes a valid GenerationRequest mode;
- no schema-version bump is required if existing serialized forms remain byte-identical.

Update the existing comment that AUTO is intentionally absent.

### AUTO options

Use strict namespace:

- namespace: `auto`
- version: `1`

Supported values:

- `candidates`: ordered non-empty list of explicit modes from MASK/RULES/WFC/HYBRID;
- `configs`: optional mapping mode -> child request config;
- `fallback_on_failure`: boolean, default false.

Default candidates:

`["MASK", "RULES"]`

Do not default production AUTO to WFC because the production WFC registry is intentionally empty.

### AUTO child config

A per-mode child config may contain only:

- `style`
- `theme`
- `generator_options`

where generator_options is the standard:

```json
{
  "namespace": "...",
  "version": 1,
  "values": {}
}
```

Unknown config fields fail closed.

If a selected mode has no child config:

- MASK/RULES may use their valid default style/options behavior;
- WFC/HYBRID may fail explicitly if required configuration/exemplar is unavailable.

### AUTO selection

Resolve outer dimensions and palette once.

Choose the first selected AUTO mode using a deterministic named domain:

`root.child("auto/selection")`

Candidate ordering must be preserved exactly as supplied.

Do not sort user candidate order.

### AUTO fallback

If `fallback_on_failure == false`:

- try exactly the selected mode;
- surface that engine's failure as an AUTO failure;
- do not try another engine.

If `fallback_on_failure == true`:

- deterministic fallback is explicitly permitted;
- try remaining candidates in cyclic order after the initially selected candidate;
- record every attempted engine and stable failure code;
- stop on first success;
- if all fail, return a bounded deterministic failure summary.

Do not hide failed engine attempts from AutoCandidate metadata.

## 8. Derived stage seeds: critical integration rule

Existing accepted engines require their supplied RNG to be a canonical **root** RNG.

Therefore M06 must **not** pass a non-root child RNG directly into MASK/RULES/WFC.

For every AUTO child engine and every HYBRID stage:

1. derive a stable stage-seed string from the outer root through a named child domain;
2. build a child GenerationRequest using that derived seed;
3. construct/use `DeterministicRNG(stage_seed)` as the child engine's root;
4. record the derived stage seed.

Recommended derivation:

```python
stage_seed = outer_root.child(
    f"hybrid/{strategy}/{attempt}/{stage_index}/{stage_name}"
).next_bytes(32).hex()
```

AUTO analog:

```text
auto/{selected_mode}/{attempt_index}
```

Equivalent deterministic domain-separated derivation is acceptable.

Do not consume one stage RNG to derive another stage seed.

## 9. Outer dimensions and palette are authoritative

For AUTO and HYBRID:

Resolve outer request exactly once:

- `width, height = request.resolve_dimensions()`
- `palette = request.resolve_palette_subset()`

Every child/stage request must receive:

- explicit `width`;
- explicit `height`;
- explicit `palette_subset=palette`.

This prevents a derived stage seed from re-selecting different dimensions or palette.

Required invariant:

```text
every stage width  == final width
every stage height == final height
every stage requested palette == outer palette
```

No crop, resize, interpolation, resampling, or scale.

## 10. Stage metadata / reproducibility

Define an immutable stage metadata record.

At minimum each stage records:

- stage index;
- stage name;
- stage kind/engine;
- derived stage seed;
- child request digest;
- engine ID;
- engine version;
- child result digest or stable failure code;
- geometry/topology digest where relevant;
- extra engine-specific digest where relevant:
  - MASK mask/family;
  - RULES canvas/recipe;
  - WFC exemplar ID + pattern table digest + attempt.

Hybrid metadata must record:

- strategy;
- outer master seed;
- resolved dimensions;
- resolved palette;
- outer attempt;
- every stage record in exact order;
- final topology digest;
- final logical-grid digest.

AUTO metadata must record:

- candidate order;
- deterministic initial selection;
- fallback policy;
- attempted engine records;
- actual successful engine ID/version if any.

Metadata must be deeply immutable or defensively copied.

## 11. Final GenerationResult contract for AUTO

An AUTO success must produce a GenerationResult whose:

- request is the original AUTO request;
- generator_mode is AUTO;
- width/height are outer resolved dimensions;
- logical grid is the actual selected engine output;
- used palette is actual canonical palette;
- seed is outer master seed;
- M02 provenance uses the **outer** root stage seeds;
- generator_id/version identify the actual engine that produced the final logical grid.

Actual selected mode must additionally be present in AutoCandidate metadata.

Do not return the child engine's GenerationResult directly because its request/seed/mode belong to the child request.

AUTO failure must likewise use the original AUTO request.

## 12. Final GenerationResult contract for HYBRID

Hybrid success:

- request = original HYBRID request;
- generator_mode = HYBRID;
- generator_id = stable hybrid engine ID, recommended `hybrid-compose`;
- generator_version = stable version, recommended `1.0.0`;
- seed = outer master seed;
- outer root M02 provenance only;
- exact final width/height;
- exact actual palette.

Stage-specific seeds/results belong in HybridCandidate metadata, not unsupported M02 provenance fields.

## 13. HYBRID options

Use strict namespace:

- namespace `hybrid`
- version `1`

Required:

- `strategy`

Optional strategy-specific fields:

- `mask_style`
- `rules_style`
- `wfc_exemplar_id`
- `mask_options`
- `rules_options`
- `wfc_options`
- `mask_symmetry`
- `max_attempts`

Nested options must use the normal generator-options shape.

Unknown fields fail closed.

`max_attempts` default 4, hard maximum 8.

Do not silently infer a production WFC exemplar.

## 14. PAG-0607 — MASK_GEOMETRY + RULE_COLOR_REGIONS

Canonical strategy ID:

`MASK_GEOMETRY_RULE_COLOR_REGIONS`

Required flow:

1. Run MASK stage with derived root stage seed.
2. Obtain MaskCandidate foreground classification.
3. Convert the mask foreground/negative classification into a RuleCanvas or equivalent RULES color-region input at the **same dimensions**.
4. Use M04's accepted region-driven colorization contract to color that geometry.
5. Preserve exact mask foreground topology:
   - final base-vs-non-base classification must equal mask negative-vs-foreground classification.
6. Use exact outer palette.
7. Reject if M04 minimum component/dominance constraints cannot be satisfied.

Do not use MASK's already-colored grid as fake RULE color regions.

Record both mask geometry evidence and rule-color stage evidence.

## 15. PAG-0608 — RULE_GEOMETRY + MASK_SYMMETRY

Canonical strategy ID:

`RULE_GEOMETRY_MASK_SYMMETRY`

Required flow:

1. Run RULES geometry stage.
2. Extract RuleCanvas occupied topology.
3. Apply a project-owned symmetry transform using the already-defined M03 `SymmetryMode` semantics.
4. Do not resize or regenerate the geometry from a mask template.
5. Preserve original occupied cells and add their deterministic mirror union, unless explicit strategy config documents another fail-closed operation.
6. Convert transformed topology back to a RuleCanvas/equivalent.
7. Re-color with M04 region-driven colorization using the exact outer palette.

`mask_symmetry` must be explicit or use a documented default such as HORIZONTAL.

Reject ASYMMETRIC for this strategy if it would make the "MASK_SYMMETRY" stage a no-op, unless explicitly tested/documented.

Topology metadata must record before/after occupancy digests and symmetry mode.

## 16. PAG-0609 — RULE_BASE + WFC_DETAIL

Canonical strategy ID:

`RULE_BASE_WFC_DETAIL`

WFC detail requires an explicit eligible exemplar ID in M06 V1.

Production default registry remains empty.

Tests may inject M05 synthetic exemplars.

Required flow:

1. Run RULES base stage.
2. Run WFC detail stage at **exactly the same outer dimensions and outer palette**.
3. Use WFC output only as deterministic detail information.
4. Apply detail only to RULES occupied cells.
5. Never write non-base colors into RULES negative-space cells.
6. Never write RULES base color into occupied cells.
7. Preserve RULES occupied/negative topology exactly.

A valid V1 overlay method:

- begin from accepted RuleCandidate final grid;
- for each occupied cell, WFC non-base logical values may replace the current occupied color;
- WFC base-color cells do not overwrite occupied cells;
- negative-space cells remain untouched.

Equivalent deterministic detail mapping is acceptable if topology is exact.

After overlay, reject rather than repair if:

- actual palette no longer equals outer palette;
- any same-color component violates the accepted M04 minimum region size;
- topology differs;
- off-palette cells appear.

Do not inject missing colors afterward.

## 17. PAG-0610 — MASK_BASE + WFC_DETAIL

Canonical strategy ID:

`MASK_BASE_WFC_DETAIL`

Required flow:

1. Run MASK base stage.
2. Run WFC detail stage same dimensions/palette.
3. Preserve MaskCandidate foreground/negative classification exactly.
4. WFC detail may recolor only foreground cells.
5. Negative-space/base cells remain untouched.
6. Reject output if exact palette, min-component quality, or topology contracts fail.

Use M03 semantic role assignment to identify the MASK negative-space/base color rather than assuming palette[0] if M03 metadata provides the exact role mapping.

## 18. PAG-0611 / PAG-0612 — dimensions and palette

Every successful hybrid output must prove:

- every stage fixed W×H;
- final W×H;
- no interpolation/resize;
- every logical cell C01..C16;
- exact outer resolved palette is actually used;
- no BG01/None/sentinel.

A stage may fail if its own contract cannot use the outer palette.

Do not silently choose a different palette for a child stage.

## 19. PAG-0613 — stage-by-stage provenance

HybridCandidate metadata must be sufficient to reproduce every stage.

Add a reproduction helper/test that:

1. takes the original HYBRID request + recorded stage metadata;
2. independently reconstructs each child stage request;
3. re-runs each stage;
4. compares child request/result/geometry digests;
5. compares final logical grid digest.

Do not depend on mutable current defaults when metadata already records explicit stage config.

## 20. PAG-0614 — topology/quality rejection

Define stable hybrid rejection codes/reasons, conceptually:

- STAGE_FAILED
- DIMENSION_DRIFT
- PALETTE_DRIFT
- TOPOLOGY_DESTROYED
- SINGLETON_COLOR_REGION
- INVALID_STAGE_METADATA
- RETRY_EXHAUSTED

Use existing M02 FailureCode externally where required, with stable hybrid reason text.

At minimum reject:

- WFC detail writes foreground color into negative topology;
- WFC detail causes base color inside occupied topology;
- final palette loses a selected color;
- final component minimum violated;
- symmetry stage changes dimensions;
- any stage result dimensions differ.

Do not repair topology after detecting destruction.

## 21. Hybrid retries

Hybrid composition may need bounded retries because final quality/palette checks can fail.

Use:

- default 4 attempts;
- max 8.

Attempt-specific stage seeds must include the outer attempt index.

Same HYBRID request must reproduce:

- same attempt sequence;
- same stage seeds;
- same stage outcomes;
- same accepted final grid or same terminal failure.

Do not reuse a successful stage from another attempt unless the metadata contract explicitly records such memoization. V1 should simply rerun the bounded stage sequence.

## 22. PAG-0615 — acceptance: at least two hybrid strategies

All four strategy code paths must exist and have focused tests.

At least **two strategies must demonstrate accepted deterministic production-contract outputs** without relying on unavailable owner art:

Required robust acceptance strategies:

1. MASK_GEOMETRY_RULE_COLOR_REGIONS
2. RULE_GEOMETRY_MASK_SYMMETRY

WFC-detail strategies may use injected synthetic M05 exemplars in tests/review evidence.

Strong preference:

- demonstrate accepted outputs for all four strategies in tests.

Minimum acceptance matrix:

- all 4 difficulties;
- representative rectangles;
- at least 3 seeds per robust strategy.

For each accepted candidate:

- byte-identical rerun;
- exact dimensions/palette;
- topology invariant;
- no singleton components where M04 quality applies;
- complete stage metadata.

## 23. PAG-0616 — metadata reproducibility

Add dedicated tests that perturb no global state and prove:

- stage seeds rederive exactly;
- child requests match recorded digests;
- actual engine IDs/versions match records;
- WFC exemplar/pattern table digest matches when applicable;
- final digest matches.

Metadata must not contain absolute machine paths or timestamps needed for reproduction.

## 24. PAG-0617 — no interpolation/resizing

Production router/hybrid code must not call:

- resize;
- resample;
- interpolation;
- image scale/crop;
- PIL/OpenCV image transforms.

Geometry transforms are logical coordinate transforms only.

Add source-policy tests.

## 25. AUTO acceptance

Add focused AUTO tests:

- GeneratorMode.AUTO parses;
- existing mode canonical bytes unchanged;
- default candidates MASK/RULES;
- same AUTO request selects same engine;
- different fixed seeds produce at least two selected modes across a fixed seed set;
- fallback=false surfaces selected engine failure;
- fallback=true may try next candidate and records failed attempt;
- AUTO success wraps selected child output into original AUTO request/result contract;
- actual engine ID/version recorded;
- dimensions/palette outer-authoritative;
- no WFC selected by default production AUTO.

Do not claim AUTO is visually intelligent; it is deterministic mode routing only.

## 26. Explicit router tests

At minimum:

- explicit MASK route equals direct MASK result;
- explicit RULES route equals direct RULES result;
- explicit WFC route equals direct WFC result with injected test registry;
- explicit HYBRID route equals direct HybridGenerator result;
- wrong/unknown mode impossible through GenerationRequest contract;
- root RNG coherence preserved.

## 27. Review-only evidence

Create:

`review/m06/m06_review_manifest.json`

and:

`review/m06/M06_HYBRID_CONTACT_SHEET.html`

Review-only, non-production.

Minimum:

- >=12 accepted hybrid examples;
- both required robust strategies represented;
- WFC-detail examples represented if they pass with injected synthetic exemplars;
- all four difficulties collectively;
- rectangles;
- multiple seeds;
- stage metadata summary;
- before/after topology masks where applicable;
- final colored output.

For each candidate display:

- strategy;
- master seed;
- dimensions;
- palette;
- stage names;
- stage seeds;
- engine IDs/versions;
- final topology digest;
- final result digest.

Self-contained/no CDN.

## 28. Golden evidence

Create compact:

`tests/golden/m06_hybrid_goldens.json`

At minimum:

- one MASK_GEOMETRY_RULE_COLOR_REGIONS case;
- one RULE_GEOMETRY_MASK_SYMMETRY case;
- one WFC-detail case if stable;
- one rectangular case;
- one VERY_HARD case.

Record:

- outer request;
- strategy;
- stage seed list;
- stage engine IDs/versions;
- stage request/result/geometry digests;
- final grid digest;
- final GenerationResult digest.

## 29. Full regression / offline boundary

All M00-M05 tests must remain green.

M06 production code must:

- be offline;
- add no networking;
- add no new runtime dependency;
- use no global random;
- use no Python hash for canonical behavior;
- run no subprocess;
- use no eval/exec;
- use no arbitrary request file paths.

WFC owner registry remains empty by default.

## 30. Prohibited shortcuts

Do not:

- modify MASK/RULES/WFC outputs to make direct-engine tests pass differently;
- pass non-root child RNGs into accepted engines;
- let stage seed alter dimensions/palette;
- call one engine and merely relabel its result HYBRID;
- implement RULE_GEOMETRY_MASK_SYMMETRY by generating a new unrelated MASK template;
- let WFC detail alter negative/foreground topology;
- inject missing palette colors after hybrid generation;
- resize/crop stages to reconcile mismatch;
- silently fallback in explicit mode;
- silently fallback in AUTO when fallback_on_failure=false;
- fabricate owner-approved WFC exemplars;
- begin M07+;
- edit ChatGPT-owned task/tracker/audit state;
- self-audit.

## 31. Required verification before handoff

Run and log:

- existing-mode request serialization regression;
- explicit router tests;
- AUTO tests;
- hybrid stage-seed tests;
- all four hybrid strategy focused tests;
- topology rejection tests;
- palette/dimension invariant tests;
- metadata reproduction tests;
- M06 golden tests;
- review manifest/contact-sheet validation;
- deterministic hybrid acceptance matrix;
- full M00-M05 regression;
- standalone import;
- `pip check`;
- offline/source-policy scans;
- no-random/no-hash/no-subprocess/no-eval scans;
- `git diff --check`;
- source scan proving no M07+ implementation.

## 32. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- PAG-0601..PAG-0617 have implementation/test evidence;
- explicit MASK/RULES/WFC/HYBRID routing is deterministic;
- AUTO exists and is seed-deterministic;
- AUTO actual selected engine/version is recorded;
- hidden fallback is impossible unless explicitly enabled;
- all four hybrid strategy paths exist;
- at least two strategies have accepted deterministic outputs across difficulty/rectangle evidence;
- all stages preserve exact dimensions and outer palette;
- hybrid stage seeds and engine metadata reproduce every stage;
- topology-destroying hybrids reject;
- no interpolation/resizing exists;
- review/golden evidence is committed;
- full M00-M05 regression is green;
- no M07+ implementation exists;
- matching builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M06. ChatGPT will independently audit.
