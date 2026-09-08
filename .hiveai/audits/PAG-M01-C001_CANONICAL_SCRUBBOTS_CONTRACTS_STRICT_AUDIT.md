# PAG-M01-C001 — Canonical SCRUBBOTS Contracts

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-08  
Auditor: ChatGPT  
Cycle: `PAG-M01-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `82c29c71f007371bc58059432b1e9678a0e1291d`
- implementation commit: `113e1401eba821460b9887ef84a14e2fb7c67f7c`
- log publication commit: `9ccc4e7ddee4586ced7cad126aa82e3fd6ec2c18`
- subsequent log-only SHA-record commit: `41601910c133f42753272877ad648db098ff7306`

Pinned main-game contract source:
`Sekiph82/Scrubbots@b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`

## 1. VERDICT

**PASS**

PAG-M01 is accepted.

All tasks `PAG-0101..PAG-0133` are validated complete.

The implementation faithfully reproduces the owner-locked C01..C16 palette, BG01 role, difficulty names, independent dimension bands, rectangular legality, actual-used-color bands, deterministic dimension selection, deterministic palette-subset selection, and fail-closed contract validation.

PAG-M02 may begin.

## 2. CONTRACT RECOVERY

M01 was required to establish generator-independent canonical contracts only.

The milestone contract included:

- local machine-readable C01..C16 palette copied from the pinned owner-locked main-game source;
- immutable canonical palette representation;
- exact ID/HEX/RGB lookup and reverse lookup;
- duplicate/off-palette/BG01 rejection;
- canonical ascending used-palette ordering;
- strict production difficulty enum:
  - EASY
  - MEDIUM
  - HARD
  - VERY_HARD
- independent width/height bands:
  - EASY 20..29
  - MEDIUM 30..39
  - HARD 40..49
  - VERY_HARD 50..59
- rectangular board legality;
- no EXTRA_HARD / TEST production difficulty;
- stable M01-only seeded dimension selection without introducing M02 RNG;
- actual-used-color bands:
  - EASY 3..5
  - MEDIUM 6..7
  - HARD 8..9
  - VERY_HARD 10..12
- deterministic legal palette-subset selection;
- explicit supplied-subset validation;
- no M02 GenerationRequest or generator implementation.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `82c29c71...` to current C001 end state shows three commits:

1. `113e1401eba821460b9887ef84a14e2fb7c67f7c` — product/data/tests
2. `9ccc4e7ddee4586ced7cad126aa82e3fd6ec2c18` — builder log publication
3. `41601910c133f42753272877ad648db098ff7306` — log-only record of prior log SHA

Product-scope files are bounded to:

- `data/palette/scrubbots_palette_v2.json`
- `pyproject.toml`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/contracts/__init__.py`
- `src/scrubbots_pixel_factory/contracts/_stable_select.py`
- `src/scrubbots_pixel_factory/contracts/palette.py`
- `src/scrubbots_pixel_factory/contracts/difficulty.py`
- `src/scrubbots_pixel_factory/contracts/color_usage.py`
- M01 unit/integration tests
- matching C001 builder log

