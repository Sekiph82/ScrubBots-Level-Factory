# SB-LFX-012-C001-R03 — True Restart + Surface-Path Revision Remediation

Work only on:
`.hiveai/audits/SB-LFX-012-C001-R02_EDITOR_BOUND_REVISION_HISTORY_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-012-C001-R03_TRUE_RESTART_AND_SURFACE_PATH_REVISION_REMEDIATION_CODEX_LOG.md`

Retain the accepted R02 revision schema, digest, canonical source baseline, fail-closed chain validation and immutable history semantics.

Close the remaining acceptance gap through the real Studio surface.

Required real integration:

1. Load a canonical candidate into the accepted manual editor.
2. Save R0/R1/R2 through `FactoryStudioRevisions`.
3. Invoke Compare through the revision surface and assert rendered/surface result.
4. Invoke Select / Undo through the revision surface; prove editor working cells actually become the selected revision.
5. Edit and save branch R3 while R2 remains immutable.
6. Invoke Restore Source through the revision surface and prove editor working grid returns to source without mutating source bytes/history.
7. Create real owner-review evidence for the candidate before/around revision transitions. Snapshot it and prove revision operations do not mutate or inherit owner acceptance/promotion truth.
8. Destroy/reinstantiate Studio, or run a true fresh-process restart, then reconstruct and use the same durable revision history.
9. After restart, corrupt a revision and prove fail-closed; restore the fixture only for test cleanup.
10. If production/promotion/export truth is unavailable, assert NOT AVAILABLE rather than fabricate it.

Do not bypass the key operator transitions with direct `revision-load` + direct editor calls in place of the UI surface under test.

Do not edit TASKS.md.

Publish one R03 implementation SHA and one terminal log-only SHA.
