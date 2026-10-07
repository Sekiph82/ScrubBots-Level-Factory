# SB-CP07-003-C001 — Cloudflare R2 Provider Adapter

Repository: `Sekiph82/ScrubBots-Level-Factory`

Standing governance:
- Root `TASKS.md` is READ-ONLY for Codex. ChatGPT is the sole lifecycle/status writer.
- Before implementation, non-destructively sync `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` with latest `origin/main`. Preserve all owner-local work. Never reset --hard, clean, force checkout, force push, or discard owner files.
- If the persistent checkout cannot be made safe/clean without touching owner work, use one TEMP worktree from exact latest `origin/main` and record that truthfully.
- Do not write `.hiveai/audits/**`.
- Push normal commits only; no force.
- Cloudflare R2 authority is owner-locked and already provisioned:
  bucket `scrubbots-content-prod`
  Family Test public read base `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev`
- Never commit, print, log, serialize, screenshot, or place in an APK any R2 access key, secret key, API token, session token, signed URL credential, or connection string.
- The public r2.dev base URL and bucket name are non-secret.
- Remote payload remains declarative-only. No GDScript, native library, plugin, bytecode, executable, shader, or evaluable payload may enter a .scrubpack.
- Preserve the closed M11-M14 provider-neutral Content Pipeline contracts. Extend through the existing provider interfaces rather than bypassing them.
- Production promotion must remain staging-first, byte/hash verified, current-Scrubbots-main replay gated, owner-approved, version-monotonic, and conditional/CAS protected.


## Task
Implement the real Cloudflare R2 provider adapter behind the existing provider-neutral interfaces in `content_pipeline/src/scrubbots_content_pipeline/`.

Requirements:
1. Add a narrow provider-specific module/package, preferably `providers/cloudflare_r2.py`; do not put Cloudflare names into manifest/scrubpack schemas.
2. Use R2's S3-compatible endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, region `auto`, and a maintained Python S3 client such as boto3 unless the repo already has a better dependency.
3. Load credentials only from process environment or an injected secret resolver. Canonical environment variable names:
   - `SCRUBBOTS_R2_ACCOUNT_ID`
   - `SCRUBBOTS_R2_ACCESS_KEY_ID`
   - `SCRUBBOTS_R2_SECRET_ACCESS_KEY`
   - optional `SCRUBBOTS_R2_SESSION_TOKEN`
   - `SCRUBBOTS_R2_BUCKET` (canonical value `scrubbots-content-prod`)
   - `SCRUBBOTS_R2_PUBLIC_BASE_URL` (canonical Family Test value above)
4. Fail closed if required write credentials are absent. Never fall back to anonymous mutation.
5. Implement only the capabilities genuinely supported and required by current CP03 publisher surfaces: exact-byte write/read/verify, conditional manifest write, staging→production promotion/copy, release-event read/append, and current-state fencing. Do not advertise OBJECT_DELETE unless an actual accepted contract requires it.
6. Normalize provider failures to existing `ProviderResultCategory`; never return raw provider error text into persistent evidence.
7. Add deterministic unit tests with a fake/mocked S3 layer, including missing credentials, stale precondition, hash mismatch, failed copy, failed readback, and redaction.
8. No live production mutation in this child.

Builder log:
`.hiveai/codex-logs/SB-CP07-003-C001_CLOUDFLARE_R2_PROVIDER_ADAPTER_CODEX_LOG.md`
