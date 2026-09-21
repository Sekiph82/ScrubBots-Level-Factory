# SB-LFX-008-C001-R02 — Fully Expanded Canonical Request Remediation

Work only on:
`.hiveai/audits/SB-LFX-008-C001-R01_PRESET_SCHEMA_REAL_EXECUTION_AND_PROVENANCE_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-008-C001-R02_FULLY_EXPANDED_CANONICAL_REQUEST_REMEDIATION_CODEX_LOG.md`

Keep the current validated five-field operator preset shape if desired.

Before execution, resolve those fields into a real canonical `GenerationRequest`.

Persist the complete `GenerationRequest.canonical_dict()` as the preset execution's expanded canonical request, including:
- request schema/version;
- typed seed;
- generator_mode;
- style/theme;
- palette subset;
- generator options/defaults;
- all other canonical request fields.

Real Godot integration must compare the persisted expanded canonical request exactly with produced bundle:
`metadata.generation.request`.

Then update/delete the preset and prove the prior bundle/request remain unchanged and reproducible.

Do not add unsupported preset operations. No TASKS edit. Publish one R02 implementation SHA + one log-only SHA.
