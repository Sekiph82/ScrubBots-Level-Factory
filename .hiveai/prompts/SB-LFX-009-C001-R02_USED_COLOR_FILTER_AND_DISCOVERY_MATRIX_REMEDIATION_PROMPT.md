# SB-LFX-009-C001-R02 — Used-Color Filter + Discovery Matrix Remediation

Work only on:
`.hiveai/audits/SB-LFX-009-C001-R01_SEARCH_TRUTH_FILTERS_AND_SMART_COLLECTIONS_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_DERIVED_VIEW_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-009-C001-R02_USED_COLOR_FILTER_AND_DISCOVERY_MATRIX_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close the remaining narrow filter/runtime finding.

1. Make backend/UI used-color filtering internally consistent:
   - candidate records expose `used_color_count = len(used_colors)`;
   - validate it is a real derived canonical field;
   - expose a bounded optional Studio used-color-count filter.
   If you intentionally remove this filter instead, remove it consistently from backend and UI contract. Preferred path is to support it because canonical used colors already exist.
2. Extend real Search integration to prove:
   - Owner Accepted collection contains a valid accepted candidate before its review changes;
   - Owner Rejected reflects the later valid review;
   - Unused in Campaign returns explicit NOT AVAILABLE;
   - Ready for Production remains NOT AVAILABLE;
   - repeated identical query/filter runs return the same deterministic ordering;
   - combined used-color-count + another grounded filter works;
   - no mutation occurs.

Do not persist collection membership.

Run full regressions and publish one R02 implementation + one R02 terminal log-only commit. Do not edit TASKS.md.
