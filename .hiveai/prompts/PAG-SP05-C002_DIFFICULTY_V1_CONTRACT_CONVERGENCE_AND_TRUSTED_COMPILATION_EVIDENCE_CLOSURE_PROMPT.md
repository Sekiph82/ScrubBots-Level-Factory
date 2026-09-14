# PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any implementation edit:

1. root `TASKS.md` — the current canonical SCRUBBOTS Content Production Platform tracker;
2. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md` — current LEVEL_ART normalization authority;
3. `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md` — current Content Platform contract precedence;
4. main-game owner authority, read-only: `https://github.com/Sekiph82/Scrubbots/blob/main/coordination/OWNER_DIFFICULTY_PROGRESSION_DECISION_V01.md`;
5. `.hiveai/audits/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_STRICT_AUDIT.md`;
6. C001 implementation: `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`;
7. C001 tests: `tests/unit/test_sp05_level_art.py`;
8. current canonical palette and legacy compatibility contracts under `src/scrubbots_pixel_factory/contracts/`;
9. accepted SP03/C005/C006 raw-artifact, PNG-decoder and provenance source/tests;
10. `docs/CONTENT_PLATFORM_ARCHITECTURE_V01.md`, `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** use legacy hidden `.hiveai` tracker/control-plane files such as `.hiveai/CYCLE_INDEX.md`, `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/STATE.json` or `.hiveai/HANDOFF.md` as current authority.

Do not edit root `TASKS.md`.

Do not modify `Sekiph82/Scrubbots`; that repository is read-only authority for this cycle.

Create the matching builder log **before any C002 source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_CODEX_LOG.md`

## Mission

Retain the useful SP05-C001 hard-cell compiler work while converging it to current owner-locked Difficulty V1 and closing the trusted compilation-evidence gap.

Canonical current production art flow:

```text
SEMANTIC RAW IMAGE
        ↓
CELL_MAJORITY_V1
        ↓
PALETTE_SNAP_V1
        ↓
ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
        ↓
C01..C16 ONLY
        ↓
PRODUCTION DIMENSION ENVELOPE: width 20..59, height 20..59, rectangles legal
        ↓
PRODUCTION USED-COLOR ENVELOPE: 3..12, independent of difficulty class/lane
        ↓
TRUSTED IMMUTABLE LOGICAL ART + EXACT PROVENANCE
```

Difficulty lane/class metadata must not determine board dimensions or distinct-color legality in the canonical production semantic compiler.

Do not redesign CELL_MAJORITY. Do not redesign C01..C16 palette snap. Do not call Magnific or PixelLab. Spend zero credits.

Do not begin M08/LevelData integration, solver work, Challenge Score implementation, SP06 recognizability scoring, Studio feature implementation, publishing work, weekly batching or M11.

---

# 1. Preserve C001 hard-cell behavior exactly

The following C001 behavior is accepted technical evidence and must remain byte-for-byte/deterministically equivalent for identical decoded input and target dimensions:

- `CELL_MAJORITY_V1` half-open footprint math;
- highest source RGBA frequency wins;
- exact ties resolve by lexicographically ascending RGBA bytes;
- no averaging/interpolation/antialiasing;
- source smaller than target fails closed in V1;
- non-opaque winning cells fail closed;
- `PALETTE_SNAP_V1` maps only to C01..C16;
- squared integer RGB-distance metric;
- palette-distance ties resolve by canonical palette index ascending;
- BG01 never participates in logical color selection.

Add regression tests proving C002 does not alter these algorithms.

---

# 2. Separate current production legality from legacy compatibility legality

Do **not** destructively rewrite historical helpers that older PAG reproduction/generator tests still depend on unless a separate migration is explicitly required.

Legacy helpers such as class-specific `validate_dimensions(difficulty, ...)` and class-specific `validate_used_color_count(difficulty, ...)` may remain available for historical compatibility.

Add or reuse **explicit current-production** contracts for the new semantic production compiler.

Required current production dimension contract:

- width integer 20..59 inclusive;
- height integer 20..59 inclusive;
- validate each axis independently;
- rectangular boards legal;
- no EASY/MEDIUM/HARD/VERY_HARD key is used to decide dimension legality.

