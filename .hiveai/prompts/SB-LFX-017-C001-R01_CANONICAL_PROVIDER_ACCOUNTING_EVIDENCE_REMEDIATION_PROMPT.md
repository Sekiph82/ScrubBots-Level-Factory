# SB-LFX-017-C001-R01 — Canonical Provider Accounting Evidence Remediation

Work only on:
.hiveai/audits/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_TRUTHFUL_ACCOUNTING_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-017-C001-R01_CANONICAL_PROVIDER_ACCOUNTING_EVIDENCE_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close BLOCKER-001 and MAJOR-001..003.

### Canonical accounting evidence
Do not accept arbitrary financial/provider records from Studio requests.
Define or reuse a durable read-only provider accounting evidence contract. Product Cost Center must discover and validate those records internally.
The UI may select scope/filter only; it must not submit provider/status/consumed/remaining/owner-acceptance facts.
If a provider lacks reliable accounting records, show NOT AVAILABLE.

### Owner-accepted denominator
Use only canonically validated candidate-bound owner-review evidence from remediated LFX-006 when computing cost-per-owner-accepted.
If linkage cannot be proven, return NOT AVAILABLE.

### Metric evidence
For every displayed metric expose provider, unit/currency, scope, source/evidence record IDs and timestamp/as-of semantics when available.
Never pick remaining balance by incidental input ordering. Validate authoritative chronology or leave it NOT AVAILABLE.
Keep incompatible currencies/credit units separated.

### Real Studio integration
Build a real read-only Cost Center surface with refresh/scope/provider selection and metric rows.
Use deterministic local committed/test accounting evidence only, no network or credit spending.
Prove success/failure counts, consumed only when present, remaining unknown when absent, mixed-unit separation, owner-accepted denominator binding, refresh after new evidence, no secrets and zero candidate/review mutation.

Correct stale master-batch SHA metadata in R01 evidence. Do not edit TASKS.md.

Run full regressions and publish one R01 terminal log-only commit.