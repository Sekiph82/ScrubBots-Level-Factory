# SB-LF01-009-R01 | GPT independent source + hosted-CI audit V01

Date: 2026-10-15 Europe/Istanbul. Source under review: `f0e257c`, `81ee0c6`, `c875a96`, `26fed2bea626c855352b6fdf77049a8381f2e55b`. Final builder-log-only HEAD: `1002b0f8363da436168502c561223063d0caf1be`. Parent GPT audit: `.hiveai/audits/SB_LF01_009_010_M01_03_GPT_INDEPENDENT_AUDIT_V01.md`.

## Verification boundary
Independently fetched the GitHub compare and exact per-file code changes, current `release_pool.py`, canonical Studio owner-source validation/derivation, two PNG decoders, workflow, tests, builder log, root TASKS and GitHub Actions REST run/job/artifact metadata. Hosted run `38778083211` at exact tested SHA `26fed2bea...` is **completed/success**; its single job and its regression step report success; JUnit/console artifact `11995020833` is present, digest `sha256:9163c90807328fcacb4f313b720a10cff19d1139c2a6975d367fd24d9c25b685`, expires 2026-10-22. **12 passed / 0 failed / 0 skipped** is the builder log's narrow pytest count; the raw JUnit/console bytes were not independently downloaded or executed here. First run `38777563242` was 11 PASS / 1 FAIL per builder, followed by reported corrected runs `38777721560`, `38777891467` and final `38778083211`. No full regression or native owner test is claimed.

## Independent findings

**F01 previous legacy publication bypass: SOURCE PASS.**
- `release_entries()` remains the legacy-visible historical view; no historical mutation. A separate `_production_release_entries()` selector demands `PRODUCTION_CANDIDATE`, `OWNER_ACCEPT` and current review/entry identity.
- `build_release_plan()` and `validate_release_plan()` now consume the same selector. Invalid/legacy selected IDs fail before `approve_release_plan()` can invoke `publish_batch()`. Focused synthetic tests check the selector and a publish spy, albeit by mocking historical entry retrieval. This closes the previous F01 in source scope.

**F02 previous claimed-source/grid mismatch: SOURCE PASS for supported strict-logical PNG input.**
- `enter_release_pool()` calls classification plus new byte verification; `validate_release_plan()` repeats it for each selected candidate. The gate binds owner source hash, source record, exact dimensions, decoded row-major cells, logical grid hash and candidate artwork PNG bytes/hash.
- One synthetic exact-source acceptance path reaches the downstream canonical Difficulty gate without fabricating successful production; a self-consistent incorrect-grid candidate fails at Pool entry. Source reads have per-file size limits and canonical path checks. This fixes the prior missing comparison for the newly selected PNG profile.

**F03 NEW blocking incompatibility: original OWNER_UPLOAD PNG format decoder differs from the accepted Studio derivation contract.**
- `studio_extensions._validation_pixels()` and `_derive_owner_candidate()` decode original owner bytes with `semantic.normalization.core._decode_raw` / `_decode_png_rgba`. That strict *owner source* decoder supports PNG scanline filters 0,1,2,3,4 and accepts safe ancillary PNG chunks, plus grayscale, grayscale-alpha, RGB and RGBA under its constraints.
- New `release_pool._validate_source_grid_bytes()` instead invokes `output.png.decode_logical_png(source_png)`. That *exported logical artwork* codec rejects every nonzero PNG row filter, all ancillary chunks and color type 0/4. As a result, a legitimate original source previously imported, validated and derived by the Studio can be rejected at new production Pool entry **despite identical logical cells**. This is a deterministic code-path mismatch, not evidence of actual owner 002 failing: no private PNGs were read.
- The new positive-control PNG is `encode_logical_png()`, which itself emits a minimal filter-0 RGB/RGBA PNG; so 12 focused tests do not cover this compatibility difference. This violates the owner-source exactness and preservation acceptance boundary. Do not close SB-LF01-009 yet.

## Decision

- `SB-LF01-009`: **R01 PARTIAL / F01 SOURCE PASS / F02 SOURCE PASS WITH F03 COMPATIBILITY BLOCKER / NOT CLOSED**.
- `SB-LF01-010`: remains previously GPT source-PASS / CLOSED, unchanged.
- `R05 / SB-LFX-018`: deferred/open; prior owner-native/game/cloud authority, 19 deselected, 19 skipped and 6 ignored modules remain unwaived. Do not substitute focused 12 tests for full release certification.
- Prior nine READY/4-4-1, accepted 002, 140 loaded PNG, installed Studio and 3,204 untracked owner paths were **reported** untouched by builder; GPT did not access Desktop to prove their hashes/status.

## Next bounded correction (R02)
Reuse the **same authoritative strict OWNER_UPLOAD pixel decoder and palette/VOID mapping** that `_derive_owner_candidate` used. Apply the unchanged exact source-vs-artwork grid binding and fail-closed hashing/dimension checks. Add reproducible synthetic positive inputs with PNG filter 1/2/4, optional safe tEXt metadata and canonical RGB(A) logical pixels; pair with altered-grid and invalid-alpha/foreign-color negatives. Verify through the actual Pool promotion check (at least to the next authority gate) and one selected-plan revalidation; no fabricated native READY or production publication. Repeat only narrow hosted synthetic tests, no 140 PNG solver, Windows TEMP, Release writes or R2. After independent R02 review, close 009 if proven and move to locally feasible M02; do not reopen R05 by default.
