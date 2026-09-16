# SB-LF06-005-C001 — Factory Studio Canonical Evidence / Metrics Panel — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity summary:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 1

## Audited builder chain

- Starting tracker HEAD: `8888e32084e766f02d446ee48e44ac3ba10af234`
- Implementation commit: `5ea045acf4ef0bae0a26055f5d26b8e3c2b4b03d`
- Terminal builder publication: `226bf06d0fc881a23660e313d23f2f33d8428aea`
- Terminal publication is log-only.

## Accepted implementation retained

The implementation correctly establishes a read-only Studio evidence panel over successful bundle `metadata.json` and preserves the intended semantic gates:

- canonical structural/art QA fields are displayed from metadata rather than recomputed in GDScript;
- request difficulty is labeled target/request context rather than measured difficulty;
- Solution remains unavailable pending M03;
- Difficulty analysis remains unavailable pending M04;
- Load/risk remains unavailable without a canonical model;
- `Structural QA ACCEPT != OWNER ACCEPT` remains explicit;
- Generate/Reproduce source switching, failed-action retention and preview/action/evidence truth separation are present;
- no solver, difficulty, load/risk, provider, Dashboard, Import, Library, Content Platform or main-game implementation was added;
- root `TASKS.md` was not modified by the builder.

Builder-reported verification is substantial: focused LF06-005 `4 passed`, retained focused regressions `109 passed`, full regression `703 passed`, compileall green, Godot headless boot green and the committed real Studio/Core integration green. These executions were not independently rerun in this audit environment; committed source/test semantics and GitHub commit topology were independently inspected.

## MAJOR finding

### F-SB-LF06-005-MAJOR-001 — Canonical evidence presentation gate is not fully fail-closed for malformed/unsupported metadata

The panel is presented to the operator as **canonical evidence**, so its narrow reader must reject the canonical identity/schema fields it actually relies on before entering `READY`.

Current `factory_studio_evidence_panel.gd` validates the root metadata schema/version and compares `metadata.artwork.candidate_id` with action evidence, but it does **not** validate the root `metadata.candidate_id` binding at all. Canonical Python `_validate_metadata()` explicitly requires `metadata.candidate_id == artwork.candidate_id`.

Therefore a metadata file whose root `candidate_id` is corrupted while `artwork.candidate_id` remains unchanged can still be presented by Studio as `READY` canonical evidence.

The same presentation gate reads and displays `generation.request.schema` and `generation.request.schema_version`, but does not require the canonical request schema or a supported request version before `READY`. Canonical Python defines `GENERATION_REQUEST_SCHEMA = "scrubbots-generation-request"` and supported schema versions explicitly. An unsupported nested request schema/version can therefore be displayed as canonical provenance rather than yielding `ERROR`.

There is also no type guard before calling `.duplicate()` on `quality.rejection_codes`. Malformed-but-parseable metadata can therefore take a runtime-error path instead of the prompt-required truthful panel `ERROR` path.

This is a closure issue because the authoritative prompt explicitly requires malformed/unsupported/mismatched metadata to yield `ERROR / no fabrication`, and requires schema/version assumptions used by Studio to be cross-language guarded.

### Required remediation

Retain the current panel architecture and add only the missing fail-closed presentation checks/tests:

1. require root `metadata.candidate_id` to match action evidence and `metadata.artwork.candidate_id`;
2. require `generation.request.schema` to equal canonical `GENERATION_REQUEST_SCHEMA`;
3. require request `schema_version` to be an exact supported canonical version, with a Python cross-language guard against `SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS`;
4. type-check presentation fields such as `quality.rejection_codes` before using array-only operations; malformed values must return a bounded failure reason and panel `ERROR`, not cause a script runtime error;
5. add real Godot integration mutations proving root-candidate mismatch, unsupported request schema/version, and malformed rejection-code type all fail to `ERROR` while retaining prior successful evidence;
6. do not duplicate the full Python bundle validator or recompute quality.

## NOTE

The implementation/publication discipline itself is clean. `5ea045a... -> 226bf06...` changes only the builder log, so no publication remediation is required.

## Closure decision

`SB-LF06-005` remains open. Do not start `SB-LF06-006` until the bounded R01 fail-closed metadata-presentation remediation passes independent audit.
