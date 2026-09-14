# PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget
Document role: CODEX BUILDER PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any implementation edit:

1. root `TASKS.md` — the ONLY current project-status tracker;
2. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V01.md` — owner-locked LEVEL_ART normalization workflow;
3. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md` — semantic-pivot architecture and LEVEL_ART/ASSET_ART separation;
4. `.hiveai/audits/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_STRICT_AUDIT.md` — accepted live PNG compatibility closure;
5. `review/sp04/SP04_Q02_Q03_MAGNIFIC_OFFICIAL_LOCAL_NORMALIZATION_2026-09-14.md` — live Magnific evidence and rejected AREA_AVERAGE LEVEL_ART behavior;
6. `src/scrubbots_pixel_factory/contracts/palette.py`;
7. `src/scrubbots_pixel_factory/contracts/color_usage.py`;
8. `src/scrubbots_pixel_factory/contracts/difficulty.py`;
9. current semantic contracts and semantic normalization source/tests;
10. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** read or use legacy hidden `.hiveai` tracker/control-plane files such as `.hiveai/CYCLE_INDEX.md`, `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, or similar files to reconstruct current state.

Do not edit root `TASKS.md`.

Create the matching builder log **before any SP05-C001 source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_CODEX_LOG.md`

## Mission

Implement the owner-locked LEVEL_ART semantic compiler through the canonical logical-cell legality boundary:

```text
SEMANTIC RAW IMAGE
        ↓
CELL_MAJORITY
        ↓
DETERMINISTIC PALETTE SNAP
        ↓
ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
        ↓
C01..C16 ONLY
        ↓
DIFFICULTY USED-COLOR BUDGET
        ↓
IMMUTABLE LEVEL_ART SEMANTIC ARTIFACT + PROVENANCE
```

This is an implementation task, not a new design vote. Do **not** reopen AREA_AVERAGE vs NEAREST vs CELL_MAJORITY. The owner selected CELL_MAJORITY for LEVEL_ART.

`AREA_AVERAGE_V1` remains historical/ASSET_ART evidence and must not be used by the new LEVEL_ART compiler.

Do not call Magnific or PixelLab. Spend zero provider credits.

Do not begin SP06 semantic scoring, Studio UI, weekly batch work, M11, final gameplay solver integration, or unrelated provider qualification.

---

# 1. Preserve existing contracts; do not duplicate authorities

Reuse the existing canonical contracts directly:

- `CANONICAL_PALETTE` / `CanonicalPalette` from `contracts/palette.py`;
- C01..C16 ordering and RGB values from the owner-locked palette data;
- BG01 remains presentation-only and must never appear in LEVEL_ART logical cells;
- `Difficulty`, `parse_difficulty`, and `validate_dimensions` from `contracts/difficulty.py`;
- `actual_used_palette_ids`, `count_used_colors`, and `validate_used_color_count` from `contracts/color_usage.py` where applicable.

Do not create a second palette table, second difficulty enum, second dimension-band table, or conflicting color-band table inside semantic code.

Owner-locked legality remains:

- EASY: width/height independently 20..29; 3..5 used colors;
- MEDIUM: 30..39; 6..7;
- HARD: 40..49; 8..9;
- VERY_HARD: 50..59; 10..12;
- rectangles allowed;
- one logical output pixel = one gameplay cell;
- only C01..C16 may exist in logical cells;
- BG01 is forbidden in logical cells.

---

# 2. Add a separate typed LEVEL_ART normalization/compile boundary

Do not weaken or repurpose the accepted ASSET_ART `SemanticNormalizationRequest` / `SemanticNormalizedArtifact` contract in a way that changes existing SP03 behavior.

Introduce a separate typed LEVEL_ART request/result boundary under the semantic normalization/integration layer. Naming may follow repository conventions, but it must be explicit and discoverable, for example:

- `SemanticLevelArtRequest`;
- `SemanticLevelArtArtifact`;
- `SemanticLevelArtReport`;
- `compile_semantic_level_art(...)`.

The exact symbol names may differ only if an existing repository naming convention clearly provides better names.

The LEVEL_ART request must include at least:

- exact source `SemanticRawArtifact` digest binding;
- difficulty;
- target width;
- target height;
- versioned CELL_MAJORITY policy id;
- versioned palette-snap policy id;
- versioned difficulty-budget policy id.

The request must validate difficulty and both target axes using existing difficulty contracts. No 24x24 special case may be hardcoded; 24x24 is merely one legal EASY example.

The resulting artifact must contain at least:

