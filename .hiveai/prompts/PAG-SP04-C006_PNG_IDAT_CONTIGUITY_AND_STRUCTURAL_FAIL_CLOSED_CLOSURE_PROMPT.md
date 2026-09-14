# PAG-SP04-C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any implementation edit:

1. root `TASKS.md` — ONLY current tracker;
2. `.hiveai/audits/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_PROMPT.md`;
4. `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`;
5. current `src/scrubbots_pixel_factory/semantic/normalization/core.py`;
6. `tests/unit/test_sp03_normalization.py`;
7. `tests/unit/test_sp04_c005_ancillary_png.py`;
8. accepted SP04 qualification tests;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** read or use `.hiveai/CYCLE_INDEX.md` or any legacy hidden `.hiveai` tracker/control-plane file to reconstruct current state.

Do not edit root `TASKS.md`.

Create the matching builder log **before any C006 source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_CODEX_LOG.md`

## Mission

Close exactly one technical residual from the C005 strict audit.

C005 correctly allows generic valid ancillary chunks such as the live Magnific-shaped `caBX` and `fdEC`, but it now also accepts an invalid chunk sequence where an ancillary chunk splits a multi-IDAT stream:

`IHDR -> IDAT(part1) -> caBX -> IDAT(part2) -> IEND`

The decoder later concatenates all IDAT payloads and therefore loses the structural violation.

Implement explicit fail-closed IDAT-run contiguity while preserving every accepted C005 behavior.

Do not call Magnific or PixelLab. Spend zero credits. Do not begin SP05, SP06, Studio UI, weekly batch work or M11.

Do not change `AREA_AVERAGE_V1`, crop/pad behavior, ASSET_ART palette policy, provider selection, benchmark corpus, qualification scoring or owner-review policy.

---

# 1. Enforce one contiguous IDAT run

Required structural behavior:

- one IDAT chunk is valid;
- multiple IDAT chunks are valid only when consecutive;
- once the parser has left the IDAT run, another IDAT must be rejected;
- no ancillary chunk may appear between IDAT chunks;
- unknown valid ancillary chunks may remain accepted before the first IDAT and after the final IDAT, subject to all existing structural/CRC/type rules;
- `IHDR` remains exactly first;
- `IEND` remains exactly last and empty;
- at least one IDAT remains required.

Implement this as an explicit parser/state invariant rather than relying on decompression behavior.

Do not special-case only `caBX` or `fdEC`.

---

# 2. Preserve C005 safety and live compatibility

Must remain unchanged:

- four-letter ASCII chunk type validation;
- reserved-bit validation;
- CRC validation for every chunk;
- unsupported/unknown critical chunk rejection;
- truncation/length checks;
- immutable original raw bytes and raw SHA;
- raw byte size limit;
- raw raster dimension limit;
- decode pixel budget;
- bounded zlib output;
- exact decompressed scanline length;
- zlib EOF/trailing-data checks;
- 8-bit/non-interlaced profile;
- supported color types and scanline filters;
- SP03 provenance seals;
- SP04 typed evidence binding.

The accepted live-shaped sequence must continue to work:

`IHDR -> caBX -> fdEC -> IDAT -> IEND`

---

# 3. Required regression tests

Extend C005 tests or add a C006-focused test file. Required proof:

1. baseline single-IDAT PNG decodes;
2. two or more **consecutive** IDAT chunks forming one zlib stream decode identically to the baseline;
3. `IHDR -> caBX -> fdEC -> IDAT -> IEND` remains accepted and pixel-identical;
4. valid ancillary chunk after the complete IDAT run and before IEND remains accepted when structurally legal;
5. `IHDR -> IDAT(part1) -> caBX -> IDAT(part2) -> IEND` is rejected before pixel decode;
6. the same interleaving with another valid ancillary type is rejected generically;
7. unknown critical chunk remains rejected;
8. corrupt ancillary CRC remains rejected;
9. malformed type / invalid reserved bit remain rejected;
10. existing decompression-bomb and exact-budget tests remain green;
11. raw SHA/provenance remains byte-sensitive;
12. normalized pixel output remains unchanged for pixel-equivalent valid inputs.

Do not commit the owner's private Magnific PNG.

---

# 4. Scope discipline

Allowed product change:

- PNG chunk ordering validation in semantic normalization decoder only.

Allowed tests:

- C006/C005/SP03 normalization regression tests required to prove closure.

Do not modify provider bridges, qualification models, palette contracts, resize algorithms, output/export algorithms or unrelated code.

---

# 5. Required verification

Run and log at minimum:

1. C005/C006 ancillary/order tests;
2. SP03 normalization tests;
3. SP04 qualification tests;
4. combined SP01+SP02+SP03+SP04 focused tests;
5. full repository tests;
6. `compileall` or equivalent syntax/import check;
7. package import and CLI smoke;
8. `git diff --check`;
9. offline/network/credential scan over changed product/test files.

Builder results are implementation evidence, not ChatGPT acceptance.

---

# 6. Builder log and publication truth

Matching H1 exactly:

`# PAG-SP04-C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- starting HEAD and origin/main;
- starting divergence and working-tree dirt;
- exact authorities read;
- exact changed files;
- implementation summary;
- all test commands/results;
- proof of no provider call/credit spend;
- implementation commit SHA;
- push result.

Important publication requirement:

After every implementation/log publication commit is complete and pushed, perform one **terminal**:

- `git fetch origin`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git rev-list --left-right --count HEAD...origin/main`

The log must record the true final terminal commit and require equality plus `0 0`. Do not add another commit after the recorded terminal equality checkpoint. If a log correction is needed, make it first, push it, then perform and record the final equality in a way that does not require another publication commit; if the repository workflow cannot satisfy that literally, state the limitation instead of claiming a terminal checkpoint that predates later commits.

---

# Acceptance criteria

C006 is eligible for ChatGPT PASS only if all are true:

- [ ] valid live-shaped `caBX/fdEC` ancillary PNG remains accepted;
- [ ] one IDAT and multiple consecutive IDAT chunks remain accepted;
- [ ] any non-IDAT chunk that splits an IDAT run is rejected fail-closed;
- [ ] post-IDAT valid ancillary handling remains structurally valid;
- [ ] critical/type/reserved-bit/CRC/truncation protections remain intact;
- [ ] bounded decode/decompression protections remain intact;
- [ ] immutable raw bytes/SHA/provenance remain intact;
- [ ] normalization pixels/policy remain unchanged;
- [ ] no provider/palette/qualification policy change occurs;
- [ ] no provider call or credit spend occurs;
- [ ] root `TASKS.md` remains untouched by builder;
- [ ] no legacy hidden tracker/control-plane file is read for current authority;
- [ ] focused and full tests are green;
- [ ] terminal publication evidence is truthful.

Stop after push and wait for ChatGPT strict audit.

After C006 PASS, ChatGPT will immediately rerun the owner-supplied 1024x1024 Magnific artifact through official SP04-Q02/Q03 and present Q04 owner review.