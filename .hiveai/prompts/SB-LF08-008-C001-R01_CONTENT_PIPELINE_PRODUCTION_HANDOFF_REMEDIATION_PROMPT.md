# SB-LF08-008-C001-R01 — Content Pipeline Handoff Remediation

Close the C001 findings for M08-008 only. Make READY depend on a strictly parsed M08-006 result, complete immutable request/result/metadata/artifact verification, and the canonical SB-LFX-006 latest-valid owner ACCEPT. Propagate explicit NOT_FACTORY_ACCEPTED, NOT_OWNER_ACCEPTED, UNAVAILABLE or ERROR for every missing, corrupt, stale or cross-candidate gate. Add deterministic rerun, cross-candidate, corrupt-review and generation-identity tests. Do not write future Content Pipeline state.
