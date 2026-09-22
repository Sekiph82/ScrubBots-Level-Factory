# SB-LF03-009 Canonical Gameplay Semantics Bridge V1

`CanonicalHeadlessBridge` is a strict external adapter. It verifies the
configured `Sekiph82/Scrubbots` checkout at the declared commit, compares the
working ProofState bytes with the committed source, validates the locked
ProofState source contract and required authority paths, and only then invokes
a caller-supplied runner outside the canonical checkout.

Requests bind bridge version, operation, compact-state digest, LevelData source
hash, payload hash, and canonical authority. A runner response must bind the
request digest, authority SHA, exact ProofState source hash, operation, schema,
and version. Request/response files live in a temporary external directory;
the canonical checkout is never written by this adapter.

This mirror has no configured canonical checkout or external runner in the
ordinary environment. Therefore the production adapter reports `UNAVAILABLE`
and does not fabricate legal moves, transitions, solver output, or gameplay
truth. Real invocation coverage is capability-gated by
`SCRUBBOTS_CANONICAL_CHECKOUT` and `SCRUBBOTS_CANONICAL_BRIDGE_RUNNER`.
