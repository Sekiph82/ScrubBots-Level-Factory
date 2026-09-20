# SB-LFX-011-C001-R02 — Capability-Gated UI + OWNER_UPLOAD Validation Remediation

Work only on:
`.hiveai/audits/SB-LFX-011-C001-R01_EXACT_REPRODUCE_REAL_ACTION_AND_CAPABILITY_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-011-C001_EXACT_REPRODUCE_CAPABILITY_GATED_ACTION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-011-C001-R02_CAPABILITY_GATED_UI_AND_OWNER_SOURCE_VALIDATION_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close the remaining blocker + two majors without redesigning canonical Reproduce.

### Capability-gated UI
- keep a real reference to the Exact Reproduce button;
- disabled by default;
- any candidate-ID change invalidates previous capability and disables the button;
- enable only after a fresh capability result is EXACT_REPRODUCIBLE for the current ID;
- SOURCE_RETRIEVABLE_ONLY / NOT_REPRODUCIBLE / STALE/INVALID / ERROR keep it disabled with reason.

### OWNER_UPLOAD truth
Never infer retrievability from an `owner-upload-` prefix.
Resolve through canonical OWNER_UPLOAD verification:
- real verified source -> SOURCE_RETRIEVABLE_ONLY;
- missing/tampered source -> STALE/INVALID or NOT_REPRODUCIBLE.

### Runtime matrix
Extend real Godot integration:
1. deterministic candidate capability enabled;
2. materially alter current draft controls and/or preset values;
3. Exact Reproduce still MATCHes recorded bundle;
4. real OWNER_UPLOAD source reports SOURCE_RETRIEVABLE_ONLY and button disabled;
5. missing/tampered owner source not retrievable;
6. unsupported/non-replayable candidate/path disabled;
7. candidate-ID change disables stale previous capability;
8. original bytes unchanged.

Run full regressions. One R02 implementation + one terminal log-only commit. Do not edit TASKS.md.
