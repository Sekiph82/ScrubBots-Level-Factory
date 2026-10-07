# M18 + CPX-004 R01 — CHATGPT STRICT RE-AUDIT V01

Date: 2026-10-07  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Audited main implementation: `7430740ba13f68fe159d5ef358a2f7e526f44ffa`  
Builder log publication: `b7888afdfa0c3838c9dd122f4a6a09cd008e89c3` + `91969af9075bdc2dd8bc0ec96aaf457952dfe0a1`  
Criteria: `.hiveai/audit-criteria/M18_CPX004_R2_R01_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R02**

R01 materially closes the two blocking provider defects from the prior audit:

- **A — release-ledger fail-closed: PASS**
- **B — exact production-object idempotency: PASS**

However **C — SB-CPX-004 owner-facing/service/headless publish handoff: FAIL**. The implementation contains a useful preflight adapter and M14 delegation helper, but the real default Release Pool path is broken and the owner-facing Studio/headless surface cannot actually execute the M14 publish transaction from its JSON/operator boundary.

M18 / CPX-004 is **not closed**. Live R2 proof also remains externally gated by missing secure writer credentials and an empty real owner-approved Release Pool.

## Independent source review

The implementation commit is a single fast-forward commit on top of the authorized base and changes exactly:

- `content_pipeline/src/scrubbots_content_pipeline/r2_provider.py`
- `scripts/scrubbots_publish_handoff.py`
- `level_factory/scripts/factory_core_launcher.py`
- `level_factory/scripts/factory_studio_release.gd`
- four focused test files

No root `TASKS.md` or `.hiveai/audits/**` builder write occurred.

## A — PASS: corrupt/unavailable release ledger now fails closed

Accepted:

1. `read_release_events()` now requires a usable provider client.
2. A confirmed missing ledger remains canonical empty history.
3. Existing malformed/noncanonical/unreplayable bytes raise `InvalidReleaseLedgerError` instead of becoming `()`.
4. Provider-unavailable/read-failure state raises `ReleaseLedgerUnavailableError`.
5. `append_release_event()` parses the exact current object snapshot and returns integrity failure on invalid existing bytes without PUT.
6. The new M14 first-publication adversarial regression proves local empty history plus corrupt remote history terminates at `RELEASE_HISTORY_PREFLIGHT` with zero staging mutation and unchanged corrupt bytes.

This closes prior finding F01.

## B — PASS: exact existing production pack is idempotent

Accepted:

1. Source STAGING bytes are read and verified against the expected SHA before promotion.
2. Existing exact PRODUCTION bytes/length/SHA return normalized SUCCESS without rewrite.
3. Existing different bytes remain a hard conflict.
4. Transient/uncertain target reads fail without mutation.
5. Conditional-create race recovery rereads and accepts only exact immutable bytes.
6. No delete authority was introduced.

This closes prior finding F02.

## C01 — BLOCKING: default live Release Pool import is broken

In `scripts/scrubbots_publish_handoff.py`, the default preflight path does:

`from .release_pool import release_entries`

But the module is imported by `factory_core_launcher.py` as top-level `scrubbots_publish_handoff` after adding `scripts/` to `sys.path`. There is no sibling `scripts/release_pool.py`; the canonical Release Pool module is:

`scrubbots_pixel_factory.supply_pipeline.release_pool`

Therefore a non-empty real preflight that does not inject `release_pool_reader` reaches an invalid relative import and is caught as generic `PREFLIGHT_REJECTED`.

The focused owner-accepted test does not expose this defect because it injects a synthetic `release_pool_reader`. The headless smoke also does not expose it because the real pool is empty and the call exits before the import.

### Required R02 fix

Use the canonical Release Pool authority directly and add a no-injection/default-path regression proving that the real import path resolves and only current owner-ACCEPT + READY + hash-bound Release Pool entries can proceed.

## C02 — BLOCKING: Studio/headless boundary has preflight only, not executable publish

The Studio surface adds only:

`Preflight Publish to ScrubBots`

There is no owner-facing STAGING publish action.

The launcher exposes `action == "run-m14"`, but its request comes from JSON. It passes:

`request.get("publisher_request")`

to `run_m14_handoff()`.

`run_m14_handoff()` requires that object to already be an in-memory typed `PublisherRunRequest`. A JSON request can only produce a dict, so the launcher/headless JSON path cannot satisfy that type requirement. The implementation comment explicitly says JSON clients can only preflight.

Therefore the implemented Studio/headless boundary cannot execute the publish transaction it claims to hand off. The actual M14 runner is callable only by direct Python code/tests with an injected typed request.

This does not satisfy the R01 requirement for an owner-facing `Publish to ScrubBots` handoff plus headless/operator equivalent.

### Required R02 fix

Implement a narrow trusted operator service that:

1. accepts only a reviewed immutable preflight identity/receipt;
2. revalidates current Release Pool membership and deterministic pack identity;
3. internally assembles the typed M14 `PublisherRunRequest` from canonical state;
4. exposes a real owner-facing STAGING publish action and equivalent headless action;
5. delegates all mutation to the existing M14 runner;
6. remains fail-closed without secure R2 writer credentials;
7. keeps PRODUCTION as a separate explicit exact approval step bound to manifest SHA + content_version.

Do not pass Python objects through JSON and do not bypass M14.

## C03 — current-main preflight identity is weaker than the accepted CPX-002 authority

The new preflight asks the operator to type `scrubbots_main_sha`.

Its local verifier checks only:

- canonical remote URL,
- branch name `main`,
- local `HEAD` SHA shape.

It does not prove the checkout is clean, detached TEMP authority, or exact current `origin/main`. The accepted CPX-002 R01 contract already has a stronger TEMP-only current-main authority boundary.

Production M14 replay remains protected, so this is not a production bypass. But the preflight must not label a manually entered/stale local SHA as the exact current ScrubBots main identity.

### Required R02 fix

Reuse the accepted CPX-002 authority resolver/check rather than duplicating a weaker verifier. The owner-facing preflight should display the resolved authority SHA; it should not rely on manually typing a purported current-main SHA.

## D — external live gates remain pending, correctly

No secure R2 writer credential was available. No real owner-approved Release Pool batch exists. No exact owner production promotion approval exists.

These remain truthful external gates:

- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`
- `AWAITING_OWNER_RELEASE_BATCH`
- production approval pending

Do not manufacture any of them for R02.

## E — regression status

Builder evidence:

- focused R2/M14/CPX: **28 passed**
- compileall: PASS
- JSON parse: PASS
- diff check: PASS
- secret scan: no credential value found
- full suite: **1691 passed, 20 skipped, 2 failed**

The two remaining failures were:

1. CPX-002 current-main integration lacked explicit `SCRUBBOTS_PROJECT` TEMP authority;
2. governance parser rejected the tracker Current Task spelling `M18/CPX-004 R01`.

The governance failure belongs to ChatGPT-owned tracker state, not builder product code. R02 must nevertheless finish with the governance suite green. CPX-002 must be rerun with a valid exact-current TEMP game authority rather than accepted as a skip/failure.

## R02 disposition

R02 is authorized only for:

1. canonical live Release Pool import/default-path proof;
2. executable owner-facing + headless STAGING handoff through internal typed M14 request assembly;
3. reuse of CPX-002 exact-current TEMP game authority for preflight identity;
4. missing/exact production-approval boundary tests;
5. full regression closure with valid TEMP ScrubBots authority.

Provider A/B fixes are retained and must not be redesigned.

## Final

**CHANGES_REQUIRED / R02**

Do not perform a real R2 write, fabricate a release batch, or bind the game APK to production yet.
