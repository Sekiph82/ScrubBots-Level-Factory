# SB-LFX-011-C001-R02 — Capability-Gated UI + Source Verification Remediation

Work only on:
`.hiveai/audits/SB-LFX-011-C001-R01_EXACT_REPRODUCE_REAL_ACTION_AND_CAPABILITY_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-011-C001-R02_CAPABILITY_GATED_UI_AND_SOURCE_VERIFICATION_REMEDIATION_CODEX_LOG.md`

Retain the real canonical Reproduce/MATCH implementation.

Required fixes:
1. Exact Reproduce button disabled by default.
2. Enable only after a fresh capability result for the current selected identity is exactly `EXACT_REPRODUCIBLE`.
3. Any candidate/source ID edit invalidates prior capability and disables the button.
4. SOURCE_RETRIEVABLE_ONLY / NOT_REPRODUCIBLE / STALE/INVALID / ERROR keep button disabled with visible reason.
5. OWNER_UPLOAD capability must use canonical owner-source verification. Prefix-only IDs such as nonexistent `owner-upload-...` must not be SOURCE_RETRIEVABLE_ONLY.

Real integration must also:
- generate deterministic candidate;
- change current draft/preset values materially;
- prove Exact Reproduce still MATCHes recorded candidate;
- test a real verified OWNER_UPLOAD source as SOURCE_RETRIEVABLE_ONLY;
- test nonexistent/tampered OWNER_UPLOAD as invalid;
- test real unsupported/non-replayable record disabled.

No TASKS edit.