Suggested discoverable helpers, names may follow existing repository conventions:

- `validate_production_width(width)`;
- `validate_production_height(height)`;
- `validate_production_dimensions(width, height)`.

Do not duplicate the C01..C16 palette table.

Required tests include:

- 20x20 legal;
- 20x59 legal;
- 59x20 legal;
- 59x59 legal;
- width/height 19 rejected;
- width/height 60 rejected;
- 24x24 is legal regardless of lane metadata;
- 38x38 is legal regardless of lane metadata.

---

# 3. Replace class-specific color budget with current production color envelope

Current production logical art may use **3..12 distinct C01..C16 colors**, independent of EASY/MEDIUM/HARD/VERY_HARD.

Introduce/version a current policy identity such as:

`PRODUCTION_COLOR_ENVELOPE_V1`

Do not continue presenting `DIFFICULTY_COLOR_BUDGET_V1` as the canonical current production legality rule. Historical C001 identity may remain in historical evidence where necessary, but newly compiled trusted production artifacts must unambiguously identify the current policy.

Required behavior after PALETTE_SNAP_V1:

### 3.1 Already legal: 3..12 colors

If actual used count is 3 through 12 inclusive:

- preserve snapped logical cells exactly;
- no recoloring merely because lane/class metadata is EASY/MEDIUM/HARD/VERY_HARD;
- no attempt to hit a class-specific preferred count.

### 3.2 Too few: <3

If fewer than 3 canonical colors are used:

- fail closed with an explicit typed reason such as `INSUFFICIENT_USED_COLORS`;
- do not fabricate accents or split regions;
- do not inject unused C-IDs.

### 3.3 Too many: >12

Retain the exact C001 frequency-weighted exhaustive subset optimization, but apply it only to reduce above 12 to **exactly 12**.

For currently used set `U` and cell frequency `f(s)`:

- enumerate all retained subsets of size 12 from U;
- cost of source used color `s` to retained subset R is the minimum squared canonical RGB distance to any member of R;
- total subset cost is `SUM f(s) * nearest_distance(s,R)`;
- choose minimum total weighted cost;
- tie by lexicographically ascending canonical palette-index tuple;
- retained cells stay unchanged;
- each removed color maps to nearest retained color by squared canonical RGB distance, tie by canonical index.

Do not introduce a C-ID that was not already used in the snapped grid during >12 reduction.

Final used count must be 12.

Record original used IDs/count, retained IDs, weighted objective cost, final used IDs/count and current policy version in trusted evidence.

---

# 4. Lane/class metadata must be non-transformative

EASY/MEDIUM/HARD/VERY_HARD may remain in the LEVEL_ART request/artifact only as campaign/difficulty-lane metadata if useful for lineage.

If retained:

- it must not select dimension ranges;
- it must not select color-count ranges;
- changing only lane/class metadata for the same raw artifact and same target dimensions must produce identical CELL_MAJORITY bytes, snapped grid, production-envelope reduction and final logical cells;
- artifact identity may record lane metadata if the product contract wants lineage, but transformation-stage digests/cells must remain identical.

If the cleanest current contract is to remove lane metadata from the hard-cell compiler request entirely and leave it to downstream Difficulty Intelligence, do so only if public API migration is explicit, backward-compatible where necessary, and tests prove no ambiguity.

Do not implement Challenge Score/Session Load/Frustration in C002.

---

# 5. Close trusted report and artifact construction

C001's exported `SemanticLevelArtArtifact.from_compilation(...)` can accept caller-supplied final cells, majority hash, snapped hash and a caller-constructed report. This is not sufficient for trusted evidence.

C002 must make the **canonical compiler itself** the trusted producer.

Required trust properties:

