# M18 + CPX-004 R01 — R2 Fail-Closed Release State + Idempotent Promotion + Handoff Implementation

Document role: CODEX REMEDIATION MASTER PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Independent audit:
`.hiveai/audits/M18_CPX004_R2_LIVE_PUBLISH_MASTER_STRICT_AUDIT_V01.md`

Verdict:
`CHANGES_REQUIRED / R01`

## FIRST TASK — mandatory non-destructive sync

1. Canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Record repo identity, branch, HEAD, origin, dirty state, worktrees and stashes.
3. Run `git fetch --prune origin`.
4. Read latest `origin/main:TASKS.md`, this prompt, its audit criteria, the strict audit, and the current M18 builder log.
5. Preserve all legitimate owner-local work byte-for-byte. Never reset --hard, clean, force checkout, rebase, auto-stash, restore/discard, overwrite or force push.
6. If the persistent checkout is unsafe, leave it untouched and use one clean TEMP worktree from exact latest `origin/main`:
   `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-R01`
7. Never create a Desktop sibling clone/worktree.
8. Never edit root `TASKS.md`.
9. Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/M18_CPX004_R2_R01_CODEX_LOG.md`

## R01-1 — fail closed on corrupt/noncanonical release ledger

Current defect:
`CloudflareR2Provider.read_release_events()` returns `()` for both truly absent ledger and existing invalid/corrupt/non-replayable ledger.

Fix this without weakening M14.

Required behavior:
- truly missing `_control/release-events/current.json` => canonical empty history;
- transient provider read failure => fail closed;
- existing malformed JSON => fail closed;
- existing malformed event => fail closed;
- existing invalid chain/replay => fail closed;
- existing valid ledger => exact tuple;
- no existing invalid ledger may be overwritten or normalized into a new empty-first-publication ledger.

The accepted M14 `RELEASE_HISTORY_PREFLIGHT` must reject invalid/unavailable remote history before any pack/manifest mutation.

`append_release_event()` must preserve the same boundary. If the object exists but cannot be validated, return a normalized failure/conflict and perform zero mutation.

Add tests proving the exact first-publication hazard:
- local expected history is empty;
- remote `_control/release-events/current.json` exists but is corrupt;
- orchestrator/provider must stop;
- object bytes remain unchanged;
- no staging pack/manifest mutation occurs.

## R01-2 — idempotent exact production promotion

Current defect:
`promote_object()` safely refuses an existing production object, but it also refuses an exact same-byte object. That breaks the locked retry/idempotency contract.

Required behavior:
1. source STAGING object must exist and match exact expected SHA;
2. if PRODUCTION target absent, create it conditionally;
3. if PRODUCTION target already exists and exact bytes/length/SHA equal source + expected SHA, report normalized SUCCESS/idempotent satisfaction without rewriting;
4. if target exists with any different bytes/hash, return hard conflict/integrity failure and preserve bytes;
5. transient target read/write failure must not overwrite;
6. never add delete authority.

Add tests:
- absent destination create;
- exact existing destination idempotent success;
- different destination conflict with byte preservation;
- uncertain/transient read no mutation;
- retry after partial promotion succeeds without rewriting already-correct objects.

## R01-3 — implement SB-CPX-004 without fabricating live content

The previous builder stopped before handoff implementation because Release Pool had zero eligible owner-approved entries.

For R01, **implementation-only work is authorized even if the real Release Pool is still empty**.

Implement the owner-facing `Publish to ScrubBots` handoff and a headless/operator equivalent using deterministic fixtures/mocks for automated proof.

Hard rules:
- READY alone is insufficient; only owner-accepted + release-eligible canonical content may pass the real gate;
- UI/controller must not call boto3/R2 directly;
- it must compose the existing M14 one-command publisher and real provider adapter;
- dry-run/preflight must be mutation-free;
- preflight shows exact content_version, level IDs/order, pack IDs, hashes, lengths, current Scrubbots main SHA, bucket and public read base;
- exact canonical LevelData + solver-proven supply plan + supported metadata/preview are packaged into deterministic .scrubpack artifacts;
- real STAGING mutation remains impossible without secure R2 writer credentials;
- fresh current `Sekiph82/Scrubbots` main CPX-002 replay remains mandatory before production;
- real production promotion requires a separate explicit owner approval bound to exact manifest SHA + content_version;
- this R01 prompt is NOT that approval;
- no phone write;
- no Scrubbots game-repo write;
- no live overwrite;
- no executable remote payload;
- no secrets in receipt/log/UI.

Automated tests must cover:
- no eligible release entry;
- READY-but-not-owner-accepted rejection;
- owner-accepted fixture dry-run;
- missing credentials;
- staging-only success using injected fake provider;
- CPX-002 replay rejection;
- missing owner promotion approval;
- exact approval match;
- duplicate/retry/idempotent presentation;
- receipt secret scan;
- GUI/service and headless path semantics parity.

Do not manufacture a real owner-approved Level 11–50 batch.

## External live gates remain external

The owner has not supplied R2 write credentials to the publisher runtime.

Therefore:
- live CP07-006 may remain `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`;
- do not claim live R2 PASS;
- do not insert secret values into Git/logs.

If the real Release Pool remains empty after implementation:
`AWAITING_OWNER_RELEASE_BATCH` remains a truthful live-publication gate.

If a real batch later exists but exact production approval is absent:
`AWAITING_OWNER_PRODUCTION_PROMOTION`.

## Regression requirements

Run:
- new R01 fail-closed release-ledger tests;
- new R01 idempotent promotion tests;
- new CPX-004 service/UI/headless tests;
- all CP07 tests;
- all M14 CP03 + CPX-002 regressions;
- M13/M12/M11 Content Platform regressions;
- relevant Release Pool / CampaignBuilder / Factory Studio tests;
- governance/tracker tests;
- safe unfiltered full pytest;
- compileall;
- JSON/schema parse checks;
- `git diff --check`;
- secret scan over tracked diff and all generated logs.

Do not weaken existing tests just to make R01 green.

## Publication / logging

Commit implementation separately from builder log.
Push normally to `main`; no force.
Final worktree must be clean and 0/0 with `origin/main`.

The R01 builder log must record:
- exact base SHA;
- implementation SHA(s);
- changed files;
- exact tests/results;
- proof that corrupt remote ledger cannot become empty authority;
- proof exact existing production object is idempotent;
- proof CPX-004 code path exists without requiring fabricated live content;
- current external gate state.

## Final state

If R01 implementation and all non-live regressions pass, end the log with:

`AWAITING_GPT_M18_CPX004_R01_STRICT_REAUDIT`

This is allowed even if live publication is still externally blocked, provided the log clearly also records the current live gate such as `OWNER_R2_WRITE_CREDENTIAL_REQUIRED` and/or `AWAITING_OWNER_RELEASE_BATCH`.

Final response:
return only the R01 builder log GitHub URL.
