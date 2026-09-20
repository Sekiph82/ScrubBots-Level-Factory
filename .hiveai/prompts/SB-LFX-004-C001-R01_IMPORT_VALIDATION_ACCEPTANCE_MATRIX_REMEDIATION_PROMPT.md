# SB-LFX-004-C001-R01 — Import Validation Acceptance-Matrix Remediation

Work only on the findings in:

`.hiveai/audits/SB-LFX-004-C001_IMPORT_VALIDATION_WIZARD_STRICT_AUDIT.md`

Original criteria remain authoritative:
`.hiveai/audit-criteria/SB-LFX-004-C001_IMPORT_VALIDATION_WIZARD_CANONICAL_ANALYSIS_AUDIT_CRITERIA.md`

Create builder log BEFORE edits:

`.hiveai/codex-logs/SB-LFX-004-C001-R01_IMPORT_VALIDATION_ACCEPTANCE_MATRIX_REMEDIATION_CODEX_LOG.md`

## Mission

Retain the existing product implementation. Close MAJOR-001 only.

Add committed acceptance coverage proving the already-implemented fail-closed paths.

Required:
1. real Godot Import Validation scenario with a supported PNG containing semi-alpha or another canonical alpha-invalid condition;
2. prove canonical validation reports the alpha-contract failure / DERIVED_ARTIFACT_REQUIRED truth and does not silently normalize;
3. tamper a bounded OWNER_UPLOAD source record and/or stored source bytes and prove validation fails closed with no trusted validation result;
4. create existing immutable validation evidence, tamper/conflict with it, re-run validation and prove it is not silently overwritten/trusted;
5. prove source.png/source.json remain byte-identical across all failure paths;
6. add focused Python coverage for the same boundaries where useful.

Do not redesign the wizard or add LFX-005+ behavior.

Run focused tests, real Godot integration, retained LFX-002/003/004 tests, full pytest, compileall, headless boot, diff-check, TASKS diff empty.

Commit implementation/tests, then exactly one R01 log-only terminal commit. Do not edit TASKS.
