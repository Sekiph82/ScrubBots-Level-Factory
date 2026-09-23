# SB-LF03-005-C001-R02 — Strict State-Bound Memo API Remediation

Document role: CODEX REMEDIATION PROMPT

Target: SB-LF03-005 — Add visited-state memoization/hashing.

R01 re-audit:
.hiveai/audits/SB-LF03-005-C001-R01_STATE_KEY_BINDING_REMEDIATION_STRICT_REAUDIT.md

Create first:
.hiveai/codex-logs/SB-LF03-005-C001-R02_STRICT_STATE_BOUND_MEMO_API_REMEDIATION_CODEX_LOG.md

Do not edit TASKS.md.

## Finding to close

R01 added state-key validation but left the old public call shape memo.observe(StateKeyResult). That path skips exact state binding and can mutate visited/memo counts.

## Required remediation

Make state binding mandatory for every memo observation.
Preferred public API: memo.observe(state: CompactSolverState, result: StateKeyResult).

Requirements:
- no bare StateKeyResult success path;
- exact result.state_digest == state.digest();
- exact result.authority == state.authority;
- exact expected provider id/version;
- exact evidence identity;
- AVAILABLE requires verified evidence;
- Factory compact digest cannot be semantic key;
- validation failure cannot mutate visited count, memo-hit count or key set.

UNAVAILABLE and ERROR observations must also be state-bound when they enter the memo API.
Migrate every LF03 caller and test to the state-bound signature.
Do not implement ProofState.canonical_key() in Python.

## Tests

Add/retain FIRST_VISIT, MEMO_HIT, distinct key, provider mismatch, Factory-digest substitution, wrong-state result, bare result call rejected/fails closed, failed observation leaves counts unchanged, deterministic repeated sequence.

Run focused 005 plus 006/012 affected tests, retained LF03, full repository pytest, compileall, Godot headless, diff-check and TASKS no-diff.
Publish implementation + finalized R02 task log + terminal log-only commit.