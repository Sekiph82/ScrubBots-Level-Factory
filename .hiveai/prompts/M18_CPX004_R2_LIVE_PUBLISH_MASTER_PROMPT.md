# M18 + CPX-004 MASTER — Cloudflare R2 Remote Publish

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository: `Sekiph82/ScrubBots-Level-Factory`

Owner-locked infrastructure:
- R2 bucket: `scrubbots-content-prod`
- Family Test public read base: `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev`
- ScrubBots game runtime CP04/M15 + CP05/M16 and clean-regression gate are already closed in `Sekiph82/Scrubbots`.
- Root `TASKS.md` is read-only for Codex. ChatGPT is sole tracker writer.

Execution order:
1. SB-CP07-003 — real R2 provider adapter
2. SB-CP07-004 — staging/production separation
3. SB-CP07-005 — immutable/versioned naming
4. SB-CP07-006 — upload/download/hash round trip
5. SB-CP07-007 — cache/CDN metadata strategy
6. SB-CP07-008 — backup/export/migration path
7. SB-CP07-009 — least-privilege secret boundary
8. SB-CP07-010 — provider-specific isolation
9. SB-CPX-004 — Factory Studio “Publish to ScrubBots” handoff

SB-CP07-001 and SB-CP07-002 are already owner-closed: Cloudflare R2 is selected and provisioned.

## Mandatory first task — sync

1. Canonical persistent root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
2. Record repo identity, HEAD, origin, dirty state, worktrees and stashes.
3. Run `git fetch --prune origin`.
4. Read latest `origin/main:TASKS.md` and this exact prompt.
5. Preserve all owner-local work byte-for-byte. Never reset --hard, clean, force checkout, rebase, auto-stash, discard, overwrite or force push.
6. If persistent checkout is unsafe, leave it untouched and use one clean TEMP worktree from exact latest `origin/main`:
   `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-MASTER`.
7. Never create a Desktop sibling clone/worktree.
8. Create master log before product edits:
   `.hiveai/codex-logs/M18_CPX004_R2_LIVE_PUBLISH_MASTER_CODEX_LOG.md`.
9. Never edit root `TASKS.md`; never write `.hiveai/audits/**`.

## Existing authority to reuse

Do not build a second publisher. Reuse and extend the accepted Content Pipeline:
- `content_pipeline/src/scrubbots_content_pipeline/provider.py`
- `one_command_publisher.py`
- `staging_pack_upload.py`
- `staging_manifest_publish.py`
- `production_promotion.py`
- `production_manifest_activation.py`
- `publish_report.py`

Also inspect current Factory Studio / release flow:
- `src/scrubbots_pixel_factory/studio_extensions.py`
- `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py`
- `campaign_builder.py`
- `game_publisher.py`

Do not weaken M11-M14 contracts.

## R2 adapter contract

Implement a provider-specific Cloudflare R2 adapter behind the existing provider-neutral interfaces.

Use R2 S3-compatible API and a maintained Python S3 client unless the repo already has a better accepted dependency. Region is `auto`.

Credentials must come only from process environment or an injected secure local secret resolver. Never commit, print, log, serialize, screenshot, include in evidence, or put into an APK any access key, secret key, API token, session token, signed credential or connection string.

If publisher credentials are absent, fail closed before remote mutation and report only:
`OWNER_R2_WRITE_CREDENTIAL_REQUIRED`

Do not report secret values, even in debug output.

## Physical namespace lock

The single bucket uses these disjoint physical prefixes:
- STAGING: `staging/`
- PRODUCTION: `production/`
- provider control state: `_control/`

Provider-neutral manifest `object_key` values remain unchanged. The adapter adds the environment prefix physically.

No direct production pack publication is allowed. Production objects arise only through the accepted staging→promotion path.

Family Test stable manifest location:
`production/manifests/current.json`

Family Test game read endpoints after a real production publish:
- manifest:
  `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev/production/manifests/current.json`
- object base:
  `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev/production`

## SB-CP07-003 — provider adapter

Implement exact-byte write/read/verify, conditional manifest write, staging→production promotion/copy, release-event read/append, and current-state fencing through the existing interfaces.

Normalize provider failures to existing `ProviderResultCategory`. Raw provider exception text must not enter persistent evidence.

Advertise only capabilities actually implemented. Do not add delete authority unless an accepted current contract genuinely requires it.

Add unit tests for missing credentials, stale precondition, same-key/different-bytes collision, hash mismatch, failed copy, failed readback, network/provider failure normalization and secret redaction.

## SB-CP07-004 — staging/production separation

Prove identical logical keys map to distinct STAGING and PRODUCTION physical keys.

Control objects under `_control/` must never be referenced by game manifests.

Cross-environment direct writes must fail closed.

## SB-CP07-005 — immutable/versioned naming

Pack objects are immutable:
- same key + same bytes/hash may be reused idempotently;
- same key + different bytes is a hard failure.

`manifests/current.json` is the stable current pointer required by the installed game. It may change only through existing conditional/CAS activation with strictly increasing `content_version`.

Preserve exact historical manifest bytes/hash in existing manifest-history authority. Do not replace that authority with a vendor-specific schema.

## SB-CP07-006 — live upload/download/hash round trip

Add deterministic unit tests plus an opt-in live R2 test.

Live integration may write only an isolated STAGING integration object, for example:
`staging/_integration/roundtrip/<sha256>.bin`

Re-read it and verify exact bytes, byte length and SHA-256.

