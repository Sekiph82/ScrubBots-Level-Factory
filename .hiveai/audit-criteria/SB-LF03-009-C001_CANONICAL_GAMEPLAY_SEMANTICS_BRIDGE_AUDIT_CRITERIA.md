# SB-LF03-009-C001 - Canonical Gameplay Semantics Bridge - Strict Audit Criteria

Target:
`SB-LF03-009 - Reuse canonical reachability/routing semantics rather than importing another game's rules.`

## Mission-critical rule

This task must establish or prove the production path to the canonical `Sekiph82/Scrubbots` gameplay authority.

No Python reimplementation of:
- reachability;
- routing;
- target selection;
- slot placement;
- clearing;
- legal-action semantics;
- completion/deadlock logic.

## Canonical source

At preparation, main-game authority is:
`Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`.

Relevant sources include:
- ProofState;
- ProofKernel;
- SolvabilitySolver;
- production routing/access/targeting engines referenced by ProofKernel.

Resolve current main when executing.

## Bridge requirements

A production AVAILABLE bridge must:
- run the canonical main-game Godot project/headless authority, not scrape source to emulate it;
- verify exact checkout commit and exact required source bytes before use;
- leave the main-game checkout byte-identical;
- accept canonical LevelData/state input through a versioned request;
- validate LevelData bytes against state LevelIdentity where used;
- return canonical legal moves/state transitions/terminal or solver evidence through strict schemas;
- bind every response to request identity, authority SHA, bridge version and source-contract verification;
- capture bounded stdout/stderr/error evidence;
- be deterministic for identical input and authority.

A bridge script may live in Level Factory and execute against the main-game project if Godot supports a safe external script path. Do not write untracked bridge files into the verified main-game checkout.

If no safe execution mechanism can be established, the task remains truthfully UNAVAILABLE and must not fake closure.

## Real integration

PASS requires at least one real headless canonical integration fixture exercising actual ProofState/ProofKernel or SolvabilitySolver behavior.

Source-pattern inspection alone is insufficient.

The fixture must prove:
- a legal canonical move/result;
- an illegal/unavailable case;
- deterministic repeat;
- checkout immutability;
- authority mismatch fail-closed.

## PASS

PASS only when production gameplay semantics are actually consumed from the canonical main-game runtime, or the audit explicitly retains the task open. No second rules engine is acceptable.
