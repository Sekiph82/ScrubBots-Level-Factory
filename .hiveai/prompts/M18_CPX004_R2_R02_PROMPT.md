# M18 + CPX-004 R02 — Live Release Pool + Executable Publish Handoff Closure

Document role: CODEX REMEDIATION MASTER PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/M18_CPX004_R2_R01_STRICT_REAUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/M18_CPX004_R2_R02_AUDIT_CRITERIA.md`

## FIRST TASK — non-destructive sync

1. Canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Record identity, branch, HEAD, origin, dirty state, stashes and worktrees.
3. Run `git fetch --prune origin`.
4. Read latest `origin/main:TASKS.md`, this prompt, R02 criteria and R01 strict audit.
5. Preserve owner-local work byte-for-byte. Never reset --hard, clean, rebase, auto-stash, restore/discard, overwrite, force push or force checkout.
6. If Desktop is unsafe, use one clean TEMP worktree:
   `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-R02`
   from exact latest `origin/main`.
7. Never edit root `TASKS.md`.
8. Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/M18_CPX004_R2_R02_CODEX_LOG.md`

## R02-1 — fix the real Release Pool service path

Current defect:
`scripts/scrubbots_publish_handoff.py` uses an invalid relative default import for `release_entries`.

Required:

- use the canonical `scrubbots_pixel_factory.supply_pipeline.release_pool.release_entries`;
- do not invent a second Release Pool;
- keep owner ACCEPT + READY + current immutable/hash-bound Release Pool semantics;
- add a default/no-injection regression proving the actual service path resolves;
- prove READY-only, stale review, stale pipeline/source identity cannot become publishable.

Do not weaken the accepted Release Pool implementation.

## R02-2 — make Publish to ScrubBots executable from Studio and headless/operator flow

Current defect:
Studio only exposes preflight. The launcher JSON `run-m14` route cannot supply an in-memory typed `PublisherRunRequest`.

Required architecture:

1. Keep preflight mutation-free.
2. Preflight must emit a deterministic reviewed identity/receipt bound to:
   - ordered candidate IDs;
   - content_version;
   - deterministic pack ID(s);
   - exact pack SHA/length;
   - exact current ScrubBots main authority SHA;
   - target bucket/public read base.
3. Add a real owner-facing action after successful preflight, such as:
   `Publish to STAGING`.
4. Add the equivalent headless/operator action using serializable request data.
5. The trusted Python operator/service layer must:
   - consume the exact reviewed preflight identity;
   - re-read/revalidate current Release Pool membership;
   - rebuild/revalidate deterministic pack bytes;
   - internally assemble the complete typed M14 `PublisherRunRequest`;
   - invoke the accepted `run_one_command_publisher`.
6. Do not serialize Python objects through JSON.
7. Do not call boto3/R2 from GDScript/UI.
8. Do not bypass M14 validation, release-history, staging upload/readback, replay or production gates.
9. Missing writer credentials must stop before remote mutation.
10. Retry must remain deterministic/idempotent and secret-free.

Implementation-only proof may use injected fake provider/fixtures. Do not fabricate real owner content.

## R02-3 — reuse CPX-002 exact-current game authority

Remove the weaker owner-entered/local-main authority claim.

Required:

- reuse the accepted CPX-002 TEMP-only current-main authority resolver/check;
- canonical remote required;
- TEMP authority required;
- clean exact current `origin/main` required;
- preflight displays the resolved SHA instead of trusting an owner-typed SHA;
- production still performs the authentic M14 current-main Godot replay.

Do not relax CPX-002.

## R02-4 — production remains a separate exact owner approval

STAGING success must never imply PRODUCTION.

Add/retain tests proving:

- missing production approval rejects;
- approval for wrong manifest SHA rejects;
- approval for wrong content_version rejects;
- exact approval fixture reaches the existing M14 production path;
- no real production write occurs in R02 without real external approval.

If an owner-facing production action is surfaced, it must clearly display and bind the exact staged manifest SHA + content_version and require a distinct explicit confirmation.

## R02-5 — regression closure

Run at minimum:

- new default Release Pool path tests;
- new Studio/headless executable-handoff parity tests;
- missing-credential zero-mutation tests;
- production approval mismatch/exact-match tests;
- R01 release-ledger and idempotent-promotion tests;
- CP07 tests;
- M11-M14 regressions;
- relevant Release Pool/CampaignBuilder/Factory Studio tests;
- governance/tracker tests;
- CPX-002 authentic current-main replay with a valid exact-current clean TEMP `Sekiph82/Scrubbots` authority;
- safe unfiltered full pytest;
- compileall;
- JSON/schema checks;
- `git diff --check`;
- tracked diff + builder-log secret scan.

Do not change tests merely to hide a real failure.

## External live gates

No secure R2 writer credential is currently supplied.
The real Release Pool may still be empty.
No exact real production approval is supplied.

Therefore it is valid for the final implementation state to retain:

- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`
- `AWAITING_OWNER_RELEASE_BATCH`
- `AWAITING_OWNER_PRODUCTION_PROMOTION`

Do not claim live publication PASS.

## Publication

Commit implementation separately from builder log.
Normal push only.
No force.

Final clean execution authority must be 0/0 with `origin/main`.

## Final state

If implementation/regressions are green while only external live gates remain, end the log:

`AWAITING_GPT_M18_CPX004_R02_STRICT_REAUDIT`

Final response:
return only the R02 builder log GitHub URL.
