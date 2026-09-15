# SB-LF01-005-C001 — Independent Dimension Envelope Migration
Document role: CHATGPT STRICT AUDIT

Audit date: 2026-09-15
Repository: `Sekiph82/ScrubBots-Level-Factory`
Authoritative prompt: `.hiveai/prompts/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_PROMPT.md`
Starting tracker/base commit: `64b3d366423c518c3083a531a3589e415c8dea17`
Implementation commit: `739e100c4a5a188f6aa3d311e87069924c8ef3c8`
Builder-declared publication/equality commit: `a919adcea378debf1bed96e4875b8b9689503a4f`
Observed terminal builder commit: `acf4b46e6b603254b221f4335bb57ba321815850`
Builder log: `.hiveai/codex-logs/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_CODEX_LOG.md`

## 1. VERDICT

**CHANGES_REQUIRED**

The central product migration is correct and retained: current production dimensions use one canonical independent `20..59` envelope, rectangles are legal, current automatic dimension selection is deterministic and no longer difficulty-banded, and historical generation-request schema v1 remains separately replayable while current schema v2 uses the migrated semantics.

However the cycle is not eligible for closure because the versioned batch compatibility boundary is not fully fail-closed and the explicit workload-guidance acceptance item is not implemented. A publication-evidence defect is also present.

Finding summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 2

The implementation commit is retained. Remediation must be bounded; do not reopen the accepted dimension architecture.

## 2. ACCEPTED IMPLEMENTATION EVIDENCE

### 2.1 Canonical independent production envelope is real

`contracts/dimensions.py` defines a single `PRODUCTION_DIMENSION_ENVELOPE = DimensionEnvelope(20, 59)`.

`contracts/production.py` consumes that shared object for production width/height validation rather than redefining a competing policy.

### 2.2 Current difficulty no longer controls dimension legality

`contracts/difficulty.py` keeps legacy difficulty bands only behind explicit dimension/request schema version 1. Current schema version 2 returns the same global `20..59` band for every difficulty label.

For current schema v2, `select_dimensions()` derives width and height from separate stable domains (`dimensions.width`, `dimensions.height`) across the same global envelope, so changing difficulty does not change the selection range or mapping.

### 2.3 GenerationRequest migration is versioned rather than silently mutating v1

Current `GenerationRequest` schema is version 2. Supported request versions are v1 and v2. Validation and deterministic resolution pass the request schema version into the dimension contract.

Canonical serialization continues to preserve explicit `width`/`height` versus omitted `None` axes and serializes the request schema version.

### 2.4 Historical request/batch replay strategy is directionally correct

The CLI parser reconstructs recorded request schema versions explicitly. Historical request v1 can therefore retain the old difficulty-band dimension behavior while current v2 uses the global envelope.

Version-1 batch templates omit a request schema field and `_request_from_manifest()` intentionally defaults those templates to request schema v1. Current manifest v2 records request schema v2.

Focused integration evidence includes:

- historical v1 omitted-dimension accepted-bundle reproduce;
- v1 batch manifest resume/replay;
- current v2 automatic dimension persistence;
- current explicit rectangle generation/reproduce;
- deterministic batch/resume behavior.

### 2.5 Required production examples are covered

Focused tests cover every production difficulty against `20x20`, `20x59`, `59x20`, `59x59`, `23x47`, and `52x31`; reject 19/60 on either axis; exercise deterministic separate-axis automatic selection; and execute 59x59 generation.

### 2.6 Scope containment is good

The implementation changed the canonical Python dimension/request/CLI compatibility surface and directly affected tests. It did not modify root `TASKS.md`, provider code, Content Platform implementation, main-game code, or Factory Studio product functionality.

The product tree froze at implementation commit `739e100c...`; commits after it modify only the builder log.

## 3. FINDINGS

### F-SB-LF01-005-MAJOR-001 — Batch manifest schema version gate is not strict and accepts boolean `true` as legacy version 1

Severity: **MAJOR**

The migration introduces `_SUPPORTED_MANIFEST_VERSIONS = {1, 2}` and `_validate_manifest()` currently checks:

