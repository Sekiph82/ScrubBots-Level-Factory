# SB-LFX-007-C001-R01 — Comparison Runtime + Review Binding + Evidence UI Remediation

Work only on:
`.hiveai/audits/SB-LFX-007-C001_SIDE_BY_SIDE_COMPARISON_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-007-C001_SIDE_BY_SIDE_CANDIDATE_COMPARISON_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-007-C001-R01_COMPARISON_RUNTIME_REVIEW_BINDING_AND_EVIDENCE_UI_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close MAJOR-001..003.

1. Consume only the canonically validated review evidence from the remediated LFX-006 review reader. Stale/tampered/mismatched review becomes unavailable/stale.
2. Render provenance/origin and canonical structural/QA evidence for every compared candidate, in addition to existing identity/dimensions/colors/review/unavailable metrics.
3. Add real Factory Studio comparison integration:
   - two distinct real candidates;
   - preview/artwork/grid identities correct;
   - differing metrics remain attached to the correct column;
   - owner review appears only on its bound candidate;
   - solver/difficulty/cost remain truthful;
   - refresh/reselection cannot cross-wire evidence;
   - candidate/review bytes unchanged;
   - no winner/rank/promotion side effect.

Do not add automatic selection or promotion.

Run focused/retained/full regressions. One R01 terminal log-only commit. No TASKS edit.
