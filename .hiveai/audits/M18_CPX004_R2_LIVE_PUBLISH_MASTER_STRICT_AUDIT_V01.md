# M18 + CPX-004 R2 MASTER — CHATGPT STRICT AUDIT V01

Date: 2026-10-07
Repository: `Sekiph82/ScrubBots-Level-Factory`
Audited main: `d03761b5b6fda29bdd4e08dec1e561dc7aa2cdfe`
Authorized base: `3d5dc46737e72f970fff989d40890eb217b8acf9`
Builder log: `.hiveai/codex-logs/M18_CPX004_R2_LIVE_PUBLISH_MASTER_CODEX_LOG.md`
Master criteria: `.hiveai/audit-criteria/M18_CPX004_R2_LIVE_PUBLISH_MASTER_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R01**

The builder's final stop state `AWAITING_OWNER_RELEASE_BATCH` is truthful for the live publication path, and the R2 adapter work is materially advanced. However, strict source review found one fail-open release-history defect and one retry/idempotency gap that must be repaired before any real R2 publication is authorized.

M18/CPX-004 is **not closed**.

## Scope independently inspected

The audited diff from the authorized base is 19 commits and does not modify root `TASKS.md` or `.hiveai/audits/**`.

Primary implementation reviewed:
- `content_pipeline/src/scrubbots_content_pipeline/r2_provider.py`
- `content_pipeline/src/scrubbots_content_pipeline/r2_export.py`
- `content_pipeline/pyproject.toml`
- R2 operator/security docs
- CP07 unit/integration tests
- the three narrowly updated CP00 boundary tests
- existing M14 one-command publisher release-history preflight and production gates

No neutral manifest/scrubpack/LevelData/supply/metadata schema was changed.

## Accepted findings

The following architecture choices are accepted in principle:
- fixed owner bucket `scrubbots-content-prod`;
- logical object keys remain provider-neutral;
- physical namespaces `staging/`, `production/`, and `_control/` are disjoint;
- direct pack writes are staging-only;
- production pack promotion is staging→production only;
- stable production current manifest is `production/manifests/current.json`;
- pack cache policy is long-lived immutable;
- current manifest cache policy is revalidation/no-cache;
- R2-specific code is isolated from gameplay/content schemas;
- no delete capability is advertised;
- no credential material is committed;
- production export is read-only against the provider;
- live R2 test correctly stayed pending because no write credential was available;
- CPX-004 did not fabricate an owner-approved batch or production approval.

The builder-reported final regression state is `1,696 passed, 6 skipped`, plus compileall and diff checks. This audit accepts that as builder evidence, not as a substitute for source inspection.

## F01 — BLOCKING: corrupt/noncanonical remote release ledger can be treated as an empty ledger

In `r2_provider.py`, `read_release_events()` returns `()` for both:
1. a genuinely absent `_control/release-events/current.json`, and
2. an existing but malformed/corrupt/non-replayable ledger.

That collapses two materially different states.

The accepted M14 orchestrator does:

`provider_ledger = tuple(request.provider.read_release_events())`

then accepts the preflight when:

`provider_ledger == request.release_events`

For the first publication, local `request.release_events` is legitimately empty. Therefore an existing corrupt remote ledger may be misread as the same clean-empty state.

The risk continues in `append_release_event()`: it separately reads the current object to obtain its ETag, then calls `read_release_events()`. If the existing object is corrupt, the parsed events become empty; for an expected initial sequence of zero, the code can conditionally overwrite that existing corrupt control ledger using `IfMatch`.

This violates the locked properties:
- append-only release-state authority;
- invalid history must fail closed;
- corrupted control state must never be silently normalized to pristine first-publication state.

### Required fix

Differentiate **ABSENT** from **INVALID/UNAVAILABLE**.

A safe narrow implementation is:
- missing object → return clean empty ledger;
- any existing object that cannot parse/replay canonically → raise/return a provider failure that causes M14 `RELEASE_HISTORY_PREFLIGHT` to reject;
- transient read failure → reject, never synthesize empty;
- `append_release_event()` must never overwrite an existing invalid ledger.

Add adversarial tests for malformed JSON, malformed event, invalid hash-chain/replay, transient GET failure, and the exact first-publication case where local history is empty but a corrupt remote control object already exists. Prove zero mutation.

## F02 — BLOCKING: exact existing production pack is not reusable idempotently during retry

The master contract states:
- same key + same bytes/hash may be reused idempotently;
- same key + different bytes must fail closed.

`promote_object()` currently reads the staging source and then always uses a production `PutObject IfNoneMatch="*"`.

If the production destination already contains the exact expected bytes from a prior partial/uncertain promotion, the second promotion returns a stale-precondition conflict instead of recognizing the exact immutable object as already satisfied.

This is safe against overwrite, but it is not the required idempotent retry behavior and can strand a valid retry after a partial publication attempt.

### Required fix

Before/after a conditional-create conflict:
- read the existing production destination;
- if exact bytes, byte length and SHA-256 equal the expected staging pack, return normalized SUCCESS/idempotent satisfaction;
- if any byte/hash differs, retain hard conflict/failure;
- never overwrite the destination.

Add focused tests for:
1. absent target → create success;
2. exact existing target → idempotent success, no mutation;
3. different existing target → hard conflict, bytes preserved;
4. transient read target → no overwrite.

## F03 — PENDING EXTERNAL GATE: no real R2 write credential / no live round trip

The live probe was skipped with `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`.

That is the correct truthful state. Therefore SB-CP07-006 cannot be closed as a live-provider proof yet.

No remediation should invent credentials or convert the skip to PASS.

## F04 — PENDING CONTENT GATE: SB-CPX-004 owner-facing handoff is not implemented

The clean Release Pool query returned zero eligible owner-approved release entries, and the builder stopped at `AWAITING_OWNER_RELEASE_BATCH`.

That stop is truthful and no production content was fabricated.

However, SB-CPX-004 itself remains open: no Factory Studio/UI/service/headless handoff implementation was added in this batch.

R01 is authorized to implement and test the handoff using deterministic fixtures/mocks for **implementation-only evidence**, while keeping every real remote mutation gated. A real staging/production publication still requires a genuine owner-approved release batch.

## R01 disposition

R01 must:
1. fix F01 release-ledger fail-open behavior;
2. fix F02 exact-object idempotent production promotion;
3. implement SB-CPX-004 owner-facing/service/headless handoff without fabricating a real owner release batch;
4. keep real R2 live integration pending until secure write credentials exist;
5. keep real publication pending until an actual owner-approved release batch exists;
6. keep production promotion pending until the owner explicitly approves the exact staged manifest SHA + content_version.

After R01, the strongest truthful handoff may still be:
- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`, or
- `AWAITING_OWNER_RELEASE_BATCH`,
depending on which external gate is first.

## Final

**CHANGES_REQUIRED / R01**

Do not bind the ScrubBots APK to a supposedly live production manifest yet.