The live test is idempotent. Existing exact bytes may be reused; mismatch is failure.

If credentials/network are unavailable, do not call it PASS.

Never mutate production for this child.

## SB-CP07-007 — cache/CDN metadata

Use role-specific HTTP metadata:
- immutable .scrubpack objects: long-lived immutable caching;
- `manifests/current.json`: rapid revalidation / no-cache style semantics;
- JSON manifest Content-Type: `application/json`;
- .scrubpack: `application/octet-stream` unless an accepted specific type already exists.

Do not assume `r2.dev` is the final production CDN. It is Family Test read delivery. A custom domain can replace the public base later without changing provider-neutral object keys.

## SB-CP07-008 — backup/export/migration

Add a read-only export operation that downloads the exact current production manifest and every referenced pack to a local destination.

Verify manifest parse, pack byte length and SHA-256 before PASS.

Produce a deterministic secret-free export receipt.

Missing/corrupt content must fail.

## SB-CP07-009 — least privilege

Document and enforce a publisher secret boundary scoped to this bucket and only the object operations actually required for upload/read/copy/conditional publication.

No account administration, DNS, billing, Worker management or unrelated Cloudflare authority.

No committed secret-bearing .env file. Blank variable-name templates are allowed only if repository policy permits.

Missing/malformed credentials fail closed before mutation.

Add secret-scan/redaction tests over logs, reports, repr/exception paths and tracked diff.

## SB-CP07-010 — provider isolation

No Cloudflare/R2/account/bucket/public-host/credential field may be added to:
- `scrubbots.content.manifest.v1`
- `scrubbots.scrubpack.manifest.v1`
- LevelData
- supply plan
- level metadata
- gameplay schemas

Cloudflare-specific imports and constants stay inside M18 infrastructure/operator integration code and tests/docs.

Existing provider-neutral M11-M14 tests must remain green without weakening.

## SB-CPX-004 — Factory Studio “Publish to ScrubBots”

Add the owner-facing handoff from Factory Studio / Pixel Art Factory to the canonical Content Pipeline.

Hard flow:
1. Input must already be owner-accepted and release-eligible. READY alone is insufficient.
2. Build exact deterministic .scrubpack(s) from canonical LevelData + exact solver-proven supply plan + supported metadata/preview.
3. Studio/UI must invoke the existing M14 one-command publisher. No direct cloud SDK calls from UI/controller code.
4. First show/emit a mutation-free dry-run containing exact content_version, level IDs/order, pack IDs/hashes/lengths, current Scrubbots main SHA, bucket name and public read base.
5. STAGING upload and authenticated readback/hash verification happen first.
6. Resolve fresh exact `Sekiph82/Scrubbots` `origin/main` in an isolated TEMP authority and run accepted CPX-002 Godot replay.
7. PRODUCTION promotion requires a separate explicit owner approval bound to exact manifest SHA + content_version.
8. This master prompt itself is NOT production approval.
9. On production success, emit a reproducible secret-free receipt containing:
   - exact Scrubbots main SHA replayed;
   - content_version;
   - manifest SHA;
   - production manifest object key;
   - public manifest URL;
   - public object base URL;
   - pack IDs/object keys/SHA/length;
   - release-state tip.
10. Never write directly to a phone.
11. Never write the remote publication into the Scrubbots game repository.
12. Never silently overwrite a live content version or production pack.
13. Provide a headless/operator equivalent so this path is testable without GUI clicking.

If there is no eligible owner-approved release batch, stop:
`AWAITING_OWNER_RELEASE_BATCH`

If production approval is absent after STAGING verification, stop:
`AWAITING_OWNER_PRODUCTION_PROMOTION`

Do not fabricate content or owner approval.

## Continuous execution

Execute all nine tasks in order without asking to continue between passing children.

For every child:
- implement only that child scope;
- create a distinct child section/log entry in the master log;
- run focused tests + prior Content Pipeline regressions;
- fix ordinary in-scope failures;
- commit implementation;
- commit log/evidence;
- fetch/prune and push normally to `main`;
- require clean worktree and 0/0 parity;
- continue immediately.

True blockers only:
- owner-work preservation ambiguity;
- required real R2 credential absent for live gate;
- no eligible owner-approved batch;
- no explicit exact owner production approval;
- an accepted M11-M14 contract cannot be preserved with the provider;
- required tests cannot be made green without weakening authority.

## Required final verification

Run:
- all new M18/CPX-004 focused tests;
- all M14 CP03 + CPX-002 regressions;
- M13/M12/M11 Content Platform regressions;
- relevant Factory Studio / Release Pool / CampaignBuilder tests;
- governance/tracker tests;
- safe unfiltered full pytest;
- compileall;
- JSON/schema parse checks;
- `git diff --check`;
- secret scan over tracked diff and generated logs.

A live/network test may be unavailable only if the correct final state remains pending/blocker. Never convert an unavailable live gate into PASS.

## Final master log state

Master log:
`.hiveai/codex-logs/M18_CPX004_R2_LIVE_PUBLISH_MASTER_CODEX_LOG.md`

End with exactly one truthful state:
- `AWAITING_GPT_M18_CPX004_STRICT_AUDIT`
- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`
- `AWAITING_OWNER_RELEASE_BATCH`
- `AWAITING_OWNER_PRODUCTION_PROMOTION`
- or a precise technical blocker.

Use `AWAITING_GPT_M18_CPX004_STRICT_AUDIT` only when every claimed implementation/live gate is backed by actual evidence.

Final response: return only the master log GitHub URL.
