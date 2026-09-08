# PAG-M01-C001 — Canonical SCRUBBOTS Contracts

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical implementation repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_STRICT_AUDIT.md`

Pinned main-game contract source:
`Sekiph82/Scrubbots@b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`

Pinned canonical palette:
`https://github.com/Sekiph82/Scrubbots/blob/b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd/data/palettes/scrubbots_palette_v2.json`

Pinned owner-locked difficulty/board rules:
`https://github.com/Sekiph82/Scrubbots/blob/b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd/tasks.md`

## 1. Objective

Implement and prove **PAG-M01 — Canonical SCRUBBOTS Contracts** only.

M01 establishes local, deterministic, generator-independent contract code for:

- canonical C01..C16 logical palette;
- BG01 exclusion;
- EASY / MEDIUM / HARD / VERY_HARD difficulty identity;
- exact independent width/height bands;
- rectangular board legality;
- actual-used-color legality;
- deterministic legal dimension selection;
- deterministic legal palette-subset selection;
- explicit valid supplied palette subsets;
- fail-closed rejection of legacy/illegal assumptions.

Do not begin PAG-M02.

Do not create the M02 `GenerationRequest`, RNG abstraction, generator interfaces, result schema, CLI, PNG writer, WFC, MASK, RULES, HYBRID, Godot integration, or gameplay code.

## 2. Authority and read-only main-game rule

GitHub is the sole task/prompt/audit authority.

The implementation repository is:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

The main game repository is **read-only contract authority** for this cycle:

`https://github.com/Sekiph82/Scrubbots`

Do not commit, push, edit, or mutate the main ScrubBots repository.

Do not discover tasks by searching local folders.

If working on the owner's Windows machine, synchronize only the Level Factory mirror specified by repository governance using safe fetch + fast-forward.

## 3. Contract drift preflight

Before implementation, verify that the pinned source commit and files above are readable.

Also inspect the current main-game `main` HEAD.

If current main has changed the owner-locked palette, board bands, difficulty names, BG01 role, or color-count bands relative to the pinned source:

- STOP before implementing conflicting contract code;
- record the exact drift in the Codex log;
- do not silently choose one version.

If current main differs only in unrelated governance/control-plane history and the pinned contract data is unchanged, continue and record that verification.

## 4. Mandatory read order

Read completely before source changes:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. previous M00 C003 strict audit
9. `reference/audits/README.md`
10. `reference/audits/scrubbots/coordination/sessions/META-C005/CHATGPT_AUDIT_V01.md`
11. pinned main-game palette JSON
12. pinned main-game task sections covering locked difficulty/dimensions/palette/BG01/color bands
13. this prompt

## 5. Mandatory builder log

Create the matching Codex log **before the first product/source edit**:

`.hiveai/codex-logs/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_CODEX_LOG.md`

Exact H1:

`# PAG-M01-C001 — Canonical SCRUBBOTS Contracts`

Immediately below:

`Document role: CODEX BUILDER LOG`

This ordering is mandatory because the previous M00 audit carried process finding `F-PAG-M00-C003-PROC-001`.

The log must preserve, chronologically:

- start timestamp;
- GitHub authority URLs;
- pinned main-game contract commit;
- current main-game HEAD and drift check;
- Level Factory starting branch/HEAD/origin/status;
- safe synchronization evidence;
- all mandatory documents read;
- architecture decisions;
- exact files changed;
- every material command;
- failed tests/commands and corrections;
- focused contract tests;
- full regression test results;
- deterministic evidence;
- invalid-input evidence;
- no-main-game-runtime-dependency proof;
- final diff summary;
- implementation commit SHA(s);
- final log completion commit SHA;
- push results;
- final local HEAD;
- final `origin/main` HEAD;
- explicit equality/divergence statement.

The final evidence fields must actually be appended after the final source/log commits. Do not repeat M00 process finding `F-PAG-M00-C003-PROC-002`.

## 6. Builder-only boundary

Codex must not:

- perform or author an independent audit;
- declare M01 PASS/CLOSED;
- modify task checkbox/state in `tasks.md`;
- modify `.hiveai/HANDOFF.md`;
- modify `.hiveai/CYCLE_INDEX.md`;
- modify `.hiveai/STATE.json`;
- append acceptance events to `.hiveai/EVENTS.jsonl`;
- create or modify files under `.hiveai/audits/`;
- rewrite prior prompt/log/audit history.

ChatGPT owns acceptance and H!veAI tracker-state updates.

## 7. Canonical palette data — PAG-S01.1

Implement:

- PAG-0101 through PAG-0110.

### Required local machine-readable source

Create the standalone repository's local canonical palette source under:

`data/palette/scrubbots_palette_v2.json`

Use the pinned main-game palette as the data authority.

Do not invent or alter canonical values.

Required logical colors:

