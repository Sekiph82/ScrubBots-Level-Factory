# SB-LFX-018 R05 M03 | V2 Content Contract, Current Game Authority and R2 S3 Gate | Independent Audit V05

**Date:** 2026-10-19, Europe/Istanbul. **Auditor:** ChatGPT, independent GitHub source and commit review of builder log, owner-provided 837-line transcript. **No Windows execution or R2 write was performed by GPT.**

**Verdict:** The narrow source repair for genuine LevelData V2 VOID is **STATICALLY ACCEPTABLE**, and the reported targeted Python results are **BUILDER PASS ONLY**. Full authentic owner-002 CPX001 pack, STAGING upload and CPX002 test are **NOT VERIFIED**. M03 FULL OPEN.

## Repository evidence
- LF remote main independently verified: 952c38a914bd4482d4646649c5dc46b80c5bdfec.
- Game Scrubbots remote main independently verified: 9663c44c0b40dd08b082e4c5a54f808efb481704.
- Compare LF baseline 49fb070d2b7cf6346362c79afee6d02e776d3da2 to 952c38a: three commits ahead, none behind, nine changed paths, including eight product/docs/schema/tests and the existing builder log only.
- Product commit 8c959d9a2ea1d4d8cf639925a1caffd1938ee5b4. Final builder receipt commit 952c38a914bd4482d4646649c5dc46b80c5bdfec.
- Builder evidence: .hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md, sections Explicit owner-authorized STAGING continuation, LevelData V2 solver-identity guard follow-up, Publication receipt.

## Actual changed source reviewed
1. content_pipeline/src/scrubbots_content_pipeline/content_boundary.py: explicit Level Data Specification v1 or v2 descriptor allowed; other allowlist families unchanged.
2. content_pipeline/src/scrubbots_content_pipeline/payload_validation.py: v1 semantics retained; V2 accepts only indexed artwork or -1 VOID, must have nonzero VOID, at least 200 artwork cells, and at least 25% artwork area. Dimensions/palette/index types remain restricted; booleans rejected. A side-effect-free shared validator fails closed on bad dimensions.
3. content_pipeline/src/scrubbots_content_pipeline/scrubpack_solver_identity.py: same V2 cell guard is applied during solver proof binding, no longer only nonzero artwork. Historical ready pipeline SHA and current game authority are not silently relabeled.
4. scripts/build_accepted_factory_output_pack.py: rejects unsupported LevelData versions and writes the actual v1/v2 version in the descriptor, not a hard-coded v1 claim.
5. content_pipeline/schemas/v1/content-boundary.schema.json: accepts 1 and 2 for level-data contract version only.
6. content_pipeline/README.md: documents the scope.
7. tests/unit/test_sb_cp00_003_payload_validation.py: V2 accepted 200/200 artwork/VOID, rejected 199 artwork, -2, no VOID, and 32x32 quarter boundary (255 rejected, 256 accepted).
8. tests/unit/test_sb_cp00_002_content_boundary.py: schema version allowlist assertion.

**Assessment:** This source diff addresses a proven V2 / v1-only content boundary incompatibility. Existing tests verify payload/schema behavior, **but the actual 002 CPX001 package did not successfully build**; there was no real end-to-end pack-level regression. Do not infer R2 readiness from the small unit suite.

