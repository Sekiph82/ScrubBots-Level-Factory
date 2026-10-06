# SB-CP03-005-C001 — Verify Remote Object Integrity

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation:
`88d2d09e28e73e4d4f8c5d555efab2e60a809704`

## VERDICT

**CONDITIONAL / REVERIFY_AFTER_TRACKER_FIX**

### Product-scope result

**PASS**

Independent source review confirms that provider self-reported SUCCESS is insufficient.

For every uploaded STAGING pack the gate now:
1. verifies provider result identity/environment;
2. reads exact stored bytes through the read-only provider surface;
3. requires expected object key identity;
4. requires exact byte length;
5. recomputes SHA-256 locally;
6. requires byte-for-byte equality to the candidate/M12 archive bytes;
7. runs M12 `inspect_scrubpack()` directly on downloaded bytes;
8. requires pack ID/version/level membership/archive digest to match immutable build evidence.

Truncated, mutated, swapped, wrong-key, stale-digest and missing-integrity cases fail closed and keep `manifest_write_authorized=false`.

No real vendor adapter, credentials, production mutation or delete path was introduced.

### Why not CLOSED yet

The required cumulative/full-suite publication gate did not finish green because root `TASKS.md` declared unified denominator **247** while the parser counted **248** after owner-authorized `SB-CPX-004` was added.

This is not a CP03-005 product defect.

ChatGPT, the sole tracker writer, corrected the authoritative denominator and extension accounting in commit:
`67807bd54d6a31d29ddc8f672ca3f23a7f754a6a`

Required closure:
- rerun the exact governance test;
- rerun CP03-005 focused/cumulative regression;
- rerun safe full pytest;
- if green, CP03-005 becomes PASS/CLOSED and M14 may continue to CP03-006.

`SB-CP03-005 = CONDITIONAL / REVERIFY_AFTER_TRACKER_FIX`
