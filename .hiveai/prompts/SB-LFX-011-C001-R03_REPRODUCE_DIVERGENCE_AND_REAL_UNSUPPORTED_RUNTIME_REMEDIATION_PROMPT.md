# SB-LFX-011-C001-R03 — Reproduce Divergence + Real Unsupported Runtime Remediation

Work only on:
`.hiveai/audits/SB-LFX-011-C001-R02_CAPABILITY_GATED_UI_AND_SOURCE_VERIFICATION_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-011-C001-R03_REPRODUCE_DIVERGENCE_AND_REAL_UNSUPPORTED_RUNTIME_REMEDIATION_CODEX_LOG.md`

Retain the accepted canonical Reproduce/MATCH implementation and R02 capability-gated UI.

Required closure:

1. Generate a deterministic canonical candidate.
2. Materially alter current Studio Generate draft values and/or save/apply a materially different preset after the candidate exists.
3. Invoke Exact Reproduce through the real capability-gated Studio surface, not a direct backend-only shortcut.
4. Prove replay still uses only the recorded canonical metadata/request and returns MATCH/byte-identical output despite current draft/preset divergence.
5. Use a real durable canonical record that is genuinely unsupported/non-replayable. Do not use a fabricated literal ID merely to exercise the error branch.
6. Prove that real unsupported/source-only/stale record keeps Exact Reproduce disabled and renders the exact capability reason.
7. Retain verified OWNER_UPLOAD positive/negative cases, tampered-metadata fail-closed behavior and original source/bundle immutability.

Do not invent provider replay authority. Do not edit TASKS.md.

Publish one R03 implementation SHA and one terminal log-only SHA.
