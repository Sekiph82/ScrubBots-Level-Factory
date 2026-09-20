# SB-LFX-017-C001 — Provider Cost / Credit Center Truthful Accounting — Strict Audit Criteria

Target:
`SB-LFX-017 — Build Provider Cost / Credit Center for truthful jobs/success/failure/consumed/remaining/cost-per-accepted accounting where reliable provider data exists. [EXTENSION]`

## Principle

Accounting displays only reliable recorded provider evidence. Unknown is a valid result. No estimated balance/cost may masquerade as fact.

## Required dimensions

Where supported by canonical provider/job records, derive:
- provider identity;
- job/generation count;
- success count;
- failure count;
- consumed credits/cost;
- remaining balance;
- cost-per-success;
- cost-per-owner-accepted artifact/level.

Every metric must expose its evidence source/scope/currency or credit unit.

## BLOCKERS

FAIL if:
- provider balance is guessed/scraped from UI;
- missing credits/cost shown as zero;
- cost-per-accepted divides by QA PASS instead of owner acceptance;
- metrics merge incompatible providers/currencies/credit units;
- manual/free source is assigned invented monetary cost;
- center makes network/provider calls merely to populate UI without explicit existing authorized connector contract;
- secrets/API keys are stored/logged;
- TASKS is edited.

## Evidence policy

Prefer existing durable provider execution/accounting records. If a provider does not expose reliable consumed/remaining values, show NOT AVAILABLE with reason.

Manual/procedural sources may be labeled NO EXTERNAL PROVIDER CHARGE only when that statement is structurally true; do not infer total infrastructure cost.

## UI

Provide Provider Cost / Credit Center with per-provider and selected-scope summaries, clear UNKNOWN/NOT AVAILABLE fields, and evidence timestamps/record identities where available.

## Real tests

Use committed/local deterministic accounting fixtures or existing canonical provider records without spending credits/network access. Prove:
- success/failure counts;
- consumed metric only when present;
- remaining unknown when absent;
- owner-accepted denominator correctness;
- mixed unit separation;
- no secrets;
- refresh reflects new records;
- no candidate/review mutation.

## PASS rule

PASS when the Cost Center is a read-only, evidence-backed accounting view that prefers UNKNOWN over invented financial precision.