- direct construction of trusted report fails;
- `dataclasses.replace()` on trusted report cannot mint another valid trusted report;
- direct construction of trusted artifact fails;
- `dataclasses.replace()` on trusted artifact cannot mint another valid trusted artifact;
- no public checked-constructor accepts arbitrary caller-supplied stage hashes/report facts and then seals them without recomputing or verifying the exact stages;
- raw SHA in trusted report must exactly equal the source raw artifact SHA;
- report source raw-artifact digest must equal the exact source artifact digest;
- request digest/policy/target dimensions must bind exactly;
- majority digest must come from actual `CELL_MAJORITY_V1` output;
- snapped-grid digest and used IDs must come from actual PALETTE_SNAP_V1 output;
- production-envelope original used IDs/count must equal actual snapped grid;
- retained subset/cost/final used IDs/count must equal actual envelope computation;
- final logical-grid digest must equal exact row-major final cells;
- source provider/request/model provenance must remain bound through the existing typed source-provenance snapshot.

Recommended implementation pattern:

- use private construction token + fingerprint for report and artifact;
- construct the trusted report internally from actual typed/stage values in `compile_semantic_level_art()` or a private internal factory;
- construct artifact internally from raw + request + trusted report/stage values;
- if a public `from_compilation` method remains for compatibility, it must not be capable of minting trust from caller assertions. It may either fail/redirect to full recomputation or require sealed typed evidence that the caller cannot mint directly.

Do not merely add one `report.raw_sha256` equality check. Close the whole boundary.

---

# 6. Version/schema clarity

C001 artifact semantics encoded legacy class-specific legality. C002 current-production semantics are materially different.

Do not allow identical schema/policy identifiers to mean both old and new rules.

Choose a clear, versioned migration strategy consistent with repository conventions, for example:

- bump the LEVEL_ART request/report/artifact schema version; and/or
- replace the old difficulty-budget policy identity with `PRODUCTION_COLOR_ENVELOPE_V1`;
- retain explicit historical identities only for reproduction evidence.

New canonical artifacts must make it impossible for a reader to mistake current Difficulty V1 production-envelope legality for old class-band legality.

---

# 7. Required focused tests

Add/adjust focused tests to prove at minimum:

### Hard-cell and palette regression

1. C001 CELL_MAJORITY known fixtures produce exactly the same majority bytes under C002;
2. non-divisible footprint and RGBA tie behavior unchanged;
3. exact palette matches and nearest/tie palette snap unchanged;
4. source<target and non-opaque winner still fail closed;
5. no AREA_AVERAGE behavior appears.

### Current production dimensions

6. 20x20, 20x59, 59x20, 59x59 legal;
7. 19 or 60 on either axis fail;
8. VERY_HARD metadata + 24x24 legal;
9. EASY metadata + 38x38 legal;
10. rectangle legality independent of class/lane.

### Current production used-color envelope

11. 3 colors preserved unchanged;
12. 5 colors preserved unchanged;
13. 8 colors preserved unchanged;
14. 12 colors preserved unchanged;
15. each of those counts remains legal under at least two different lane labels, including a cross-class case such as EASY 8-color and VERY_HARD 5-color;
16. fewer than 3 fails without fabricated colors;
17. 13 through 16 used colors reduce deterministically to exactly 12;
18. exact weighted-subset expected fixture passes;
19. equal-cost subset tie resolves by canonical index tuple;
20. explicit removed-color fixture proves every removed C-ID maps to the nearest retained C-ID with canonical-index tie-break;
21. no new snapped-set-external C-ID appears during >12 reduction.

### Lane non-transformative behavior

22. same raw + same target + EASY vs VERY_HARD metadata yields identical majority digest;
23. identical snapped-grid digest;
24. identical final logical cells/grid digest;
25. only lineage identity fields may differ if lane metadata is intentionally part of artifact identity.

### Trusted evidence

26. direct trusted-report construction fails;
27. `replace(report, raw_sha256=...)` fails/trips integrity;
28. direct trusted-artifact construction fails;
29. `replace(artifact, ...)` fails/trips integrity;
30. forged report raw SHA cannot be sealed;
31. forged majority digest cannot be sealed;
32. forged snapped digest/used set cannot be sealed;
33. forged retained subset/weighted cost cannot be sealed;
34. forged final-grid digest cannot be sealed;
35. any retained public checked constructor cannot mint arbitrary trusted stage evidence;
36. raw-byte-distinct but decoded-pixel-equivalent sources preserve equal logical cells while retaining distinct exact source provenance/artifact identity.

### Compatibility/regression