## Real blocked attempts and legitimate remaining work
- Initial accepted-pack builder attempt selected Desktop repository root, which lacks installed owner READY pool. This was a root-selection error, not missing owner authority.
- Corrected installed Release root identified authentic owner 002 and failed at v1-only CONTRACT_MISMATCH, justifying the source fix.
- Even after v2 support, the owner 002 accepted READY solver pipeline's recorded game git_head is **aef60a616d4ac401e9dfac15df6fe56e671c0053**, whereas the current canonical Scrubbots game main is **9663c44c0b40dd08b082e4c5a54f808efb481704**. A fully authenticated CPX001 proof must be freshly derived for current game authority, not modified in an old READY JSON, not based on synthetic solver hashes, and not via an always-true authority callback.
- Codex reported 5 targeted pytest cases PASS, six Python AST parses and git diff check PASS. No current-authority 002 package, CPX001 artifact, STAGING upload/readback receipt or actual CPX002 pass was produced. Neither prior successful 002 replay nor Level11 seed92 were redundantly rerun.
- Process, user and machine environments had no R2_ACCOUNT_ID, R2_ENDPOINT_URL, R2_ACCESS_KEY_ID or R2_SECRET_ACCESS_KEY. No relevant separate local credential was found. The connected Cloudflare API read connection is **not** proof that the canonical factory S3 client has matching account credentials.
- Existing 002 is owner ACCEPT / MEDIUM / unassigned. Seed92 is a distinct EASY READY_AUTO / unassigned item, not owner accepted and not part of this package.
- Prior two task TEMP directories were owner-removed and builder verified absent. Old 17-pool read PASS remains valid. No owner Release data or bucket was changed by this continuation.

## Owner authorization already received and bounded
The owner explicitly authorized creation of ONE authentic original owner 002 solver-proven package, STAGING-only write and same-provider independent readback in approved bucket scrubbots-content-prod/staging/, followed by true CPX002. Do not ask for duplicate staging approval. No production key, promotion, overwriting unrelated data, broad Cloudflare token, CI or GitHub Actions was authorized.

## Concrete continuation under the SAME M03 V02 master
1. Preserve original owner upload/review/READY source hashes. Use current LF product source and explicitly configured installed Release data root, **not older installed code**.
2. Produce a **new additive canonical owner002 solver-proven READY pipeline for the actual current game main SHA**, referencing unchanged 32x32 V2 LevelData and real four-FIFO supply plan. This is a new authority-proof task, not a pointless rerun of old passed replay. If no safe supported current-main runner can bind those bytes, report exact missing integration rather than rewriting historical owner data.
3. Run an actual focused authentic owner002 build through build_accepted_factory_output_pack and build_solver_proven_scrubpack with a genuine current authority reread callback; add a pack-level negative test and ensure produced archive bytes/size/hash and solver identity are actually verified. No fabricated receipts or forced PASS.
4. Bind a real securely configured local R2 S3 client to the exact approved connected Cloudflare account and bucket. The owner alone must set up the missing credential in a secure process environment. Do not send secrets to chat/GitHub or log account IDs. Ensure only authorized STAGING prefix writes with create-if-absent/conditional guards and no production writes.
5. Only after real CPX001 pack and credential binding exist, publish bounded STAGING objects and manifest, read both back through the SAME provider with exact SHA256/size/level IDs, then run the real pack-backed CPX002 in a legitimately authorized clean DETACHED origin/main checkout with isolated Godot AppData. Clean only new task-owned TEMP at end.
6. If the credential or current authority cannot actually be obtained, stop on that precise blocker. Do not repeat global empty-bucket scans, stale successful native tests, or create fake externally staged proof.

## Final audit statuses
- M03_V2_CONTENT_CONTRACT_SOURCE_STATIC_AUDIT_ACCEPTABLE
- M03_V2_TARGETED_5_TESTS_BUILDER_PASS_NOT_GPT_EXECUTED
- CPX001_ACTUAL_OWNER002_PACK_NOT_BUILT
- CPX001_OLD_GAME_AUTHORITY_AEF60A_VS_MAIN_9663C44
- R2_LOCAL_CANONICAL_S3_CREDENTIALS_ABSENT
- STAGING_REMOTE_WRITE_NOT_PERFORMED
- CPX002_REAL_STAGING_DOWNLOAD_TEST_NOT_VERIFIED
- M03_FULL_OPEN_R05_PRODUCTION_OPEN

**Independent conclusion:** The implemented V2 fix is worth retaining. The remaining gates are authentic **current-main solver authority** and **secure local R2 S3 credentials**, not missing upload approval and not a regression in previously accepted owner 002 data.
