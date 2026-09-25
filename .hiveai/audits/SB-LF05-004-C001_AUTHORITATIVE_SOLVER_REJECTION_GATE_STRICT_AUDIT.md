# SB-LF05-004-C001 — Strict Audit

**VERDICT: CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Accepted: SOLVED/PROVEN_UNSOLVABLE/INCONCLUSIVE/UNAVAILABLE/ERROR and timeout semantics remain distinct.

Blocker: solver evidence has no bound requested level/source/request identity. Caller-supplied source/authority can relabel the same evidence for another level.

R01: use provenance-bearing M03 envelope binding exact source/state/request, authority/provider/version, evidence digest and budget digest; cross-level/cross-request/authority/budget mismatch => ERROR; add replay adversarials.
