# SB-LFX-009-C001-R01 — Search Truth + Filters + Smart Collections Remediation

Work only on:
.hiveai/audits/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_DERIVED_VIEW_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-009-C001-R01_SEARCH_TRUTH_FILTERS_AND_SMART_COLLECTIONS_REMEDIATION_CODEX_LOG.md

Create log before edits.

## Mission

Close BLOCKER-001 and MAJOR-001..003.

### Smart-collection truth
- Needs Review must include only records with canonically grounded NEEDS_REVIEW semantics.
- Source-only records whose owner-review state is NOT AVAILABLE must NOT be converted into Needs Review.
- Owner Accepted / Owner Rejected must consume only canonically validated review evidence from the remediated LFX-006 reader.

### Real field filters
Expose bounded Studio controls for real canonical fields such as record type, origin, dimensions, owner-review disposition, QA/structural disposition and used-color count where present.
Do not expose unavailable domains as factual filters.

### Real integration
Create multiple real source/candidate/review records and prove combined field filters, text search, Needs Review / Accepted / Rejected / Imported Sources, Ready for Production and Unused in Campaign remaining NOT AVAILABLE, refresh after canonical changes, deterministic ordering and zero mutation.

Do not persist collection membership. Do not edit TASKS.
Run focused/retained/full regressions and publish one R01 terminal log-only commit.