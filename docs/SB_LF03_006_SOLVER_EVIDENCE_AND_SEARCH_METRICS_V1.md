# SB-LF03-006 — Solver Evidence and Search Metrics

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

`solver_evidence.py` instruments the accepted baseline provider orchestration
and records only observed deterministic evidence: ordered canonical move path,
bounded structural state references, visited count, optional memo-hit count,
dead ends, maximum depth, branch observations, and DFS frontier peak.

Monotonic elapsed time is exposed only by `telemetry_dict()` and is excluded
from canonical bytes and digest. When provider execution is unavailable, the
report has no metrics rather than fabricated zero values. Fixture tests prove
repeat-deterministic evidence, timing exclusion, bounded references,
unavailable truth, and input immutability.