- immutable logical cell grid in deterministic row-major order;
- target width/height;
- difficulty;
- actual used C-IDs;
- source raw artifact digest and raw SHA provenance;
- source provider/request/model provenance already available from the raw artifact;
- policy/version identities;
- CELL_MAJORITY intermediate digest or equivalent deterministic binding;
- final logical-grid digest;
- report/evidence sufficient to reproduce and audit every transformation.

The artifact must be deeply immutable and fail closed on coordinated provenance tampering using the accepted SP03 construction-seal pattern or an equally strong existing project pattern.

Do not convert it into M08/LevelData in C001. C001 ends at a canonical immutable semantic LEVEL_ART logical artifact. Existing M08/LevelData/export integration belongs to the next bounded SP05 cycle after this compiler passes strict audit.

---

# 3. Implement CELL_MAJORITY_V1 exactly

Define and version a deterministic `CELL_MAJORITY_V1` reduction.

### 3.1 Exact-size source

If decoded source dimensions equal target dimensions:

- each source pixel corresponds to exactly one target logical cell;
- no resize/interpolation/averaging is performed;
- continue through palette snap and color-budget stages.

### 3.2 High-resolution source reduction

For source width `SW`, source height `SH`, target width `TW`, target height `TH`, require for V1:

- `SW >= TW`;
- `SH >= TH`.

If either source axis is smaller than the requested target axis, fail closed with a typed LEVEL_ART compilation error. Do not invent hidden upsampling in C001.

For target cell `(tx, ty)`, use the deterministic half-open source footprint:

- `x0 = floor(tx * SW / TW)`;
- `x1 = floor((tx + 1) * SW / TW)`;
- `y0 = floor(ty * SH / TH)`;
- `y1 = floor((ty + 1) * SH / TH)`;
- source pixels are all `(x, y)` where `x0 <= x < x1` and `y0 <= y < y1`.

Each footprint must be non-empty under the V1 source>=target requirement.

Count exact decoded RGBA values in that footprint. Select exactly one winner:

1. highest pixel count wins;
2. ties are resolved by lexicographic RGBA byte tuple ascending.

Emit exactly one RGBA winner per logical target cell.

CELL_MAJORITY_V1 must never:

- average channels;
- interpolate;
- antialias;
- synthesize intermediate colors;
- use PIL/OpenCV resampling as a hidden substitute.

Record a deterministic digest of the row-major majority RGBA grid before palette snap.

### 3.3 Alpha policy for LEVEL_ART V1

LEVEL_ART logical cells have no transparent logical color.

For C001:

- every selected CELL_MAJORITY winner must have alpha `255`;
- if any winning majority cell is non-opaque, fail closed with a typed error;
- do not silently composite transparency onto white, BG01, black, or any palette color;
- do not reinterpret transparent cells as BG01.

Future explicit transparency/background policy, if needed, requires a separate owner-visible decision.

---

# 4. Implement deterministic C01..C16 PALETTE_SNAP_V1

For every CELL_MAJORITY winner RGB value, snap to exactly one C01..C16 canonical palette color.

Distance metric for V1:

```text
d2 = (R - Rc)^2 + (G - Gc)^2 + (B - Bc)^2
```

where `(Rc, Gc, Bc)` is the canonical RGB for a C-ID.

Selection rule:

1. smallest integer squared RGB distance wins;
2. exact distance ties are resolved by canonical palette index ascending, therefore C01 before C02 ... before C16.

Requirements:

- output is C-ID strings, not arbitrary RGB values;
- BG01 must never participate in nearest-color selection;
- no provider color survives as a LEVEL_ART logical color outside C01..C16;
- same input bytes/request must always produce the same snapped grid;
- record pre-budget snapped-grid digest and exact used C-IDs.

Do not add dithering in C001.

---

# 5. Implement DIFFICULTY_COLOR_BUDGET_V1

After palette snap, compute actual used C-IDs using the existing color-usage contract.

Let difficulty band be `[MIN, MAX]`.

### 5.1 Already legal

If actual used count is within `[MIN, MAX]`:

- preserve the snapped grid exactly;
- do not add or remove colors merely to hit a preferred count.

### 5.2 Too few colors

If used count is below `MIN`:

- fail closed with a typed `INSUFFICIENT_USED_COLORS` or equivalent explicit reason;
- do not fabricate accents, split regions, recolor arbitrary cells, or inject unused palette colors merely to satisfy the minimum.

This behavior is owner-locked.

### 5.3 Too many colors

