# SB-LF03-005-C001-R01 — State-Key Binding Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-005 — Add visited-state memoization/hashing.`

Audit:
`.hiveai/audits/SB-LF03-005-C001_CANONICAL_VISITED_STATE_MEMOIZATION_HASHING_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-005-C001-R01_STATE_KEY_BINDING_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Bind every opaque canonical key result back to the exact state supplied to `key(state)`.

Introduce a single validator/API that checks:
- result.state_digest == state.digest();
- result.authority == state.authority;
- provider id/version matches expected provider;
- evidence identity/disposition is consistent;
- AVAILABLE key evidence is verified;
- structural Factory digest is never silently used as canonical semantic key.

Update memo/evidence consumers to use this binding.

Do not implement `ProofState.canonical_key()` in Python.

## Tests

Add a negative fixture where provider is queried with state A but returns an otherwise valid result carrying state B's digest/key evidence. It must ERROR and must not alter visited/memo counts.

Retain duplicate collapse/distinct separation/determinism tests.

Run focused 005 + dependent evidence tests + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