| ID | HEX | RGB |
| --- | --- | --- |
| C01 | #E94B4B | 233,75,75 |
| C02 | #F28C3C | 242,140,60 |
| C03 | #F2C94C | 242,201,76 |
| C04 | #55B85A | 85,184,90 |
| C05 | #63D6A3 | 99,214,163 |
| C06 | #42C7D9 | 66,199,217 |
| C07 | #3E7EDB | 62,126,219 |
| C08 | #3451A3 | 52,81,163 |
| C09 | #845EC2 | 132,94,194 |
| C10 | #E66FA5 | 230,111,165 |
| C11 | #956447 | 149,100,71 |
| C12 | #E8CFA0 | 232,207,160 |
| C13 | #B8C2CC | 184,194,204 |
| C14 | #3D4652 | 61,70,82 |
| C15 | #FFFFFF | 255,255,255 |
| C16 | #000000 | 0,0,0 |

BG01:

- ID: `BG01`
- name: Midnight Slate
- HEX: `#202533`
- RGB: `32,37,51`
- presentation/gameplay background only
- never a logical artwork color
- never counts toward used-color legality.

### Palette loader requirements

Implement a narrow contract module, expected location:

`src/scrubbots_pixel_factory/contracts/palette.py`

The API may differ slightly if justified, but it must provide:

- immutable canonical palette representation;
- deterministic ID → RGB/HEX lookup;
- deterministic RGB → canonical ID lookup;
- canonical ascending C-ID ordering;
- local used-palette ordering by ascending C-ID;
- validation of palette schema/content;
- explicit rejection of duplicate IDs;
- explicit rejection of duplicate RGB values that make reverse lookup ambiguous;
- rejection of C17+ or malformed logical IDs;
- rejection of BG01 as a logical cell color;
- fail-closed behavior for off-palette RGB/HEX.

Do not silently normalize illegal logical colors into the nearest canonical color.

### Canonical source integrity

Tests must verify all 16 exact IDs/HEX/RGB values.

Prefer a deterministic semantic integrity assertion against the vendored JSON data.

The production/test runtime must not require network access or the main ScrubBots checkout.

## 8. Difficulty and dimensions — PAG-S01.2

Implement:

- PAG-0111 through PAG-0120.

Expected location:

`src/scrubbots_pixel_factory/contracts/difficulty.py`

Canonical production difficulties:

- `EASY`
- `MEDIUM`
- `HARD`
- `VERY_HARD`

No `EXTRA_HARD`.
No `TEST` production difficulty in this standalone generator contract.

Dimension bands:

| Difficulty | Width | Height |
| --- | --- | --- |
| EASY | 20..29 | 20..29 |
| MEDIUM | 30..39 | 30..39 |
| HARD | 40..49 | 40..49 |
| VERY_HARD | 50..59 | 50..59 |

Requirements:

- validate width independently;
- validate height independently;
- rectangles are first-class legal boards;
- never assume `width == height`;
- reject 19 and 60 at outer edges;
- test every cross-band boundary: 19,20,29,30,39,40,49,50,59,60;
- reject legacy fixed 40×40 / fixed 50×50 assumptions;
- reject `EXTRA_HARD` and spelling/case aliases unless explicitly normalized by a documented strict enum parser;
- never expose a fifth production difficulty.

### Deterministic automatic dimension selection

PAG-0118/0119 require automatic seeded selection.

Do **not** implement the general M02 deterministic RNG abstraction yet.

For M01 only, use a narrow project-owned stable selection primitive based on deterministic hashing/domain separation, for example SHA-256-derived integer selection.

Requirements:

- no use of module-global `random`;
- width and height must use distinct deterministic domains/subkeys;
- same difficulty + same seed = same dimensions;
- dimensions always remain inside band;
- across a reasonable fixed test seed set, both square and rectangular outputs must occur;
- selection result must not depend on Python hash randomization.

Keep this helper internal/narrow so M02 can later define the full RNG architecture without inheriting accidental global randomness.

## 9. Difficulty actual-used-color contracts — PAG-S01.3

Implement:

- PAG-0121 through PAG-0130.

Canonical actual distinct-used-color bands:

| Difficulty | Used canonical logical colors |
| --- | --- |
| EASY | 3..5 |
| MEDIUM | 6..7 |
| HARD | 8..9 |
| VERY_HARD | 10..12 |

The count means:

**distinct canonical logical cell colors actually present in the logical artwork cells.**

It does not mean:

- requested palette length;
- metadata palette length;
- BG01;
- CLEARED transparency;
- presentation grid/border colors.

### Required API behavior

Provide generator-independent helpers to:

- count distinct canonical logical colors from an iterable/grid of logical C-IDs;
- reject BG01 if supplied as a logical cell;
- reject off-palette/malformed C-IDs;
- validate actual used-color count against difficulty;
- produce ascending used-palette IDs;
- deterministically choose a legal canonical palette subset from difficulty + seed;
- accept an explicitly supplied canonical subset only when valid;
- reject duplicate entries in an explicit subset;
- reject BG01/off-palette IDs in an explicit subset;
- reject explicit subset sizes incompatible with difficulty;
- return explicit validation failure rather than silently trimming/expanding supplied subsets.

