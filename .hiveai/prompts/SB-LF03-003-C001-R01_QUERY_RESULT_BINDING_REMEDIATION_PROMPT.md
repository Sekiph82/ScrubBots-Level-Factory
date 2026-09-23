# SB-LF03-003-C001-R01 — Query / Result Binding Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-003 — Define legal-move-provider interface.`

Audit:
`.hiveai/audits/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-003-C001-R01_QUERY_RESULT_BINDING_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Retain the accepted provider architecture and fix only the missing mandatory query/result binding.

Implement one authoritative validation path proving a returned `LegalMoveResult` belongs to the exact `LegalMoveQuery` it answers.

Validate at minimum:
- exact query digest;
- exact state digest;
- exact authority;
- exact provider id/version;
- capability provider/authority consistency;
- disposition/capability consistency;
- AVAILABLE verification evidence;
- move kind/order/duplicates;
- every move column within the queried state's column_count.

A syntactically valid result constructed for another query/state must fail closed.

Do not derive legal moves in Python.
Do not add transitions/search/gameplay mechanics.

## Tests

Add negative tests for:
- wrong query digest;
- wrong state digest;
- wrong provider id/version;
- wrong authority;
- AVAILABLE result with mismatched capability;
- validly typed move result from another state/query.

Retain unavailable canonical behavior and all prior tests.

Run focused 003 + retained LF03 + full pytest + compileall + Godot headless + diff-check + TASKS no-diff.

Publish implementation + finalized R01 task log + terminal log-only commit.
