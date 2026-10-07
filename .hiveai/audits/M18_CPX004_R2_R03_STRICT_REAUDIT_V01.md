# M18 + CPX-004 R03 — CHATGPT STRICT RE-AUDIT V01

Date: 2026-10-07
Repository: `Sekiph82/ScrubBots-Level-Factory`
Audited implementation: `864301396c771c5cd5a11acb6c3dcd81e19a830a`
Builder log: `.hiveai/codex-logs/M18_CPX004_R2_R03_CODEX_LOG.md`
Evidence head reviewed: `b7f2ce7294154d3eaca3467c4796b7052a086c9f`
Criteria: `.hiveai/audit-criteria/M18_CPX004_R2_R03_AUDIT_CRITERIA.md`

## VERDICT

**TECHNICAL PASS / EXTERNAL LIVE GATES PENDING**

R03 closes the remaining technical edge defects from R02. No R04 is required.

The M18 / SB-CPX-004 implementation boundary is technically closed. The only remaining R2 items are live operational gates that cannot be satisfied by fixtures:

- secure publisher-side R2 writer credentials;
- a genuine owner-approved Release Pool batch;
- first real STAGING upload/readback/hash proof;
- separate exact owner PRODUCTION approval bound to manifest SHA + content_version;
- first real PRODUCTION manifest/packs.

These live gates remain truthful and must not be marked PASS until real evidence exists.

## A — PASS: canonical Studio UTC timestamp

Accepted source behavior:

1. Factory Studio now calls `_current_utc_timestamp()` instead of forwarding Godot's timezone-less system string.
2. `_current_utc_timestamp()` obtains UTC from Godot and appends the explicit `Z` designator.
3. The trusted Python handoff independently passes `created_at_utc` through the accepted `normalize_created_at_utc()` scrubpack authority before pack assembly and review identity creation.
4. Timezone-less/ambiguous input fails closed as `PREFLIGHT_INPUT_INVALID`.
5. Explicit offsets normalize deterministically to whole-second UTC `Z`.
6. The reviewed identity binds the normalized timestamp; the STAGING flow re-runs preflight and deterministic pack construction, preserving the same canonical instant and bytes.
7. No hidden wall-clock read was added to the pack builder.

Permanent proof:

- CPX-004 focused suite: **13 passed**.
- Actual Godot Factory Studio runtime suite exercises the Release surface helper and verifies canonical `YYYY-MM-DDTHH:MM:SSZ`: **PASS**.

## B — PASS: production approval adversarial regressions

R03 adds permanent production-path regressions for:

- wrong owner approval manifest SHA;
- wrong owner approval content_version.

Both are required to reject before any PRODUCTION object promotion or manifest write.

Retained existing proof:

- missing explicit owner approval blocks;
- exact manifest SHA + exact content_version approval reaches the accepted M14 production path;
- STAGING-only CPX-004 remains explicitly `AWAITING_OWNER_PRODUCTION_PROMOTION`.

The production code itself did not require redesign.

## C — PASS: regression closure

Accepted final evidence:

- CPX-004 focused timestamp/STAGING: **13 passed**
- M14 approval/promotion/activation focused: **23 passed**
- R01 ledger/idempotency regression selection: **35 passed**
- M11-M14 + CP07 regression selection: **365 passed**
- governance/tracker selection: **204 passed**
- Factory Studio Godot runtime suite: **PASS**
- CPX-002 exact-current TEMP authority integration: **1 passed**
- Route A authentic verifier: **1 passed**
- final unfiltered pytest with verified TEMP ScrubBots authority: **1716 passed, 6 skipped, 0 failed**
- compileall: PASS
- JSON parse: 60 PASS
- JSON schema meta-validation: 9 PASS
- `git diff --check`: PASS
- secret-pattern scan: 0 matches
- builder root `TASKS.md` edits: 0
- builder `.hiveai/audits/**` edits: 0

The earlier full-suite failures were independently rerun after their environment gates were restored, then the complete suite was rerun successfully. They are not accepted merely as ignored failures.

## D — retained R01/R02 architecture

The following previously audited items remain accepted:

- corrupt/unavailable R2 release ledger fails closed;
- exact existing production pack promotion is idempotent without rewrite;
- provider-specific R2 implementation remains behind the provider boundary;
- staging and production namespaces remain separated;
- no delete authority was introduced;
- canonical Release Pool default path is used;
- owner ACCEPT + READY + current hash-bound candidate authority is required;
- Studio exposes a real `Publish to STAGING` action;
- headless/operator path is serializable;
- typed M14 request assembly happens only inside trusted Python;
- all remote mutation delegates to M14 `run_one_command_publisher`;
- UI/GDScript does not hold R2 credentials or call R2 directly;
- CPX-002 TEMP-only exact-current ScrubBots authority is reused;
- STAGING never implies PRODUCTION approval.

## E — external live gates

The following are intentionally **not** claimed as completed:

1. live R2 writer credential proof;
2. live STAGING upload/readback/hash round trip;
3. real owner-approved Release Pool publication batch;
4. real exact owner production promotion approval;
5. live PRODUCTION manifest/packs.

Those gates now require real operational inputs, not more implementation remediation.

## Sequencing disposition

Per owner sequencing, the next implementation task is:

`MAINT-FACTORY-STUDIO-LAUNCHER-C001`

The launcher is authorized now that the M18 / CPX-004 technical implementation has independently passed. It must PASS/CLOSE before M17 begins.

The launcher does not itself satisfy the external R2 live gates. It enables the owner's real Factory Studio workflow needed to process/accept the real pixel-art batch that will later supply those live gates.

## FINAL

**TECHNICAL PASS / EXTERNAL LIVE GATES PENDING**

**NO R04 REQUIRED.**

Next: Desktop Factory Studio Launcher, then real owner content/live publication evidence; M17 remains gated behind launcher closure.
