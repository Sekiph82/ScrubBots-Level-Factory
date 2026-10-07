# M18 + CPX-004 MASTER — Cloudflare R2 Remote Publish

Document role: CODEX BUILDER LOG

## Session start

- Starting timestamp: 2026-10-07T15:07:22+03:00
- Canonical repository: Sekiph82/ScrubBots-Level-Factory (https://github.com/Sekiph82/ScrubBots-Level-Factory)
- Persistent Desktop root verified: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; branch main; starting HEAD 7c6051589d0a95fc785d7f182ccd0d7f8d7013ce; origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git; after git fetch --prune origin, origin/main=3d5dc46737e72f970fff989d40890eb217b8acf9; divergence 0 ahead / 417 behind.
- Desktop status at preflight: 123 tracked modified paths and 766 untracked paths (889 dirty paths); 18 stashes; 22 worktree entries including one pre-existing prunable worktree entry. Dirty/incoming overlap check: 0 overlaps across 378 incoming changed paths. Desktop preserved byte-for-byte; not synchronized due owner work and large divergence.
- Authorized execution root: %TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-MASTER; detached clean worktree at 3d5dc46737e72f970fff989d40890eb217b8acf9, origin/main exact match, 0/0 divergence.
- Files read before implementation: root TASKS.md, AGENTS.md, GOVERNANCE.md, this authoritative master prompt, previous M14 CP03/CPX-002 audit, and M11-M14 provider/publisher/manifest/release contracts to be enumerated below.
- Authorized order: SB-CP07-003 → 004 → 005 → 006 → 007 → 008 → 009 → 010 → SB-CPX-004. Root TASKS.md and .hiveai/audits/** remain protected.

## SB-CP07-003 — Provider adapter

Status: IN PROGRESS



### Pre-implementation contract review and correction

- Read `.hiveai/audit-criteria/M18_CPX004_R2_LIVE_PUBLISH_MASTER_AUDIT_CRITERIA.md`, `.hiveai/audits/M14_CP03_001_012_CPX002_FINAL_CLOSURE_STRICT_REAUDIT.md`, and the authoritative provider/config/staging upload/staging manifest/promotion/activation/one-command/report modules. Existing M14 closure requires staging-first exact-byte verification, current-main replay, explicit approval, manifest CAS, append-only release history, and secret-free report behavior.
- `TASKS.md` confirms exact master authorization at base SHA `3d5dc46737e72f970fff989d40890eb217b8acf9`; no tracker or audit changes are permitted.
- Live credential availability check inspected presence only (never values): `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, and `R2_BUCKET` are absent. No remote R2 call has been made. The live round trip will remain pending if credentials remain absent.
- Initial PowerShell interpolation inserted two NUL bytes where literal zero counts were intended in this new log. Corrected both immediately to `0` before implementation; no prior evidence was modified.

## SB-CP07-003 — Provider adapter

### Implementation decision

- Added an isolated `r2_provider.py` behind the existing provider-neutral methods. Uses lazy `boto3` S3 client construction, `region_name="auto"`, path style, canonical bucket, environment prefixes, conditional create/copy, exact SHA checks, and normalized result categories. SDK/exception text is never included in results or repr. No delete capability is advertised.
- Added boto3 as the Content Pipeline's optional-by-deployment runtime client dependency. Offline generation and tests do not initialize a client or need credentials.
- Added deterministic fake-S3 tests for namespace separation, missing credentials, direct-production-write rejection, immutable key collision, exact round trip/hash, normalized provider failure, copy rejection, corruption detection, and delete-capability absence.
- Commands: `python` import/presence probe (boto3 unavailable; no R2 env values present); repository contract review via `rg` and source reads; implementation patch applied. Focused test command pending.
- First `python -m pytest tests/unit/test_sb_cp07_003_r2_provider.py -q` run: **2 failed, 5 passed**. It found that injected clients bypassed missing-credential validation, and the fake S3 call counter counted conditional conflicts as requests. Corrected the provider to require endpoint + both credential variables before using any client, and corrected the assertion to verify persisted bytes/object count rather than request count. Re-run follows.
- Second focused run found two assertion-only mistakes in newly added coverage (the release ledger key is not serialized into its payload; S3-compatible metadata stores the requested literal `no-cache`). Corrected those assertions; no product-code change was needed for these two failures.
- Final SB-CP07-003 focused test: `python -m pytest tests/unit/test_sb_cp07_003_r2_provider.py -q` — **9 passed**.
- M14 publisher regression selection: `python -m pytest tests/unit/test_sb_cp03_004_staging_pack_upload.py tests/unit/test_sb_cp03_006_staging_manifest_publish.py tests/unit/test_sb_cp03_008_production_promotion.py tests/unit/test_sb_cp03_009_production_manifest_activation.py tests/unit/test_sb_cp03_010_no_silent_live_overwrite.py tests/unit/test_sb_cp03_011_one_command_publisher.py -q` — **45 passed**.
- Implementation files: `content_pipeline/src/scrubbots_content_pipeline/r2_provider.py`, `content_pipeline/pyproject.toml`, `tests/unit/test_sb_cp07_003_r2_provider.py`.
- Dependency note: boto3 is declared (`>=1.37,<2`); it is not installed in this execution environment. Unit tests inject a fake S3 client and do not require it. No runtime network request was made.
- `git diff --cached --check` passed. Implementation commit: `1f5189014c25d18441440bd9a36c312cb6741cb0`.
- Child result is implementation evidence only; real R2 credential/network verification remains unavailable and is not marked PASS.

## SB-CP07-004 — Staging/production separation

Status: IN PROGRESS

- The adapter physically prefixes unchanged neutral object keys with `staging/` or `production/`, rejects already-prefixed and `_control/` logical keys, restricts pack writes to STAGING, and restricts manifest writes to `manifests/current.json` under the exact target identity.
- Added focused namespace tests proving identical logical keys cannot alias, control objects cannot enter the game content path, and direct production writes/control-manifest writes fail closed.
- Commands: pending focused namespace and M14 publisher regressions.
- `git diff --cached --check` initially rejected one extra blank line at EOF in the new CP07-004 test. Removed only that trailing whitespace; focused/regression test results above are unchanged. Rechecking and committing.

- SB-CP07-004 tests: python -m pytest tests/unit/test_sb_cp07_004_r2_namespace_separation.py tests/unit/test_sb_cp07_003_r2_provider.py -q — **12 passed**; selected M14 publisher regressions — **45 passed**. Implementation/test commit: `9312b2c0cdefbf83fee7de8b8a597bff4704ea02`. Corrected git diff --cached --check passed.

## SB-CP07-005 — Immutable/versioned naming

Status: IN PROGRESS

- Production pack promotion remains copy-if-absent and exact source SHA checked. Stable manifest writes now require exact prior bytes/hash, exact prior content version, strictly increasing successor version, and a current release-state pending-event fence; conditional S3 writes protect the observed ETag.
- Added collision, prior-version mismatch, non-increasing version, and manifest-byte-preservation tests. Manifest history remains in the existing M13/M14 authority; the provider does not create a vendor-specific history schema.
- Commands: pending focused immutability/provider tests and M14 publisher regressions.

- SB-CP07-005 focused tests (provider/namespace/immutability) — **15 passed**; selected M14 publisher regressions — **45 passed**. Implementation commit: `01998e5f540dff2b9a3b4e5c76da822cf71e742d`. git diff --cached --check passed.

## SB-CP07-006 — Upload/download/hash round trip

Status: IN PROGRESS

- Added an opt-in live test limited to `staging/_integration/roundtrip/<sha256>.bin`. It accepts only successful or idempotent conditional-create status, then requires exact downloaded bytes, byte length, and SHA-256. It cannot address PRODUCTION.
- Existing CP07-003 unit tests cover local exact-byte readback, length/hash, idempotence, and mismatch detection. Live credentials remain absent based on presence-only environment inspection; the integration test should be reported as skipped, never PASS.
- Commands: pending focused M18 tests + M14 regression.
- `git diff --cached --check` initially found one extra blank line at EOF in the CP07-006 test. Removed only trailing whitespace; test outcomes remain unchanged. Rechecking before commit.

- SB-CP07-006 focused suite: **15 passed, 1 skipped**; skip reason exactly OWNER_R2_WRITE_CREDENTIAL_REQUIRED. The live R2 object was not written. Selected M14 publisher regressions — **45 passed**. Test commit: `4d58a0500f2745e2bba1f035cf8f1cf8ba2de4b9`. Corrected git diff --cached --check passed.

## SB-CP07-007 — Cache/CDN metadata

Status: IN PROGRESS

- `.scrubpack` writes use `application/octet-stream` and `public, max-age=31536000, immutable`; current manifest writes use `application/json` and `no-cache`.
- Added operator documentation for locked namespace mapping, stable production manifest key, cache policy, and the distinction between Family Test `r2.dev` delivery and a future custom CDN.
- Added focused metadata verification. Commands pending alongside selected M14 publisher regressions.
- Initial CP07-007 `git diff --cached --check` stopped on an extra trailing blank line in the new test. Removed trailing whitespace; focused/regression outcomes were already green and are unchanged.

- SB-CP07-007 focused M18 suite — **16 passed, 1 skipped** (live R2 credential gate); selected M14 publisher regressions — **45 passed**. Implementation/docs commit: `f5406e9005fcd628bdbba20e7c4e6787ce0c00d0`. Corrected git diff --cached --check passed.

## SB-CP07-008 — Backup/export/migration path

Status: IN PROGRESS

- Added `export_current_production()`: reads only the exact current production manifest and its referenced packs, validates canonical manifest bytes, pack lengths and hashes, and produces a deterministic secret-free receipt. All remote reads and integrity checks complete before local output creation. Existing files are refused to preserve destination data.
- Added successful exact export, deterministic receipt, corrupt/missing pack, and existing-file preservation tests. This provider operation calls no write/copy/delete methods.
- Commands: pending focused export/provider tests and M14 publisher regressions.

- SB-CP07-008 focused M18 suite — **19 passed, 1 skipped** (R2 credential-gated live probe); selected M14 publisher regressions — **45 passed**. Export implementation/test commit: `5ee9d7360466da4830e77f1153c51f79cb698259`. git diff --cached --check passed.
