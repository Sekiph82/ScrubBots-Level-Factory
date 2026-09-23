# SB-LF03-004-C001-R01 — Provider / Transition Binding Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-004 — Implement deterministic baseline search when semantics available.`

Audit:
`.hiveai/audits/SB-LF03-004-C001_DETERMINISTIC_BASELINE_SEARCH_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-004-C001-R01_PROVIDER_AND_TRANSITION_BINDING_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Consume the remediated SB-LF03-003 query/result validator for every legal-provider response.

Before using moves, prove the result belongs to the exact request.

For AVAILABLE transition output, fail closed unless:
- child is a CompactSolverState;
- child authority exactly equals parent authority;
- transition output is otherwise structurally valid.

Do not infer gameplay semantics or child identity from local rules.

Malformed provider/transition output must return search ERROR, never SOLVED/PROVEN_UNSOLVABLE/INCONCLUSIVE based on untrusted data.

## Tests

Add cases where:
- provider returns a valid result bound to a different query/state;
- provider returns different authority;
- transition returns a child state under another authority.

All must fail closed.

Retain deterministic traversal, alternate-branch success, zero-move semantics and provider-unavailable behavior.

Run focused 004 + 003 + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