No PAG-M02 GenerationRequest, RNG abstraction, generator interface, CLI, WFC, MASK, RULES, HYBRID, PNG/JSON, Godot, GUI, or gameplay implementation was introduced.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Task / criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0101 machine-readable C01..C16 data | PASS | Local JSON exists and is semantically identical to pinned main-game JSON. |
| PAG-0102 palette schema/version metadata | PASS | v2 schema/version/owner lock retained exactly. |
| PAG-0103 canonical palette loader | PASS | `load_palette()` validates and constructs immutable contract object. |
| PAG-0104 duplicate ID rejection | PASS | Direct validation path rejects duplicates. |
| PAG-0105 duplicate RGB rejection | PASS | Reverse-map ambiguity is rejected. |
| PAG-0106 reject C17+ | PASS | Strict regex/ordered canonical validation rejects C17+. |
| PAG-0107 reject BG01 logical color | PASS | Explicit logical-ID rejection; BG01 remains presentation-only. |
| PAG-0108 deterministic ID↔RGB lookup | PASS | ID→RGB/HEX and RGB/HEX→ID are deterministic. |
| PAG-0109 ascending local palette | PASS | used/subset outputs are numerically sorted by C-ID. |
| PAG-0110 exact all-16 values | PASS | Independently compared local JSON to pinned owner source; identical. |
| PAG-0111 strict four difficulties | PASS | Enum contains exactly four production values. |
| PAG-0112 exact dimension bands | PASS | Mapping matches owner lock exactly. |
| PAG-0113 width independent | PASS | Dedicated width validation. |
| PAG-0114 height independent | PASS | Dedicated height validation. |
| PAG-0115 rectangles supported | PASS | Validation and deterministic selection do not require square boards. |
| PAG-0116 reject Extra Hard | PASS | Strict parser rejects legacy name. |
| PAG-0117 reject fixed-size assumptions | PASS | API supports full ranges and rectangles; no fixed-size contract. |
| PAG-0118 deterministic auto dimension selection | PASS | SHA-256 domain-separated stable selection. |
| PAG-0119 square and rectangular auto outputs | PASS | Independent 10,000-seed stress found all 100 legal dimension pairs per difficulty and thousands of rectangles. |
| PAG-0120 boundary tests | PASS | Source tests cover outer boundaries, min/max bands, cross-band invalid axes. |
| PAG-0121 EASY 3..5 | PASS | Implemented and tested. |
| PAG-0122 MEDIUM 6..7 | PASS | Implemented and tested. |
| PAG-0123 HARD 8..9 | PASS | Implemented and tested. |
| PAG-0124 VERY_HARD 10..12 | PASS | Implemented and tested. |
| PAG-0125 count actual logical use | PASS | Distinct IDs are derived from supplied logical cells, not requested palette metadata. |
| PAG-0126 BG01 excluded/rejected | PASS | BG01 cannot enter logical-cell count. |
| PAG-0127 reject out-of-band used count | PASS | `validate_used_color_count()` fails closed. |
| PAG-0128 deterministic palette-subset selection | PASS | Stable SHA-256 ranking/size selection. |
| PAG-0129 explicit valid subset | PASS | Accepted and canonically sorted. |
| PAG-0130 reject incompatible explicit subset | PASS | duplicates, BG01, C17/off-palette, wrong size all rejected. |
| PAG-0131 legal difficulty coherent contract | PASS | Integration layer resolves legal dimensions + subset for all four difficulties without M02 GenerationRequest. |
| PAG-0132 illegal dimension/color-band rejected pre-generator | PASS | Contract validators exist before any generator implementation. |
| PAG-0133 tests independent of generator implementation | PASS | No generator package is present/imported. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: local palette semantically equals pinned owner source

Independent GitHub comparison result:

- current main-game HEAD = `b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`
- local vendored palette == pinned palette: **true**
- current main-game palette == pinned palette: **true**

This directly verifies no contract drift.

Disposition: **VERIFIED**

### Claim: deterministic dimensions/subsets

Independent audit reproduced the exact source formulas and stress-tested 10,000 integer seeds per difficulty.

Dimension results:

- all generated width/height pairs legal;
- all 100 possible dimension pairs observed for each difficulty;
- thousands of rectangular outputs observed;
- deterministic outputs remained stable.

Palette-subset results:

- all subset sizes stayed within legal band;
- all IDs unique and canonical;
- all outputs sorted ascending by C-ID;
- thousands of distinct subsets observed.

Disposition: **VERIFIED**

### Claim: package-data configuration supports installed palette data

The audit environment could not clone the GitHub repository directly because outbound DNS/network access is disabled.

However, the exact `setuptools` `data-files` configuration pattern was independently reproduced in a temporary build.

