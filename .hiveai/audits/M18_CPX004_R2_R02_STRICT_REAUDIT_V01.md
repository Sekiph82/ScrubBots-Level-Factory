# M18 + CPX-004 R02 — CHATGPT STRICT RE-AUDIT V01

Date: 2026-10-07
Repository: `Sekiph82/ScrubBots-Level-Factory`
Audited implementation: `896114374c487801f8e416a43f0c126ff05fdca1`
Builder evidence: `.hiveai/codex-logs/M18_CPX004_R2_R02_CODEX_LOG.md`
Final evidence head reviewed: `1da6e2cf027c713914c9f3542e67cae51969c5c5`
Criteria: `.hiveai/audit-criteria/M18_CPX004_R2_R02_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R03**

R02 closes the substantive R01 handoff architecture defects:

- A — canonical default Release Pool authority: **PASS**
- B — executable Studio + serializable headless STAGING handoff: **PASS**
- C — CPX-002 exact-current TEMP game authority reuse: **PASS**
- D — production remains separate from STAGING: **PASS in source architecture, regression evidence incomplete**
- E — regression closure: **PASS**

One real owner-facing runtime defect remains in the Studio timestamp path, and the exact wrong-manifest/wrong-content-version approval regressions requested by R02 were not added. R03 is intentionally narrow.

## Scope independently inspected

The implementation commit is one fast-forward commit over the authorized R02 base and changes only:

- `level_factory/scripts/factory_core_launcher.py`
- `level_factory/scripts/factory_studio_release.gd`
- `scripts/scrubbots_publish_handoff.py`
- `tests/unit/test_sb_cpx_004_scrubbots_publish.py`

Subsequent commits `2b2b569`, `10773a9`, and `1da6e2c` are log/evidence-only.

## A — PASS: canonical Release Pool default path

Accepted:

1. `publish_preflight()` now resolves the canonical `scrubbots_pixel_factory.supply_pipeline.release_pool.release_entries` service by default.
2. The canonical `release_entries()` authority itself revalidates latest owner ACCEPT, immutable entry digest, pipeline evidence hash, candidate identity, and bound artifact hashes.
3. The handoff performs an additional READY/pipeline identity shape check.
4. A no-injection regression verifies the actual import/service path.
5. READY-only and stale pipeline identity fixtures fail closed.

## B — PASS: executable Studio/headless STAGING handoff

Accepted:

1. Studio now exposes a distinct `Publish to STAGING` action enabled only after successful preflight.
2. The serializable launcher action is `publish-staging`; no in-memory Python object is expected over JSON.
3. `publish_to_staging()` re-runs preflight, requires exact reviewed identity equality, checks credentials before assembly, rebuilds pack bytes, rechecks Release Pool and game authority, internally assembles a typed M14 `PublisherRunRequest`, and delegates mutation to `run_one_command_publisher`.
4. GDScript does not import/call boto3/R2 directly.
5. Missing credentials are proven zero-mutation.
6. The real M14 in-memory STAGING orchestrator path is exercised in focused tests.
7. STAGING success reports `AWAITING_OWNER_PRODUCTION_PROMOTION` rather than implying PRODUCTION.

## C — PASS: exact-current TEMP ScrubBots authority

Accepted:

1. The owner-entered SHA field was removed from the Studio surface.
2. The handoff reuses `resolve_explicit_temp_game_authority()` plus `_authority_snapshot()` from the accepted CPX-002 adapter.
3. That boundary requires TEMP location, canonical remote, detached checkout, clean status, and `HEAD == origin/main`.
4. R02 created a fresh TEMP authority at exact ScrubBots main `19a39876572506bcb1df33aaf339c409f60f5eeb`.
5. Authentic CPX-002 Godot integration passed: **1 passed**.

## D — PASS architecture / incomplete explicit regression

The existing M14 production path remains separate and fail-closed:

- STAGING-only R02 request assembly never creates ProductionRunInputs.
- `OwnerPromotionApproval` is validated against exact staged manifest SHA, exact content_version and production target before promotion.
- approval is rechecked again at the activation boundary.
- existing M14 production tests prove missing approval blocks and an exact approval can traverse the production path.

However the R02 prompt explicitly required retained/added regressions for:

- wrong manifest SHA approval rejects;
- wrong content_version approval rejects.

Those exact adversarial regression cases are not present in the R02 changed test set and were not located in the existing production-promotion tests. Source logic is correct, but the requested permanent regression proof is incomplete.

R03 must add these two narrow tests without redesigning production code unless a test exposes a real defect.

## E — PASS: regression closure

Builder evidence accepted:

- CPX-004 focused suite: **10 passed**
- authentic CPX-002 integration: **1 passed**
- full suite: **1710 passed, 6 skipped, 0 failed**
- compileall: PASS
- 60 JSON parse checks: PASS
- git diff check: PASS
- secret scan: PASS
- root `TASKS.md` untouched by builder
- `.hiveai/audits/**` untouched by builder
- final R02 execution worktree and game authority reported clean/current

## F01 — BLOCKING: actual Studio UTC timestamp is not a valid scrubpack timestamp

`factory_studio_release.gd` currently does:

`Time.get_datetime_string_from_system(true, false)`

and sends that value directly as `created_at_utc`.

Godot 4.7 documents that this method returns:

`YYYY-MM-DDTHH:MM:SS`

even when `utc=true`; the `utc` flag changes the represented time to UTC but does not append a timezone suffix.

The accepted scrubpack contract explicitly rejects timezone-less values. The permanent M12 builder test includes:

`"2026-10-05T10:00:00"`

in the invalid timestamp set.

Therefore the real Studio button can produce a value that reaches `build_accepted_factory_output_pack()` and is rejected before a scrubpack is built. The R02 Python tests use a synthetic value ending in `Z`, so they do not exercise the actual GDScript timestamp boundary.

Official Godot 4.7 Time documentation:
`https://docs.godotengine.org/en/4.7/classes/class_time.html`

### Required R03 fix

Use a canonical timezone-explicit UTC instant across the real Studio boundary. Prefer one authority for normalization:

- Studio may append the explicit UTC designator when using the UTC system call; and/or
- the trusted Python service may normalize/validate through the already accepted scrubpack timestamp authority before binding the reviewed identity.

Requirements:

1. reviewed identity must contain canonical whole-second UTC;
2. STAGING rebuild must use the exact same canonical value;
3. timezone-less/ambiguous inputs must fail closed;
4. add a regression covering the actual Studio-produced timestamp shape, not only a hand-authored Python fixture.

## R03 disposition

R03 is authorized only for:

1. canonical Studio `created_at_utc` boundary fix;
2. actual Studio-to-service timestamp regression;
3. wrong manifest-SHA owner approval regression;
4. wrong content_version owner approval regression;
5. focused + full regression confirmation.

Do not redesign the accepted R01/R02 provider, Release Pool, authority, or STAGING architecture.

## External gates remain external

No secure live R2 writer credentials were supplied during R02.
No genuine owner Release Pool batch was published.
No exact real production approval was supplied.

These remain truthful after R03:

- `OWNER_R2_WRITE_CREDENTIAL_REQUIRED`
- `AWAITING_OWNER_RELEASE_BATCH`
- `AWAITING_OWNER_PRODUCTION_PROMOTION`

## Final

**CHANGES_REQUIRED / R03**

R03 should be a small closure, not another architecture cycle.
