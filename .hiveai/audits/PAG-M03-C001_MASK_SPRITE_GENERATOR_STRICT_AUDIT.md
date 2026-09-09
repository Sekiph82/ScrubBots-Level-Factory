# PAG-M03-C001 — Mask / Sprite Generator

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09  
Auditor: ChatGPT  
Cycle: `PAG-M03-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `f67e1cf446517577642f0243d89dc0fc102f6980`
- implementation commit: `19e6431ac5a508965adfbe2953e6e4aa35b702a8`
- builder-log publication commit / terminal builder-era HEAD: `15363eb9d49d4e8791bfe0e038f9e83017c503fc`

Primary conceptual reference:
`zfedoran/pixel-sprite-generator@8c2cee790b0ae5885319181e56745ae45a0f8138`

## 1. VERDICT

**FAIL**

The M03 implementation establishes a real deterministic MASK pipeline and passes many structural contracts, but it does not yet satisfy the milestone's reproducibility and visual-quality acceptance gates.

Findings:

- **F-PAG-M03-C001-001 — BLOCKER — supplied RNG coherence can be bypassed with a non-root domain stream, allowing output that does not match the recorded provenance.**
- **F-PAG-M03-C001-002 — MAJOR — default colorization produces substantial single-pixel color salt / fragmented regions.**
- **F-PAG-M03-C001-003 — MAJOR — outline/body/detail semantic color roles required by PAG-0330 are not implemented.**
- **F-PAG-M03-C001-004 — MAJOR — manual review evidence does not demonstrate sufficiently recognizable/distinct template families; forced four-way template symmetry is a primary cause.**

PAG-M04 must remain blocked.

A bounded `PAG-M03-C002` remediation is required.

## 2. CONTRACT RECOVERY

M03 was required to deliver:

- deterministic generic mask engine;
- REQUIRED/FORBIDDEN/RANDOM semantics;
- optional symmetry/asymmetry;
- deterministic mutation and placement;
- ten original SCRUBBOTS-owned template families;
- deterministic canonical region coloring;
- exact legal used-color count;
- no BG01/transparency in logical output;
- no default single-pixel color salt;
- coherent connected color regions;
- semantic outline/body/detail roles;
- deterministic recoloring preserving geometry;
- >=100 accepted deterministic candidates with zero palette/dimension violations;
- committed review evidence demonstrating recognizable family diversity.

M03 also had to preserve M02 deterministic/provenance truth and use a supplied project RNG coherently with the request master seed.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `f67e1cf...` to `15363eb...` shows exactly two M03 commits:

1. `19e6431ac5a508965adfbe2953e6e4aa35b702a8` — M03 implementation/tests/review evidence.
2. `15363eb9d49d4e8791bfe0e038f9e83017c503fc` — matching builder log.

Changed scope is limited to:

- `src/scrubbots_pixel_factory/generators/mask/**`;
- generator package exports;
- M03 unit/integration/golden tests;
- M03 review builder/manifest/contact sheet;
- test isolation fixture;
- matching builder log.

No PAG-M04+ production module was introduced.

No main ScrubBots mutation is present.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Task / criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0301..PAG-0310 generic mask engine | PASS | Immutable mask structures, hard/random states, seeded resolution, symmetry, mutation, rectangles and occupancy checks exist. |
| PAG-0311..PAG-0320 ten family definitions | PASS | Ten project-owned procedural family builders exist; no external art dependency found. |
| PAG-0321 multiple seeds | PASS | Family tests use multiple fixed seeds and require variation. |
| PAG-0322 all production difficulty bands | PASS | Representative square/rectangular matrix is covered. |
| PAG-0323 logical scaling without interpolation | PASS | Integer target-dimension construction; no image resize/interpolation dependency. |
| PAG-0324 negative space | PASS | Internal foreground mask retains nonzero negative-space classification. |
| PAG-0325 non-empty subject | PASS | Resolved masks require foreground. |
| PAG-0326 canonical region coloring | PASS | Final cells use selected C01..C16 only. |
| PAG-0327 exact legal distinct-color count | PASS | Result contract and palette subset usage enforce legality. |
| PAG-0328 avoid single-pixel color salt by default | **FAIL** | Independent review-manifest analysis found singleton color components in 39/40 review candidates; worst examples contain 24. |
| PAG-0329 prefer coherent connected color regions | **FAIL** | Many review outputs contain heavily fragmented same-color components; current random-anchor Voronoi colorizer does not enforce minimum connected region size. |
| PAG-0330 semantic outline/body/detail roles | **FAIL** | No semantic role model exists in production colorizer; colors are assigned from random foreground anchors plus one base color. |
| PAG-0331 no BG01 logical cells | PASS | Source/tests/review manifest exclude BG01. |
| PAG-0332 every resolved palette color actually appears | PASS | Colorizer/result tests enforce exact set equality. |
| PAG-0333 deterministic recoloring preserves geometry | PASS | Colorizer is deterministic and does not mutate the foreground mask classification. |
| PAG-0334 >=100 deterministic candidates | PASS / REVALIDATE | Builder reports 120/120 accepted and integration test encodes the 120-candidate matrix. Must be rerun after remediation changes. |
| PAG-0335 zero accepted palette/dimension violations | PASS / REVALIDATE | Current batch reports zero violations. Must be rerun after remediation changes. |
| PAG-0336 manual contact sheet demonstrates recognizable different families/seeds | **FAIL** | Independent manifest-based visual review found multiple families too blob-like or mutually similar for closure. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: matching builder log existed before M03 product edits

The log chronology states that the matching log was created before synchronization completion and before product/review edits.

No repository evidence contradicts the claim.

Disposition: **ACCEPTED**

This corrects the process-ordering defect carried from M02.

### Claim: supplied RNG coherence is validated

Current generator checks:

`stream.stage_seeds() == DeterministicRNG(request.seed).stage_seeds()`

This is not sufficient with the current M02 RNG semantics.

`DeterministicRNG.stage_seed()` and `retry_seed()` depend on root seed material but **not on the stream's current domain**.

By contrast, `child()`, `retry_rng()`, and `stage_rng()` derive executable stream keys from `self.domain`.

Independent adversarial reproduction showed:

- `DeterministicRNG(11).stage_seeds() == DeterministicRNG(11, "evil").stage_seeds()` → **true**
- root `retry/0/geometry` stream digest differs from non-root `evil/retry/0/geometry` stream digest.

Therefore a non-root supplied RNG with the correct seed passes the coherence check but drives different geometry/color streams while the resulting provenance still records root-derived stage/retry seed values.

Disposition: **REJECTED**

### Claim: default coloring avoids color salt and prefers coherent regions

Independent analysis of committed `m03_review_manifest.json` computed 4-neighbor same-color connected components for all 40 review candidates.

Results:

- candidates containing at least one singleton color component: **39 / 40**
- SEA_CREATURE / EASY: **24** singleton components
- CREATURE / VERY_HARD: **24**
- FISH / EASY: **22**
- FISH / VERY_HARD: **22**
- INSECT / VERY_HARD: **20**

This is not an edge case.

Disposition: **REJECTED**

### Claim: ten families provide recognizable review evidence

The review manifest does cover all 10 families and 4 difficulties.

However, coverage is not recognizability.

Independent silhouette review of representative EASY masks found:

- `FISH` reads as a bilateral/multi-ended emblem rather than a clear fish silhouette;
- `FACE_EMBLEM` is mostly a filled symmetric mass with no clear facial feature separation;
- `TREE_PLANT` is a dense top/bottom-symmetric slab rather than a clear trunk/crown silhouette;
- `SPACE_SHIP` and `INSECT` are very dense;
- `CORAL` is strongly mirrored and emblem-like.

Independent mask Jaccard similarity at EASY includes:

- INSECT vs TREE_PLANT: **0.843**
- ROBOT vs FACE_EMBLEM: **0.668**
- SEA_CREATURE vs INSECT: **0.636**
- SPACE_SHIP vs INSECT: **0.617**

Disposition: **NOT ACCEPTED for PAG-0336**

## 6. FILE / SYMBOL EVIDENCE

### `mask/model.py`

Positive:

- immutable mask/config dataclasses;
- strict cell-state enum;
- bounded integer mutation/offset/occupancy options;
- immutable resolved mask.

Result: **PASS**

### `mask/engine.py`

Positive:

- deterministic symmetry orbits;
- REQUIRED/FORBIDDEN conflict rejection;
- RANDOM resolution per symmetry orbit;
- bounded mutation;
- occupancy fail-closed behavior.

Result: **PASS**

### `mask/templates.py::_finish`

Problematic design:

`_finish()` mirrors **every REQUIRED cell across both horizontal and vertical axes** for every family before the configured engine symmetry mode is applied.

This makes four-way hard symmetry intrinsic to all templates, including directional/organic families such as:

- FISH;
- TREE_PLANT;
- CORAL;
- CREATURE.

Consequences visible in review evidence:

- directional cues are duplicated;
- top/bottom structures become emblem-like;
- family silhouettes converge toward large centered symmetric masses;
- placement offsets become a mirrored union rather than a simple translated subject.

This is a major contributor to F-004.

### `mask/colorize.py::colorize_mask`

Current model:

1. select one palette ID as base/background-classification color;
2. choose shuffled foreground coordinates as one anchor per remaining color;
3. assign every other foreground cell to nearest random anchor.

There is no:

- outline extraction;
- body/primary role;
- detail/accent role model;
- minimum region size;
- connected-region cleanup;
- singleton prevention.

This directly explains F-002 and F-003.

### `mask/generator.py::generate_candidate`

Positive:

- MASK-only mode;
- explicit theme/style/options failure semantics;
- M02 validated result use;
- bounded retries;
- exact palette resolution;
- authenticated result provenance format.

Blocking issue:

The supplied RNG coherence check validates only root-derived `stage_seeds()`, not that `stream.domain == "root"` or that executable child streams match the canonical request root stream.

Result: **FAIL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- focused M03 suite: `40 passed`;
- full repository: `164 passed`;
- review/golden validation: `3 passed`;
- 120-candidate batch: `120 accepted`, zero palette/dimension violations.

These are builder claims.

Independent audit additionally performed:

1. source inspection of all M03 production modules;
2. review-manifest structural validation;
3. manual ASCII silhouette review for 10 EASY family representatives;
4. occupancy analysis;
5. pairwise foreground-mask Jaccard comparison;
6. same-color connected-component/singleton analysis;
7. adversarial RNG-domain analysis.

The independent analysis exposed issues not covered by the passing suite.

Missing tests include:

- non-root-domain supplied RNG rejection;
- zero/default bounded singleton-color-region policy;
- semantic color-role behavior;
- recognizability/family-separation acceptance metric/manual gate beyond manifest coverage.

## 8. REGRESSION EVIDENCE

M00-M02 source is not modified by the M03 implementation.

No network/runtime dependency was added.

M02 result factory/invariant usage is preserved.

No M04+ production source exists.

Builder reports full suite green.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no network imports;
- no cloud/API;
- no subprocess;
- no global random;
- no Python `hash()` output dependence;
- no copied external artwork found;
- logical grid contains canonical C-IDs only.

Integrity problem:

The supplied-RNG domain hole allows generation behavior that cannot be reproduced from the recorded root provenance.

Result: **FAIL**

## 10. ARCHITECTURE CONSISTENCY

The broad layering is good:

- M01 contracts;
- M02 request/RNG/result;
- M03 generator package;
- review-only artifacts isolated from production exporter scope.

However, two architectural quality gaps remain:

1. template geometry hardcodes four-way symmetry independent of configured symmetry semantics;
2. colorization has no semantic-region layer despite PAG-0330.

Result: **FAIL**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- Codex did not edit task/H!veAI acceptance state;
- matching log exists;
- failures/corrections are recorded;
- source/log publication commits are separate and bounded;
- no self-audit verdict is asserted.

The builder log's statement that review evidence satisfies M03 should be treated as builder evidence only; manual recognizability belongs to ChatGPT and fails here.

Result: **PASS**

## 12. FINAL REPOSITORY STATE

Builder implementation commit:

`19e6431ac5a508965adfbe2953e6e4aa35b702a8`

Builder-log commit / terminal builder-era HEAD:

`15363eb9d49d4e8791bfe0e038f9e83017c503fc`

No unauthorized product scope was found.

Implementation is published but M03 is not accepted.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M03-C001-001 — BLOCKER

**Non-root supplied RNG domains pass coherence while producing different executable streams from recorded provenance.**

Affected:

- `core/rng.py`
- `generators/mask/generator.py`

Required target:

MASK generator must accept only a canonical request-root RNG or otherwise verify the executable stream identity, not merely root stage-seed metadata.

The simplest M03 fix is to require:

- exact project RNG type;
- `rng.domain == "root"`;
- root stage seeds equal request-derived root stage seeds.

Do not change M02 RNG algorithm/version in this remediation unless absolutely necessary.

### F-PAG-M03-C001-002 — MAJOR

**Default colorizer violates no-salt/coherent-region intent.**

Affected:

`generators/mask/colorize.py`

Required target:

- no isolated single-cell color regions by default;
- minimum deterministic region-size policy;
- coherent connected regions;
- all selected palette IDs still used.

### F-PAG-M03-C001-003 — MAJOR

**PAG-0330 semantic color roles are absent.**

Required target:

Implement explicit deterministic roles, at minimum:

- negative_space/base;
- outline;
- body/primary;
- secondary/detail/accent as palette cardinality permits.

Roles must map only to selected canonical IDs and must not enter logical cells as metadata values.

### F-PAG-M03-C001-004 — MAJOR

**Manual recognizability/family separation is insufficient.**

Required target:

- redesign template finishing so vertical/horizontal hard mirroring is not automatically forced onto every family;
- preserve directional/organic cues;
- make FISH, TREE_PLANT, CORAL, FACE_EMBLEM, etc. clearly family-specific;
- regenerate review evidence;
- manual contact sheet must show recognizable and distinct structures across families/seeds/difficulties.

## 14. DEFECTS BY SEVERITY

### BLOCKER

- F-PAG-M03-C001-001

### MAJOR

- F-PAG-M03-C001-002
- F-PAG-M03-C001-003
- F-PAG-M03-C001-004

### MINOR

None.

### NOTE

The exact Windows `164 passed` full-suite command was not independently rerun by ChatGPT. The audit findings are based on direct committed source and committed review-manifest evidence, so they do not depend on reproducing the builder test environment.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after remediation:

- separate template hard constraints from optional symmetry decoration;
- consider explicit per-family geometry metadata for semantic color regions;
- keep review/contact-sheet generation review-only until M08;
- later M07 quality filters can measure fragmentation, but M03 must already avoid obvious default salt rather than defer all quality responsibility.

## 16. UNVERIFIED ITEMS

The exact builder test/performance commands were not independently executed on the owner's Windows environment.

The review manifest itself was independently analyzed.

## 17. REGRESSION RISK

**MEDIUM**

Template/colorization changes will alter M03 golden hashes and review artifacts by design.

M00-M02 golden behavior must remain unchanged.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct current GitHub source inspection;
- exact M03 commit/diff scope;
- independent review-manifest parsing;
- independent silhouette rendering;
- connected-component/singleton analysis of all 40 committed review candidates;
- pairwise family-mask similarity analysis;
- direct adversarial reasoning/reproduction of RNG-domain mismatch.

## 19. FINAL VERDICT

**FAIL**

`PAG-M03-C001` is not accepted.

Validated generic engine/family infrastructure should be retained.

PAG-M04 remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M03-C002 — Reproducibility, Region Quality & Recognizability Remediation`

Required work:

1. close non-root supplied-RNG coherence/provenance hole;
2. eliminate default single-pixel color salt;
3. add coherent deterministic region-size behavior;
4. implement semantic color roles;
5. redesign family finishing/symmetry so family cues remain recognizable;
6. regenerate M03 family goldens;
7. regenerate review manifest/contact sheet;
8. rerun >=120 deterministic acceptance batch;
9. re-prove zero accepted palette/dimension violations;
10. re-prove M00-M02 full regression;
11. do not begin M04.
