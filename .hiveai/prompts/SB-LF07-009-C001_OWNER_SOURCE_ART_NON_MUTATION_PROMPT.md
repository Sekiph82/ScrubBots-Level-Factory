# SB-LF07-009-C001 — Owner Source Art Non-Mutation — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_AUDIT_CRITERIA.md`

Implement SB-LF07-009 as a hard M07 owner-source immutability gate.

Reuse the accepted M05 OWNER_UPLOAD/source-library record. M07 may mutate candidate/gameplay configuration only, never immutable owner source bytes. Verify source SHA/length/dimensions before and after operations, reject derived-path aliasing, stale/corrupt records, and any silent recolor/resize/quantize/normalize attempt made to chase difficulty. Any future visual derivative must be a distinct explicit revision and may not masquerade as source.

Add source-alias, byte-mutation, corrupt-record, metadata/path trick, repeated-run and valid-candidate-only tests. Run all required gates and publish task logs/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md`
