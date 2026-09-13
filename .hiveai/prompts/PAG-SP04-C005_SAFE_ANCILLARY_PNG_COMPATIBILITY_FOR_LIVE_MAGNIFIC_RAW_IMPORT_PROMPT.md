# PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any source/test edit:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md` — live compatibility evidence;
3. `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md` — accepted SP03 closure;
4. `.hiveai/audits/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_STRICT_AUDIT.md` — accepted SP04 offline foundation closure;
5. accepted SP03 normalization source/tests;
6. accepted SP04 qualification source/tests;
7. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** use or read legacy hidden `.hiveai` tracker/control-plane files to reconstruct current state. Root `TASKS.md` is the tracker.

Do not edit root `TASKS.md`.

Create the matching C005 builder log **before any C005 source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_CODEX_LOG.md`

## Mission

Close exactly one live-evidence compatibility failure discovered at SP04-Q02:

The owner-supplied Magnific PNG is a valid 8-bit non-interlaced RGB PNG with valid CRCs, but contains two valid ancillary/private chunks between `IHDR` and `IDAT`: `caBX` and `fdEC`. The current SP03 decoder blanket-rejects every chunk outside `{IHDR, IDAT, IEND}` and therefore rejects a real provider artifact before deterministic normalization can begin.

Implement safe ancillary-chunk compatibility **without weakening raw-byte identity, bounded decoding, critical-chunk safety, provenance, or normalization determinism**.

Do not call Magnific or PixelLab. Do not spend credits. Do not begin SP05, SP06, Studio UI, weekly batches or M11.

Do not change `AREA_AVERAGE_V1`, crop/pad behavior, ASSET_ART palette policy, provider qualification scoring, benchmark corpus, provider selection or owner visual acceptance rules in this cycle.

---

# 1. Preserve immutable raw source identity

The accepted behavior must continue to treat provider/local source bytes as immutable evidence.

Requirements:

- never rewrite, strip, transcode or canonicalize `SemanticRawArtifact.raw_bytes`;
- `raw_sha256` must continue to hash the exact original input bytes;
- ancillary chunks may be ignored for pixel decoding, but must remain present in the immutable raw bytes/evidence;
- no new code path may substitute a rewritten PNG as the raw artifact;
- all existing SP03 provenance seals and SP04 typed evidence bindings must remain intact.

---

# 2. Replace blanket ancillary rejection with PNG-criticality-aware validation

Current `_png_chunks()` has a blanket condition equivalent to:

`if any(kind not in {IHDR, IDAT, IEND} ...): reject`

Replace this with explicit fail-closed PNG chunk classification.

At minimum:

- `IHDR`, `IDAT`, `IEND` remain required critical chunks with current structural validation;
- valid ancillary chunks are identifiable from the PNG chunk type's first-byte ancillary bit / uppercase-lowercase semantics;
- structurally valid ancillary chunks may be ignored by the pixel decoder;
- unsupported or unknown **critical** chunks must still be rejected;
- malformed chunk type codes must be rejected;
- CRC validation remains mandatory for every chunk, including ignored ancillary chunks;
- truncated length/data/CRC remains rejected;
- `IEND` rules remain strict;
- no ancillary chunk may be interpreted as pixel data;
- no network/file-system side effect may be driven by ancillary payload data.

The implementation must be generic enough to accept the observed valid private ancillary chunks `caBX` and `fdEC` without hardcoding those two names as the only allowed provider exceptions.

Do not add permissive behavior for unsupported critical chunks.

---

# 3. Preserve bounded-memory and decompression-bomb protections

C005 must not regress SP03-C002 safety closure.

Preserve and test:

- `RAW_ARTIFACT_MAX_BYTES`;
- `SEMANTIC_RAW_RASTER_MAX_DIMENSION`;
- `MAX_DECODE_PIXELS`;
- bounded zlib output;
- exact expected scanline length;
- stream EOF/trailing-data checks;
- 8-bit only;
- non-interlaced only;
- supported color types only;
- valid scanline filter set only.

Ancillary payloads count toward the bounded raw input size because the immutable original file bytes remain the source artifact.

---

# 4. Add synthetic live-shape regression fixtures

Do **not** commit the owner's private/live Magnific PNG itself.

Add synthetic tests that construct an otherwise valid strict PNG and insert ancillary chunks shaped like the observed live file:

`IHDR -> caBX -> fdEC -> IDAT -> IEND`

Use deterministic synthetic payload bytes and correct CRCs.

Required proof:

1. baseline PNG without ancillary chunks decodes successfully;
2. the same PNG pixel payload with `caBX` and `fdEC` decodes successfully;
3. decoded width/height/pixel RGBA bytes are exactly identical between baseline and ancillary variants;
4. raw SHA-256 differs between the two files, proving immutable raw identity remains byte-sensitive;
5. `SemanticRawArtifact.from_local_file()` accepts the ancillary-bearing valid file after remediation;
6. deterministic 24x24 normalization from the two pixel-equivalent sources yields identical normalized RGBA bytes/hash while preserving distinct source raw artifact digests/raw SHA values in provenance;
7. an unknown synthetic critical chunk is rejected;
8. an ancillary chunk with corrupt CRC is rejected;
9. malformed/non-letter chunk type is rejected;
10. truncated ancillary chunk is rejected;
11. existing decompression-bomb and exact-budget tests remain green.

---

# 5. Keep provider metadata-vs-file mismatch visible

The live evidence records a provider metadata dimension of 2048x2048 while the owner-supplied file examined locally is 1024x1024.

C005 must **not** silently rewrite this evidence or pretend those facts are equal.

This cycle is only decoder compatibility. Do not invent a provider-original dimension reconciliation.

Existing candidate/import contracts that require provider-reported returned dimensions to match provider result provenance must remain unchanged. Local `from_local_file()` must continue deriving dimensions from decoded bytes.

Any future provider-result dimension reconciliation belongs to live qualification evidence or a separate bounded finding if required.

---

# 6. No normalization-policy change in C005

The diagnostic 1024→24 `AREA_AVERAGE_V1` run produced 124 distinct RGBA colors because hard source boundaries were area-averaged.

That is a live visual observation, not authorization to alter resampling policy in C005.

C005 must not add nearest-neighbor, majority-vote, palette snapping or other new resize policy.

After C005 passes strict audit, ChatGPT will execute official SP04-Q03 using the accepted pipeline and present Q04 owner review. Any resize-policy change must be evidence-driven after that review.

---

# 7. Required test evidence

Run and log at minimum:

1. focused SP03 normalization tests;
2. focused SP04 qualification tests;
3. new C005 ancillary compatibility tests;
4. combined SP01+SP02+SP03+SP04 focused tests;
5. full repository test suite;
6. `compileall` or equivalent syntax/import check;
7. CLI/import smoke check;
8. offline/network/credential scan consistent with project governance.

Do not claim independent ChatGPT audit from builder results.

---

# 8. Required builder-log content

Matching H1 exactly:

`# PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start HEAD and origin/main;
- clean/dirty state before implementation;
- exact files read as authority;
- exact files changed;
- implementation summary;
- focused/full test commands and outputs;
- proof no provider call/credit spend occurred;
- commit SHA(s);
- push result;
- final `git rev-parse HEAD`;
- final `git rev-parse origin/main`;
- final divergence `git rev-list --left-right --count HEAD...origin/main` and require `0 0`.

If any requirement cannot be verified, say so explicitly and stop rather than manufacturing evidence.

---

# Acceptance criteria

C005 is eligible for ChatGPT PASS only if all are true:

- [ ] valid ancillary chunks no longer cause blanket rejection;
- [ ] unknown/unsupported critical chunks remain fail-closed;
- [ ] observed live shape `caBX` + `fdEC` is covered by synthetic regression tests;
- [ ] ancillary and baseline variants decode to identical RGBA pixels;
- [ ] original raw bytes and raw SHA remain distinct and immutable;
- [ ] local raw artifact import accepts the valid ancillary-bearing synthetic PNG;
- [ ] normalized RGBA result remains deterministic and pixel-equivalent;
- [ ] source provenance remains distinct for byte-distinct raw inputs;
- [ ] CRC/truncation/malformed-type tests fail closed;
- [ ] bounded decompression protections remain intact;
- [ ] no normalization-policy/provider-policy expansion occurs;
- [ ] no Magnific/PixelLab call or credit spend occurs;
- [ ] root `TASKS.md` remains untouched by builder;
- [ ] builder log was created before C005 implementation edits;
- [ ] final HEAD == origin/main and divergence is `0 0`.

Stop after push and wait for ChatGPT strict audit.
