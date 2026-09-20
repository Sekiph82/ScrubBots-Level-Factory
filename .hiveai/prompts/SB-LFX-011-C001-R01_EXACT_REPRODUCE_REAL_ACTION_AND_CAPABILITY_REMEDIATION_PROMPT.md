# SB-LFX-011-C001-R01 — Exact Reproduce Real Action + Capability Remediation

Work only on:
.hiveai/audits/SB-LFX-011-C001_EXACT_REPRODUCE_ACTION_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-011-C001_EXACT_REPRODUCE_CAPABILITY_GATED_ACTION_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-011-C001-R01_EXACT_REPRODUCE_REAL_ACTION_AND_CAPABILITY_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close MAJOR-001..003.

### Capability
Do not classify by origin string alone. EXACT_REPRODUCIBLE requires a validated canonical bundle/metadata, recorded generation request/config/typed seed/version, matching candidate/artwork/grid identities and an available canonical Reproduce path.
Tampered/incompatible metadata must become STALE/INVALID or NOT_REPRODUCIBLE.
OWNER_UPLOAD remains SOURCE_RETRIEVABLE_ONLY and is never described as regenerated.

### Real action
Add an enabled Exact Reproduce action only for EXACT_REPRODUCIBLE records.
Invoke the accepted canonical Factory Core Reproduce using recorded metadata, never current draft/preset values.
Require canonical MATCH, create separate governed reproduction output/evidence and preserve original bundle bytes.

### Real integration
Prove deterministic candidate -> enabled -> MATCH; draft/preset divergence does not affect replay; OWNER_UPLOAD is not falsely regenerated; unsupported/provider-like path is disabled; tampered metadata fails closed; original bytes remain unchanged.

Do not edit TASKS.md. Run full required regressions and publish one R01 terminal log-only commit.