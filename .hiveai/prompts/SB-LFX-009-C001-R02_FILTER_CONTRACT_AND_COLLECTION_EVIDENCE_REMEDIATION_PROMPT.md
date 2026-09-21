# SB-LFX-009-C001-R02 — Filter Contract + Collection Evidence Remediation

Work only on:
`.hiveai/audits/SB-LFX-009-C001-R01_SEARCH_TRUTH_FILTERS_AND_SMART_COLLECTIONS_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-009-C001-R02_FILTER_CONTRACT_AND_COLLECTION_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Close the one remaining finding.

Make backend and UI filter contracts agree:
- either derive `used_color_count = len(used_colors)` for candidate records and expose a bounded Studio filter for it;
- or remove `used_color_count` from allowed filters if intentionally unsupported.

Real integration must additionally prove:
- Owner Accepted collection contains the accepted candidate before later review changes;
- Unused in Campaign is NOT AVAILABLE;
- repeated identical query/filter calls return exactly the same deterministic order.

Preserve current truthful Needs Review behavior and validated review-chain use. Do not persist membership. No TASKS edit.