### Deterministic palette subset selection

Do not implement M02's general RNG.

Use a narrow stable hash-derived selection method.

Requirements:

- same difficulty + seed = identical subset;
- chosen subset size is always inside the difficulty band;
- all entries are C01..C16;
- subset contains unique IDs;
- returned order is ascending canonical C-ID;
- multiple fixed seeds can produce distinct valid subsets;
- result does not depend on set/dict/hash iteration order.

## 10. M01 acceptance semantics

Tasks PAG-0131..0133 must be satisfied **without creating M02's GenerationRequest class**.

For M01 acceptance, prove that for every legal production difficulty the contract layer can resolve a coherent set of:

- legal width;
- legal height;
- legal canonical palette subset;

from explicit values and/or deterministic seed selection.

Do not create `GenerationRequest` in M01.

PAG-0132 requires illegal dimensions/color-band combinations to fail before any generator exists.

PAG-0133 requires all M01 tests to run without importing generator-family modules.

## 11. Suggested package shape

Expected narrow additions:

```text
data/
  palette/
    scrubbots_palette_v2.json

src/scrubbots_pixel_factory/
  contracts/
    __init__.py
    palette.py
    difficulty.py
    color_usage.py
    _stable_select.py      # optional, narrow M01-only helper

tests/
  unit/
    test_palette_contract.py
    test_difficulty_contract.py
    test_color_usage_contract.py
  integration/
    test_m01_contract_acceptance.py
```

Exact filenames may differ if architecture is cleaner, but separation must remain obvious.

Do not add empty future generator folders solely to match the long-term tree.

## 12. Required negative tests

At minimum test:

### Palette
- all exact 16 values;
- missing required canonical color;
- duplicate ID;
- duplicate RGB;
- C17;
- BG01 as logical;
- unknown HEX/RGB;
- invalid schema/version if loader validates them.

### Dimensions
- 19/20/29/30/39/40/49/50/59/60;
- each difficulty min/min and max/max;
- valid rectangles;
- invalid one-axis cross-band boards such as:
  - EASY 20×30
  - MEDIUM 39×40
  - HARD 49×50
  - VERY_HARD 49×59;
- legacy `EXTRA_HARD`;
- fixed-size assumptions are absent from API/tests.

### Used colors
- exact min/max per difficulty;
- one below / one above every band;
- duplicate cells do not inflate count;
- BG01 does not count and is rejected as logical data;
- off-palette cell rejected;
- explicit valid subsets;
- duplicate explicit subset rejected;
- wrong-size explicit subset rejected.

## 13. Determinism tests

At minimum:

- same seed/difficulty → same dimensions;
- same seed/difficulty → same auto palette subset;
- repeated executions produce same results;
- fixed seed sample demonstrates rectangular outputs exist;
- fixed seed sample demonstrates more than one valid palette subset;
- deterministic logic uses no uncontrolled global randomness.

## 14. Offline/security regression

All M00 tests must remain green.

New M01 code must:

- introduce no runtime network dependencies;
- operate inside `offline_runtime()`;
- not import networking modules;
- not require GitHub/main ScrubBots at runtime;
- not read arbitrary files outside the standalone repo;
- not mutate the vendored canonical palette during execution.

Run the full test suite, not only new M01 tests.

## 15. Prohibited shortcuts

Do not:

- edit the main ScrubBots repo;
- change any canonical palette RGB/HEX value;
- add C17+;
- treat BG01 as C16 or logical artwork;
- count requested-but-unused colors as actual used colors;
- count BG01 or transparency;
- assume square boards;
- add Extra Hard;
- hardcode one dimension per difficulty;
- use Python global `random` for deterministic contract selection;
- create M02 `GenerationRequest`;
- start generator implementations;
- edit ChatGPT-owned tracker/audit/task state;
- self-audit.

## 16. Required verification

Before builder handoff, run and log:

- focused palette contract tests;
- focused difficulty/dimension tests;
- focused used-color/subset tests;
- M01 integration acceptance tests;
- full repository pytest regression;
- direct standalone import;
- `pip check`;
- `git diff --check`;
- static/no-network source-policy regression;
- deterministic repeated-run smoke.

Record exact test totals and failures/corrections.

## 17. Builder exit criteria

The builder may stop as **implementation complete / pending independent audit** only if:

- PAG-0101..PAG-0133 have implementation/test evidence;
- all four legal difficulties pass contract acceptance;
- all required boundary/negative cases pass;
- local palette exactly matches pinned owner-locked source;
- deterministic auto dimensions/subsets are proven;
- M00 regression remains green;
- no PAG-M02 implementation started;
- matching Codex log is complete;
- source/log commits are pushed;
- final log contains exact final commit SHA(s), push result, local HEAD, remote HEAD, and equality/divergence.

Do not mark tasks complete. Do not update H!veAI acceptance state. ChatGPT will perform the independent strict audit.