Wheel inspection showed:

`<dist>.data/data/data/palette/<file>`

and a temporary installation placed the file at:

`<sys.prefix>/data/palette/<file>`

which matches the loader fallback:

`Path(sys.prefix) / "data" / "palette" / "scrubbots_palette_v2.json"`

Disposition: **VERIFIED**

### Claim: focused/full pytest totals

Builder records:

- 51 focused M01 tests PASS
- 60 full repository tests PASS

The auditor could not directly clone the repository into the execution container because GitHub network resolution is unavailable there.

The tests and implementation were independently inspected through the connected GitHub source, and separate property/adversarial checks were run against the exact deterministic algorithms.

Disposition: **SUPPORTED BUT FULL 60-TEST COMMAND NOT INDEPENDENTLY RE-RUN**

This limitation is non-blocking because direct source truth, canonical-data equality, static architecture inspection, and independent stress validation all agree with the builder claims.

## 6. FILE / SYMBOL EVIDENCE

### `data/palette/scrubbots_palette_v2.json`

Independent semantic equality check against pinned main-game source: **exact match**.

Result: **PASS**

### `contracts/palette.py`

Positive findings:

- strict C01..C16 ordered validation;
- exact schema/version/owner lock validation;
- production color-band metadata validation;
- duplicate ID and RGB rejection;
- HEX/RGB consistency check;
- immutable `PaletteColor`, `BackgroundColor`, and `CanonicalPalette`;
- mapping proxies for lookup maps;
- explicit BG01 logical rejection;
- unknown RGB/HEX fail closed;
- ascending used-ID output;
- repository-path + installed-data fallback.

Result: **PASS**

### `contracts/difficulty.py`

Positive findings:

- exact four-value enum;
- strict parsing;
- bool excluded from integer dimension acceptance;
- independent axis validation;
- first-class rectangular support;
- stable domain-separated width/height selection;
- no `random` usage;
- no M02 RNG abstraction leakage.

Result: **PASS**

### `contracts/color_usage.py`

Positive findings:

- actual logical-cell distinct IDs determine used palette;
- malformed/BG01/off-palette values rejected;
- explicit subset duplicates rejected;
- explicit subset legality checked against difficulty;
- stable subset size/member selection;
- ascending canonical return order.

Result: **PASS**

### `contracts/_stable_select.py`

Narrow M01-only helper is clearly documented as not M02 RNG.

Uses SHA-256 and explicit domain separation.

Result: **PASS**

## 7. FOCUSED TEST EVIDENCE

Independent audit source inspection confirmed focused tests cover:

Palette:
- all exact 16 values;
- unknown/malformed HEX;
- malformed/off-palette RGB;
- BG01;
- missing color;
- duplicate ID;
- duplicate RGB;
- C17;
- palette immutability.

Difficulty:
- min/max axis combinations;
- 19/60;
- cross-band invalid rectangles;
- legacy/alias difficulty names;
- deterministic seeded selection;
- rectangular occurrence;
- explicit/partial resolution.

Color usage:
- min/max used-color bands;
- below/above bands;
- duplicate logical cells;
- BG01/off-palette cells;
- explicit subset sorting/validation;
- duplicate/wrong-size/off-palette subset;
- deterministic subset variation.

Integration:
- all four production difficulties;
- fresh-process deterministic repeat;
- no generator/network dependency.

Result: **PASS**

## 8. REGRESSION EVIDENCE

M00 architecture remains intact:

- zero runtime dependencies;
- offline runtime boundary retained;
- no networking imports in M01 contracts;
- no main ScrubBots runtime dependency;
- no third-party source/art copied;
- no generator-family implementation.

Builder reports full suite `60 PASS`; no source evidence contradicts this.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no network dependency;
- no HTTP client;
- no telemetry;
- no global randomness;
- no runtime main-game repo access;
- vendored data is local/read-only contract source;
- fail-closed palette/difficulty/color validation;
- no arbitrary file-system traversal beyond fixed palette locations.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

