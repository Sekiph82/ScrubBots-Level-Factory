# SB-LFX-017-C001 — Factory Studio Provider Cost / Credit Center

Builder log:
`.hiveai/codex-logs/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_CODEX_LOG.md`

Create log first. Work only on LFX-017.

Inspect existing provider execution/evidence contracts before designing accounting. Do not spend credits or make provider/network calls merely for this task.

Build a read-only Cost / Credit Center that derives only reliable recorded facts:
jobs, success/failure, consumed credits/cost, remaining balance, cost-per-success and cost-per-owner-accepted where each input is authoritative.

Unknown fields must be NOT AVAILABLE, not zero.

Keep provider/currency/credit units separated. QA PASS is not owner acceptance. Never store/log secrets.

Use deterministic local fixtures or existing committed provider records for tests. Prove mixed providers/units, missing balance, accepted denominator, refresh and zero side effects.

Do not edit TASKS.

Commit/push implementation then exactly one task-final builder-log-only commit and stop the implementation batch.
