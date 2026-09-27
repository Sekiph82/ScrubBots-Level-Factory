# SB-LF08-007-C001 — Strict Audit
Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Result

CHANGES_REQUIRED / CANONICAL OWNER-REVIEW AUTHORITY NOT ACTUALLY REUSED

## Scope and evidence

- Live audited SHA: `a0c7fc7198c3b5f9692b8f962336e076108b3c7c`.
- Product task commit: `a24ea08573b70d9ed2447462afb7ae7897115df6`; builder log: `132bb22855c3d87f5b96328f71d3b49e87e73d1f`.
- The existing SB-LFX-006 validator requires the review schema, version, deterministic review ID, candidate identity hash, candidate ID, artwork digest, grid hash, disposition, sequence and predecessor.
- Sources: [M08-007 criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/audit-criteria/SB-LF08-007-C001_OWNER_REVIEW_GATE_BEFORE_PUBLICATION_AUDIT_CRITERIA.md), [M08 implementation](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/src/scrubbots_pixel_factory/m08_batch.py), [SB-LFX-006 authority](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/src/scrubbots_pixel_factory/studio_extensions.py).

## Findings

1. `_review_chain()` is a permissive parallel parser, not the existing SB-LFX-006 review authority. It filters only by `candidate_id` and disposition, accepts missing `artwork_sha256` by defaulting it to the expected digest, and accepts reviews without sequence/predecessor fields by sorting `review_id`.
2. It does not require the canonical review schema/version, deterministic review ID, candidate identity hash, grid hash, exact sequence or predecessor chain. A synthetic partial mapping can therefore become the latest owner ACCEPT.
3. If a valid chain is accompanied by corrupt review evidence, `review_summary()` can still report `OWNER_ACCEPTED` while separately incrementing `INVALID_REVIEW_EVIDENCE`; the strict gate requires corrupt/tampered evidence to fail closed and not become latest truth.
4. The tests exercise the permissive adapter's own reduced mapping rather than the canonical SB-LFX-006 record validator and do not cover missing identity fields, sequence gaps, predecessor tamper or a valid ACCEPT plus corrupt evidence.

## Required remediation

Route M08 review projection through the existing SB-LFX-006 record/chain validator. Require exact candidate identity hash, artwork and grid identity, schema/version, deterministic review ID, contiguous sequence and predecessor chain. Any invalid record for the candidate must yield `INVALID_REVIEW_EVIDENCE` and block publication/handoff, even when an earlier record was ACCEPT. Add all listed negative tests without creating a second review store.

## Disposition

Not closed. Re-audit only after the complete authorized R01 batch.