`value.get("version") not in _SUPPORTED_MANIFEST_VERSIONS`

without requiring `type(version) is int` and excluding booleans.

In Python, `True == 1` and `True in {1, 2}` is true. Therefore a JSON batch manifest containing:

`"version": true`

can enter the legacy-v1 branch instead of being rejected as malformed schema data. Because the same branch also decides whether `request_template.schema_version` is required, malformed version typing can alter compatibility parsing behavior.

This violates the prompt's version/corruption requirement and the intended fail-closed historical replay boundary. The request schema gate correctly uses strict integer typing; the batch manifest gate must meet the same standard.

Required remediation:

1. manifest version must be exact integer type, excluding bool;
2. only integer 1 and 2 are accepted;
3. add explicit regression tests for `true`, `false`, float/string/null, unsupported integer, and the valid v1/v2 cases;
4. preserve byte/replay behavior for valid historical v1 and current v2 manifests.

### F-SB-LF01-005-MINOR-002 — Required workload guidance was not implemented

Severity: **MINOR**

The task is explicitly `Support width/height selection within current engine/content envelope and workload guidance`, and the acceptance criteria require workload guidance to remain advisory and separate from legality/difficulty.

The implementation correctly migrates legality and tests 59x59, but no changed product/documentation/help surface supplies workload guidance. The implementation diff contains no new workload-guidance documentation or operator-facing help statement.

Required remediation:

- add concise, non-numeric advisory guidance stating that all `20..59` rectangles remain legal and that larger board area may require more processing/resources;
- explicitly state that guidance does not alter legality and is not difficulty;
- do not invent measured timing/memory thresholds;
- keep one canonical legality source; guidance must not create a second dimension policy;
- add a small regression/documentation assertion so the guidance cannot drift back into difficulty bands.

A documentation/help-level implementation is sufficient. Do not create an arbitrary workload scoring system merely to satisfy this finding.

### F-SB-LF01-005-MINOR-003 — Builder log's recorded equality checkpoint is not the true terminal builder commit

Severity: **MINOR**

The log records local `HEAD == origin/main == a919adce...` after publication and calls the builder-log closure ready for audit. But that equality record itself was later committed in `acf4b46e6b603254b221f4335bb57ba321815850` (`Record final publication equality checkpoint`).

Therefore `acf4b46e...`, not `a919adce...`, is the observed terminal builder commit.

This does not affect product behavior because `739e100c... -> acf4b46e...` changes only the builder log. It is nevertheless a truthfulness/publication-discipline defect under the prompt.

Required remediation:

- in the R01 log, avoid self-referential terminal-equality claims;
- record an observed pre-final equality checkpoint and identify the actual final log-only publication commit externally at handoff, or use another truthful non-self-referential publication pattern;
- do not rewrite the original C001 builder log.

## 4. NON-BLOCKING OBSERVATIONS

`GenerationResult` currently validates successful result dimensions through the current global dimension contract rather than the request's schema-specific dimension contract. Existing generators resolve dimensions from `GenerationRequest`, and historical replay tests demonstrate the accepted v1 path, so this is not a C001 closure blocker. Future contract-hardening work may consider binding omitted-axis results explicitly to `request.resolve_dimensions()` if that becomes part of a dedicated integrity task.

The existing difficulty-dependent color-count contract is outside this dimension-only cycle. It must not be treated as justification for reintroducing dimension/difficulty coupling.

## 5. REMEDIATION BOUNDARY

Retain all accepted C001 product implementation. R01 must not redesign the dimension model.

R01 scope is limited to:

1. strict batch manifest version typing/corruption tests;
2. non-binding workload guidance/documentation/help and a narrow regression assertion;
3. truthful R01 publication/log discipline.

Do not begin `SB-LF06-002`, Dashboard, Import, Library, solver, provider, Content Platform, or main-game work.

## 6. CLOSURE RULE

`SB-LF01-005` remains active and is not promoted to `[x]` until an independent ChatGPT audit passes R01.
