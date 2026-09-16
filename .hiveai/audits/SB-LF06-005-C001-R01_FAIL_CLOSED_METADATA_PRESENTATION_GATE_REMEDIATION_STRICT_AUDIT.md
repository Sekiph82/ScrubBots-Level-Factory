# SB-LF06-005-C001-R01 — Fail-Closed Metadata Presentation Gate Remediation — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**PASS / CLOSED**

Severity summary:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

## Audited builder chain

- Starting tracker HEAD: `4de700eb32edc1a0e26bc2f11f29129a87a7b172`
- Remediation implementation commit: `b257d09764507f24fad840314e8afce6add4914b`
- Terminal builder publication: `1d8f0d47b4419134f26600313775d9d4e3cbf130`
- `b257d097... -> 1d8f0d47...` is log-only; product/test tree is frozen at the remediation implementation commit.

## Independent scope review

The remediation commit changes only:

- `.hiveai/codex-logs/SB-LF06-005-C001-R01_FAIL_CLOSED_METADATA_PRESENTATION_GATE_REMEDIATION_CODEX_LOG.md`;
- `level_factory/scripts/factory_studio_evidence_panel.gd`;
- `level_factory/tests/factory_studio_action_integration_suite.gd`;
- `tests/unit/test_sb_lf06_005_factory_studio_evidence_panel.py`;
- `tests/unit/test_sb_lf06_005_r01_fail_closed_metadata_gate.py`.

Root `TASKS.md`, canonical Python Factory Core semantics, provider/network code, solver/difficulty implementation, Dashboard, Import, Library, Content Platform, main-game and `SB-LF06-006+` product work are untouched by the builder.

## Closure of prior MAJOR finding

### F-SB-LF06-005-MAJOR-001 — CLOSED

The prior canonical-evidence fail-closed defect is remediated without duplicating the full Python bundle validator.

The Studio evidence panel now requires before `READY`:

1. root `metadata.candidate_id` is a non-empty string;
2. root `metadata.candidate_id`, `metadata.artwork.candidate_id` and successful action `candidate_id` all agree;
3. artwork dimensions are numeric integral values and match the successful action dimensions;
4. `generation.request.schema` equals canonical `scrubbots-generation-request`;
5. request schema version is an integral numeric representation and belongs to the supported canonical version set;
6. selected structural metrics consumed for presentation are numeric;
7. `quality.rejection_codes` is an array whose members are strings before array-only duplication/use.

The request schema literal and supported version list are protected by a Python cross-language test against `GENERATION_REQUEST_SCHEMA` and `SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS`, preventing silent Studio drift from canonical Python contracts.

The accepted semantic gates remain intact:

- Structural / Art QA values are read from canonical metadata only;
- request difficulty remains target/request context only;
- Solution remains unavailable pending M03;
- measured Difficulty analysis remains unavailable pending M04;
- load/risk remains unavailable without canonical models;
- `Structural QA ACCEPT != OWNER ACCEPT` remains explicit;
- action truth, artwork-preview truth and evidence-panel truth remain separate.

## Runtime regression evidence

The committed Godot integration suite now mutates real Generate metadata and requires `ERROR` plus prior-evidence retention for:

- root candidate mismatch;
- unsupported request schema;
- unsupported request version;
- wrong request-version type;
- malformed `quality.rejection_codes` type.

After each mutation the canonical metadata is restored. The suite then proves the Generate panel returns to `READY`, preserves the accepted failed-action retention path, performs real Reproduce `MATCH`, switches evidence to the reproduction bundle metadata, and retains accepted crisp-preview behavior.

This is executable runtime evidence, not grep-only acceptance. The new focused Python test also invokes the committed Godot integration suite.

## Builder-reported verification

Builder reports:

- focused R01 + retained LF06/LF01/LF00 set: `113 passed`;
- canonical request/result/quality/output/bundle set: `84 passed`;
- full regression: `707 passed`;
- compileall: PASS;
- Godot headless boot: exit 0;
- committed real Godot integration: PASS;
- `git diff --check`: PASS.

These executions were not independently rerun in the audit environment. The committed source/test semantics, exact changed-file scope and commit topology were independently inspected through GitHub.

## Publication discipline

Publication discipline is correct:

- implementation/equality checkpoint: `b257d09764507f24fad840314e8afce6add4914b`;
- terminal publication: `1d8f0d47b4419134f26600313775d9d4e3cbf130`;
- terminal publication changes only the matching builder log;
- no post-final product/test commit exists in the audited chain.

## NOTE

Godot JSON numeric parsing can surface canonical integer JSON numbers as integral numeric Variants. The presentation gate therefore accepts only `TYPE_INT` or `TYPE_FLOAT` values whose numeric value is exactly integral, while rejecting strings and non-integral numbers. The runtime regression explicitly covers a wrong-type string version. This is compatible with the presentation-reader boundary and is not a silent schema-version coercion.

## Closure decision

`SB-LF06-005-C001-R01` is **PASS / CLOSED**.

`SB-LF06-005` is eligible for tracker closure. The next Studio task may open only through ChatGPT-owned root `TASKS.md` advancement and a separately published authoritative prompt.
