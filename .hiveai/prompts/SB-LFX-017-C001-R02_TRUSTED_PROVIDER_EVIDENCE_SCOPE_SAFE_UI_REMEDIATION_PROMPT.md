# SB-LFX-017-C001-R02 — Trusted Provider Evidence + Scope-Safe Cost Center UI Remediation

Work only on:
`.hiveai/audits/SB-LFX-017-C001-R01_CANONICAL_PROVIDER_ACCOUNTING_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_TRUTHFUL_ACCOUNTING_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-017-C001-R02_TRUSTED_PROVIDER_EVIDENCE_SCOPE_SAFE_UI_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close MAJOR-001..004.

### Trusted evidence source
Do not trust arbitrary well-shaped accounting JSON as financial authority.

Define/reuse one canonical local provider/job accounting evidence contract and trusted ingestion/writer path.

Each accounting record must bind to a verifiable underlying provider/job evidence reference when that provider exposes reliable data.

Derive provider/status/consumed/remaining from the trusted evidence rather than accepting duplicated unchecked facts where practical.

For providers without reliable cost/balance evidence, return NOT AVAILABLE.

Test-only fixtures must go through a dedicated canonical fixture/evidence writer, not direct FileAccess into product accounting directory.

### Scope-safe aggregation
Never merge different scopes under one labeled group.
Preferred key:
`(scope, provider, unit)`

or require an explicit scope before aggregation.

### Full UI
Render actual per-group metrics:
- provider;
- scope;
- unit/currency;
- jobs;
- success/failure;
- consumed;
- remaining;
- cost per success;
- cost per owner accepted;
- UNKNOWN/NOT AVAILABLE;
- as-of timestamp;
- evidence record IDs/references.

GDScript is presentation only.

### Runtime matrix
Prove:
1. mixed providers and units;
2. same provider/unit across two scopes remains separated;
3. consumed only where reliable;
4. missing remaining stays unknown;
5. validated owner-review denominator;
6. malformed/unbound accounting evidence rejected;
7. extra/secret-bearing record rejected;
8. first refresh then add a new trusted record then refresh reflects it;
9. candidate bundle + review evidence bytes unchanged;
10. no network/credit spend.

Run full regressions. One R02 implementation + terminal log-only commit. Do not edit TASKS.md.
