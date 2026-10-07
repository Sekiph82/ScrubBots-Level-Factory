# M18 + CPX-004 MASTER — STRICT AUDIT CRITERIA

Repository: `Sekiph82/ScrubBots-Level-Factory`

Audit the implementation independently. Builder prose alone is never sufficient.

## Governance
- Codex did not edit root `TASKS.md`.
- Codex did not write `.hiveai/audits/**`.
- Persistent owner-local work was preserved non-destructively.
- Execution HEAD was synchronized to current `origin/main`.
- No force push, reset --hard, clean, destructive checkout or owner-byte discard.
- Master log records exact base/implementation/log SHAs and final parity.

## SB-CP07-003 — Cloudflare R2 adapter
PASS only if:
- a real R2 adapter exists behind accepted provider-neutral interfaces;
- provider-specific code does not bypass the M14 publisher;
- R2 S3-compatible endpoint/region behavior is correct;
- credential absence fails before mutation;
- no secret value is committed, logged, serialized or exposed through exception/repr/report paths;
- provider errors normalize to accepted `ProviderResultCategory`;
- stale precondition, hash mismatch, failed copy/readback and idempotency cases are tested.

## SB-CP07-004 — environment separation
PASS only if:
- STAGING physical namespace is disjoint from PRODUCTION;
- accepted mapping is `staging/` and `production/` or a stricter documented equivalent;
- control state is outside manifest-visible content namespace;
- provider-neutral object keys remain unchanged in manifests;
- direct production publication through staging writer surfaces is impossible;
- tests prove no key alias/collision.

## SB-CP07-005 — naming / immutability
PASS only if:
- pack same-key/same-bytes is idempotent;
- same-key/different-bytes is rejected;
- production pack overwrite is impossible;
- `manifests/current.json` is guarded by exact prior state/CAS and monotonically increasing content_version;
- existing M13 history/version contracts remain green.

## SB-CP07-006 — round trip
PASS only if:
- local/unit exact-byte/hash round-trip tests exist;
- live test does not report PASS without real R2 credentials/network;
- if live PASS is claimed, evidence shows a real isolated STAGING object in `scrubbots-content-prod` was written, re-read and verified by byte length + SHA-256;
- no production content was mutated by the integration probe;
- no credential appears in evidence.

If live credentials were absent, the correct status is `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`, not task closure.

## SB-CP07-007 — cache/CDN
PASS only if:
- immutable packs receive long-lived immutable cache metadata;
- current manifest receives rapid-revalidation/no-cache semantics;
- object Content-Type is deterministic by role;
- implementation does not claim r2.dev is equivalent to final custom-domain CDN behavior.

## SB-CP07-008 — backup/export
PASS only if:
- current production manifest exact bytes are exported;
- all referenced packs are downloaded and byte/hash/length verified;
- corrupt/missing pack fails export;
- export performs no remote mutation;
- export receipt is deterministic and secret-free.

## SB-CP07-009 — least privilege
PASS only if:
- documented publisher permission scope is limited to `scrubbots-content-prod` object operations actually required by publication;
- no unrelated Cloudflare account/admin/DNS/billing/Worker authority is requested;
- no committed secret-bearing file/value exists;
- secret redaction/scanning tests cover logs, reports, repr and exception paths;
- deletion is not required/advertised without independent justification.

## SB-CP07-010 — schema isolation
PASS only if:
- no R2-specific field enters content manifest, scrubpack, LevelData, supply-plan, level-metadata or gameplay schemas;
- provider-neutral object keys remain portable;
- Cloudflare-specific imports/constants are confined to M18 infrastructure/operator code and tests/docs;
- M11-M14 tests remain green without weakening.

## SB-CPX-004 — Factory Studio Publish to ScrubBots
PASS only if:
- only owner-accepted release-eligible content can enter;
- READY alone cannot publish;
- Studio/controller invokes canonical M14 one-command publisher rather than direct cloud writes;
- preflight is mutation-free and binds exact content_version, levels/order, packs/hashes, current game SHA and target;
- staging upload + authenticated re-read/hash verification happen before production;
- current `Sekiph82/Scrubbots` main is freshly resolved in isolated TEMP authority and CPX-002 real Godot replay passes;
- production requires explicit owner approval bound to exact manifest SHA + content_version;
- master prompt text itself was not treated as approval;
- production current manifest is conditional/version-monotonic;
- production pack bytes cannot be silently replaced;
- no phone write and no Scrubbots game-repo write occurs;
- receipt is reproducible and contains no credential;
- headless/operator path exists and matches GUI/service semantics.

## Family Test public contract
If a real production publish is claimed, independently verify:
- public manifest URL:
  `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev/production/manifests/current.json`
- public object base:
  `https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev/production`
- unauthenticated manifest GET returns exact activated manifest bytes;
- each referenced pack is reachable at `<object-base>/<object_key>`;
- public bytes equal exact manifest/receipt SHA-256 and byte_length.

## Regression closure
Require:
- new M18/CPX-004 focused tests green;
- all M14 CP03 + CPX-002 regressions green;
- M13/M12/M11 Content Platform regressions green;
- relevant Factory Studio / Release Pool / CampaignBuilder tests green;
- governance tests green;
- safe unfiltered full pytest green unless an independently proven unrelated baseline defect exists;
- compileall green;
- JSON/schema parse checks green;
- `git diff --check` clean;
- secret scan clean.

## Truthful blocker rule
Do NOT award live production closure if any of these are absent:
- real R2 write credential available to the local publisher runtime;
- real owner-approved release batch;
- exact explicit owner production approval.

Allowed truthful pending states:
- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`
- `AWAITING_OWNER_RELEASE_BATCH`
- `AWAITING_OWNER_PRODUCTION_PROMOTION`
- precise technical blocker.

Only actual evidence can support `AWAITING_GPT_M18_CPX004_STRICT_AUDIT`.