If used count is above `MAX`, deterministically reduce to exactly `MAX` retained C-IDs using the following V1 weighted palette-subset optimization.

Definitions:

- each currently used C-ID has weight equal to its logical-cell frequency in the snapped grid;
- candidate retained subsets are all combinations of exactly `MAX` IDs drawn from the currently used IDs only;
- for each source used color `s`, remap cost to a retained color `r` is squared canonical RGB distance using the same integer `d2` metric as palette snap;
- subset total cost is:

```text
SUM_over_used_s( frequency(s) * MIN_over_retained_r( d2(s, r) ) )
```

Select the retained subset with:

1. minimum total weighted cost;
2. ties resolved by the lexicographically ascending tuple of canonical palette indexes.

Then remap every cell whose snapped C-ID is not retained to its nearest retained C-ID using:

1. minimum squared canonical RGB distance;
2. tie by canonical palette index ascending.

Properties:

- at most 16 source C-IDs exist, so exact combination search is intentionally bounded and acceptable;
- no random seed is used;
- no new C-ID outside the already used snapped set may be introduced by budget reduction;
- final used count must be exactly `MAX` unless two retained IDs somehow collapse, which must be impossible because retained IDs are distinct and retained cells themselves remain unchanged;
- validate the final grid using existing `validate_used_color_count`;
- record retained subset, original used IDs/count, final used IDs/count, weighted objective cost and budget-policy version in the report.

Do not use existing `select_palette_subset()` for this semantic reduction because that helper selects a seed-based arbitrary legal subset and does not preserve semantic source color fidelity. Continue to use existing contract validators for legality.

---

# 6. Preserve source provenance and deterministic identity

The LEVEL_ART compiler must consume a typed `SemanticRawArtifact` and remain bound to its exact immutable bytes/provenance.

Required invariants:

- input raw SHA must continue to hash exact original provider/local bytes;
- decoder must use the accepted C006 PNG behavior;
- source dimensions in the raw artifact must match decoded dimensions;
- LEVEL_ART request must bind the exact raw artifact digest;
- report/result must bind request digest, raw artifact digest/SHA, decoded dimensions, majority-grid digest, pre-budget snapped-grid digest, final logical-grid digest, difficulty, target dimensions and policy versions;
- normal dataclass construction/`replace()` must not permit a caller to mint a false trusted artifact by resetting a seal/fingerprint;
- cost/timestamps/audit metadata, if any, must remain outside deterministic artifact identity.

No provider call is needed or authorized.

---

# 7. Logical-grid representation

Use a single unambiguous row-major representation.

At minimum:

- exactly `target_width * target_height` logical cells;
- each cell is one canonical C-ID string;
- deterministic accessor/row conversion is allowed;
- dimensional mismatch fails closed;
- `actual_used_palette_ids()` on the final cells must match the artifact/report used-color declaration;
- BG01 and off-palette values fail closed.

Do not create per-pixel blended RGB output as the canonical LEVEL_ART artifact. RGB preview/export can be derived later from C-IDs.

---

# 8. Required tests

Add focused SP05-C001 tests that prove at least all of the following.

### CELL_MAJORITY

1. exact-size input performs no averaging and preserves one source pixel per target cell before palette snap;
2. 4x4 -> 2x2 synthetic footprints choose the true local majority;
3. non-divisible rectangular reduction, e.g. 7x5 -> legal synthetic target footprint math in an isolated helper test, is deterministic;
4. exact majority ties use lexicographic RGBA tie-break;
5. source smaller than target on either axis fails closed;
6. non-opaque winning cell fails closed;
7. no AREA_AVERAGE/intermediate-color behavior appears in LEVEL_ART compiler.

### Palette snap

8. every final logical cell is C01..C16;
9. BG01 cannot appear;
10. exact RGB match maps to its exact C-ID;
11. nearest-color selection uses integer squared RGB distance;
12. equal-distance tie resolves by lower canonical palette index;
13. arbitrary source colors cannot survive into logical output.

### Difficulty budget

14. in-band used count is preserved unchanged;
15. below-minimum count fails closed and does not fabricate colors;
16. above-maximum EASY reduces deterministically to exactly 5;
17. above-maximum MEDIUM reduces to exactly 7;
18. above-maximum HARD reduces to exactly 9;
19. above-maximum VERY_HARD reduces to exactly 12;
20. weighted subset optimization has a small fixture with a hand-computable expected retained subset;
21. tie between equal-cost subsets resolves by canonical index tuple;
22. removed colors map only to nearest retained colors;
23. final `validate_used_color_count()` passes.