37. legacy compatibility dimension/color helpers still behave as before for historical tests;
38. accepted SP03 ASSET_ART behavior remains unchanged;
39. C005/C006 PNG ancillary/IDAT behavior remains unchanged;
40. no provider call is required.

Use synthetic images only. Do not commit the owner's private Magnific PNG.

---

# 8. Verification

Run and log at minimum:

1. updated SP05-C001/C002 focused tests;
2. canonical palette and legacy compatibility contract tests;
3. SP03 normalization tests;
4. SP04 C005/C006 PNG tests;
5. SP04 qualification tests;
6. combined semantic SP01-SP05 focused regression;
7. any current Content Platform core tests affected by the concurrent platform migration;
8. full repository Python test suite;
9. `python -m compileall -q src tests` or equivalent;
10. package import smoke;
11. current CLI smoke;
12. `git diff --check`;
13. scoped offline/network/credential scan over changed source/test files.

Builder results are implementation evidence, never ChatGPT acceptance.

If concurrent `main` changes arrive while working, fetch/rebase or fast-forward safely before final publication and verify they do not invalidate this prompt's current authorities. Never force-push.

---

# 9. Scope discipline

Allowed product work:

- current production dimension-envelope contract needed by semantic LEVEL_ART compiler;
- current production used-color-envelope contract;
- SP05 LEVEL_ART request/report/artifact/compiler convergence;
- trust/sealing remediation;
- public exports directly required for these current contracts;
- focused tests.

Explicitly out of scope:

- provider execution or model qualification;
- C01..C16 value changes;
- CELL_MAJORITY redesign;
- PALETTE_SNAP redesign;
- dithering;
- transparency compositing;
- Challenge Score / Session Load / Frustration implementation;
- gameplay solver;
- M08/LevelData bridge;
- SP06 semantic recognizability implementation;
- Studio UI feature implementation;
- publishing/control-plane implementation;
- weekly batch work;
- main-game source changes;
- root `TASKS.md` edits by builder.

---

# 10. Builder log and publication truth

Matching H1 exactly:

`# PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start HEAD/origin/main and divergence;
- working-tree dirt;
- all current authorities read;
- concurrent-main changes encountered, if any;
- exact changed files;
- implementation summary;
- focused/full test commands and exact outcomes;
- proof no provider call or credit spend;
- implementation commit SHA(s);
- push result;
- truthful terminal repository state.

Because a commit cannot contain its own final SHA without self-reference, do not create endless log-only commits. After the final publication commit, fetch origin and report terminal `HEAD`, `origin/main`, and divergence in the handoff. Do not fabricate a checkpoint.

Stop after push and wait for ChatGPT strict audit.

---

# Acceptance criteria

C002 is eligible for ChatGPT PASS only if all are true:

- [ ] CELL_MAJORITY_V1 is unchanged;
- [ ] PALETTE_SNAP_V1 is unchanged;
- [ ] current production width/height legality is independent 20..59;
- [ ] rectangular boards remain legal;
- [ ] difficulty lane/class no longer controls dimension legality;
- [ ] current production used-color legality is global 3..12 C01..C16;
- [ ] 3..12 snapped grids remain unchanged regardless of lane/class;
- [ ] <3 fails closed without fabrication;
- [ ] >12 reduces deterministically to exactly 12 with retained C001 weighted optimizer;
- [ ] removed colors map only to nearest retained colors;
- [ ] no new C-ID is introduced by envelope reduction;
- [ ] current policy/schema identities cannot be confused with legacy C001 class-band semantics;
- [ ] trusted report construction cannot be forged directly or through `replace()`;
- [ ] trusted artifact construction cannot be forged directly, through `replace()`, or through a public assertion-based checked constructor;
- [ ] raw/intermediate/budget/final provenance is recomputed or exactly sealed from actual stages;
- [ ] legacy compatibility validators remain available for historical reproduction/tests;
- [ ] accepted ASSET_ART and strict PNG behavior remains green;
- [ ] no provider calls / zero credits;
- [ ] builder does not edit root TASKS.md;
- [ ] no main-game writes occur;
- [ ] focused and full regressions are green;
- [ ] builder publication evidence is truthful.
