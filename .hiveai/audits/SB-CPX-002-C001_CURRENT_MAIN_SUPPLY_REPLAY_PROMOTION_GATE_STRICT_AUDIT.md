# SB-CPX-002-C001 — Current-Main Supply Replay Promotion Gate

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation:
`bffe95ed47c3d5daf9a6ff270cd29837150af2a0`

## VERDICT

**CHANGES_REQUIRED / R01 — PRODUCT SEMANTICS RETAINED**

### Product result

The implemented gate itself is strong and source review confirms:
- exact verified STAGING manifest/pack bytes are required;
- CPX-001 solver identity, LevelData/supply-plan digests, FIFO columns and level binding are rechecked;
- the current-game result must report `SOLVED`, replay success, zero active/unresolved remainder and exhausted supply;
- exact current `Sekiph82/Scrubbots` repository/main commit and authority-source hashes are captured and drift-fenced;
- the host adapter refuses non-TEMP authority roots and requires clean `HEAD == origin/main`;
- no production mutation occurs in this child.

The final authentic builder run used isolated TEMP authority at ScrubBots main `2fd60ae69055c6c26c1f5f1b9d3869c743093786`, Godot `4.7.2.stable.official.ed1daf0bf`, and passed the real current-main integration.

### Strict audit blocker

The child criteria and M14 master invariant explicitly require **isolated TEMP game authority only, never implicit owner Desktop game checkout**.

The builder chronology records an earlier end-to-end attempt where `SCRUBBOTS_PROJECT` was omitted and the existing Factory bridge selected the owner Desktop `ScrubBots` checkout. That result correctly failed the authority-SHA gate and was discarded, but the protected checkout was nevertheless selected/accessed during this child execution.

A later clean run does not erase that process-boundary violation. No product-semantic redesign is required, but closure needs fresh evidence proving the CPX-002 path cannot silently fall back to an owner Desktop game checkout.

### R01 required

R01 must:
1. add/verify a fail-closed explicit-authority guard for the CPX-002 integration path so an omitted authority cannot fall back to Desktop;
2. create a fresh isolated TEMP ScrubBots authority from current `origin/main`;
3. explicitly bind every Factory/solver/current-main invocation to that TEMP authority before any replay/build step;
4. run the authentic Godot integration from scratch with no owner Desktop game path selected;
5. rerun focused, cumulative and unfiltered regressions;
6. publish separate implementation/evidence commits if code changes are required.

CP03-008..012 are not reopened unless R01 changes the accepted CPX-002 receipt semantics.

`SB-CPX-002 = CHANGES_REQUIRED / R01`