### Difficulty/dimensions

24. legal rectangles work, including 20x29 EASY and one legal rectangle for each other difficulty;
25. out-of-band width/height fails closed through existing difficulty contracts;
26. no hardcoded 24x24 assumption exists.

### Provenance / determinism

27. same raw artifact + same request yields byte-for-byte / digest-identical LEVEL_ART artifact;
28. raw byte change changes source provenance/artifact identity even if decoded pixels are equivalent;
29. request target/difficulty/policy change changes deterministic identity;
30. direct construction or `dataclasses.replace()` cannot mint trusted mismatched provenance;
31. existing ASSET_ART normalization behavior remains unchanged.

Use synthetic test images. Do not commit the owner's private Magnific PNG.

---

# 9. Regression verification

Run and log at minimum:

1. new SP05-C001 focused tests;
2. SP03 normalization tests;
3. SP04 C005/C006 PNG compatibility tests;
4. SP04 qualification tests;
5. existing palette/color-usage/difficulty contract tests;
6. combined SP01-SP05 semantic focused tests;
7. full repository test suite;
8. `python -m compileall -q src tests` or equivalent;
9. package import smoke;
10. CLI smoke;
11. `git diff --check`;
12. scoped offline/network/credential scan over changed product/test files.

Do not claim independent ChatGPT audit from builder tests.

---

# 10. Scope discipline

Allowed product work:

- semantic LEVEL_ART request/report/artifact/compiler;
- deterministic CELL_MAJORITY_V1;
- deterministic PALETTE_SNAP_V1;
- deterministic DIFFICULTY_COLOR_BUDGET_V1;
- exports needed to make the new API discoverable.

Allowed tests:

- focused tests necessary to prove the above and preserve accepted contracts.

Explicitly out of scope:

- Magnific/PixelLab execution;
- provider/model selection changes;
- ASSET_ART policy redesign;
- M08/LevelData export integration;
- gameplay solver integration;
- semantic recognizability scoring/SP06;
- Studio UI;
- weekly batch pipeline;
- WFC/MASK/RULES/HYBRID redesign;
- changing C01..C16 values;
- changing difficulty dimension or used-color bands;
- dithering;
- transparency compositing;
- re-opening the CELL_MAJORITY owner decision.

---

# 11. Builder log and publication truth

Matching H1 exactly:

`# PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- starting HEAD and origin/main;
- starting divergence and working-tree dirt;
- exact authorities read;
- exact files changed;
- implementation summary;
- all focused/full test commands and results;
- proof no provider call/credit spend occurred;
- implementation commit SHA(s);
- push result;
- truthful terminal repository state.

Because a commit cannot contain its own final SHA without self-reference, do not create an endless chain of log-only commits trying to encode the terminal SHA inside itself. After the final publication commit, run `git fetch origin`, `git rev-parse HEAD`, `git rev-parse origin/main`, and `git rev-list --left-right --count HEAD...origin/main`; include the observed terminal values in the handoff response to ChatGPT. The committed log must state this limitation truthfully rather than fabricate a checkpoint.

Stop after push and wait for ChatGPT strict audit.

---

# Acceptance criteria

SP05-C001 is eligible for ChatGPT PASS only if all are true:

- [ ] owner-locked CELL_MAJORITY is implemented as the LEVEL_ART reduction policy;
- [ ] no averaging/interpolation/antialiasing occurs in the logical-cell reduction;
- [ ] exact-size and source>=target reductions are deterministic;
- [ ] source<target fails closed in V1;
- [ ] non-opaque majority winners fail closed;
- [ ] every logical cell is exactly one C01..C16 ID;
- [ ] BG01/off-palette cells are impossible in trusted artifacts;
- [ ] palette snap uses the specified deterministic squared-RGB metric/tie-break;
- [ ] in-band color counts remain unchanged;
- [ ] below-minimum color count fails closed without fabricated colors;
- [ ] above-maximum color count reduces through exact deterministic weighted subset optimization;
- [ ] final grid passes existing difficulty used-color validation;
- [ ] existing dimension bands and rectangles are preserved;
- [ ] raw/request/policy/intermediate/final provenance is exact and immutable;
- [ ] accepted ASSET_ART/SP03 behavior is not weakened;
- [ ] no provider calls or credits occur;
- [ ] no M08/solver/SP06/UI expansion occurs;
- [ ] root `TASKS.md` is untouched by builder;
- [ ] focused and full regression tests are green;
- [ ] builder publication/handoff evidence is truthful.