M01 correctly stops before M02.

There is no:

- `GenerationRequest`;
- project RNG abstraction;
- generator interface;
- generation result;
- output schema;
- CLI;
- rendering/export implementation.

M01-only stable selection helper is intentionally narrow and replaceable.

Result: **PASS**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- builder log was created before first product edit;
- previous process finding F-PAG-M00-C003-PROC-001 is corrected;
- task/H!veAI/audit acceptance files were not modified by Codex;
- failed tests/commands were preserved in the log;
- final implementation and publication SHAs were recorded.

### Process-design finding: self-referential final log SHA

The C001 prompt required the builder log itself to contain its own final completion commit SHA.

That requirement is not logically stable:

1. writing SHA A into the log changes the file;
2. committing that change creates SHA B;
3. writing SHA B creates SHA C;
4. the process repeats.

Codex therefore produced:

- `9ccc4e7d...` as a log commit;
- then `41601910...` to write `9ccc4e7d...` into the log.

The final repository HEAD is `41601910...`, which by construction cannot be written inside the same immutable terminal log without creating another SHA.

Finding:

**F-PAG-M01-C001-PROC-001 — NOTE — terminal log self-SHA requirement is self-referential.**

Disposition:

- not a builder defect;
- not an M01 acceptance defect;
- future prompts must require:
  - implementation commit SHA(s) in builder log;
  - push result and equality at a publication checkpoint;
  - terminal repository HEAD to be captured by Git/H!veAI STATE/EVENTS and independent audit, not by forcing the log to contain its own final SHA.

## 12. FINAL REPOSITORY STATE

Audited current GitHub HEAD:

`41601910c133f42753272877ad648db098ff7306`

No unauthorized product scope found.

M01 product implementation commit:

`113e1401eba821460b9887ef84a14e2fb7c67f7c`

Result: **PASS**

## 13. OPEN CROSS-MILESTONE FINDINGS

No technical M01 finding remains open.

Carried process rule for M02+:

- builder log must exist before source edits;
- builder log must record implementation commit(s), push results, and observed equality checkpoints;
- terminal repository HEAD is independently recorded by ChatGPT/H!veAI after audit;
- do not require a log file to contain its own final commit SHA.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

None.

### MINOR

None.

### NOTE

- F-PAG-M01-C001-PROC-001 — self-referential terminal log SHA requirement.
- Exact 60-test command was not independently rerun because the audit execution container has no outbound GitHub DNS/network access; direct source inspection and independent property verification were completed instead.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking:

- M02 should centralize deterministic RNG semantics rather than expand M01 `_stable_select.py`;
- palette data may eventually move to package resources in a later packaging-focused milestone if desirable, but current installed data-files layout is valid and independently checked;
- explicit typed contract-result objects may become useful in M02, but M01 should remain simple.

## 16. UNVERIFIED ITEMS

Only the exact builder-reported Windows full-suite command was not independently rerun.

No canonical contract value, deterministic property, file scope, or architecture invariant remains unverified.

## 17. REGRESSION RISK

**LOW**

The contract layer is small, immutable, deterministic, dependency-free, and heavily validated.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct GitHub source inspection;
- exact pinned/current palette comparison;
- main-game HEAD verification;
- commit/diff scope inspection;
- independent 10,000-seed deterministic stress checks;
- independent setuptools data-files packaging probe;
- test-source inspection;
- no contradictory repository evidence.

## 19. FINAL VERDICT

**PASS**

`PAG-M01-C001` is accepted.

`PAG-M01 — Canonical SCRUBBOTS Contracts` is **PASS / CLOSED**.

All M01 task IDs `PAG-0101..PAG-0133` are validated complete.

PAG-M02 is authorized to begin.

## 20. REQUIRED REMEDIATION

None for M01.

The process-design NOTE is carried into future prompt governance and does not require a remediation cycle.
