# SB-LFX-017-C001-R02 — Authoritative Accounting Source + Full UI Remediation

Work only on:
`.hiveai/audits/SB-LFX-017-C001-R01_CANONICAL_PROVIDER_ACCOUNTING_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-017-C001-R02_AUTHORITATIVE_ACCOUNTING_SOURCE_AND_FULL_UI_REMEDIATION_CODEX_LOG.md`

Do not treat manually dropped JSON as financial authority.

First inspect existing provider/job execution records.

If reliable consumed/remaining/cost facts already exist:
- derive accounting directly from those immutable records;
- bind provider run/job ID + execution evidence identity/hash + metric source + unit + timestamp.

If reliable provider accounting facts do NOT exist:
- product Cost Center must truthfully report those metrics NOT AVAILABLE;
- do not manufacture a new free-standing financial source merely to make tests pass.

Owner-accepted denominator uses only validated candidate-bound review evidence.

Studio must render real per-provider/unit rows with:
- scope;
- jobs/success/failure;
- consumed;
- remaining;
- cost per success;
- cost per owner accepted;
- UNKNOWN/NOT AVAILABLE;
- evidence record IDs;
- as-of timestamp.

Real integration must prove refresh after new authoritative evidence, malformed/secret-bearing evidence rejection, mixed-unit separation, unknown handling, candidate/review byte immutability, and zero network/credit spending.

No TASKS edit.
