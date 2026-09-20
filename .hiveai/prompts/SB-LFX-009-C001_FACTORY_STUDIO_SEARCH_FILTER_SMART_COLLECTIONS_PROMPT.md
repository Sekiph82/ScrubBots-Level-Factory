# SB-LFX-009-C001 — Factory Studio Search / Filter / Smart Collections

Builder log:
`.hiveai/codex-logs/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_CODEX_LOG.md`

Create log first. Work only on LFX-009.

Build a derived discovery layer over committed canonical source/candidate/review records. Reuse Library/Candidate data readers; do not persist membership lists as truth.

Provide deterministic text search + filters for real fields and a small set of grounded smart collections.

If a requested collection requires unavailable solver/difficulty/campaign/publication truth, render it NOT AVAILABLE instead of guessing.

Test combined filters, deterministic ordering, refresh after record changes, Needs Review/Accepted/Rejected where grounded, unavailable collections, and zero mutation.

Do not implement readiness card/LFX-010+ or Content Platform. Do not edit TASKS.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
