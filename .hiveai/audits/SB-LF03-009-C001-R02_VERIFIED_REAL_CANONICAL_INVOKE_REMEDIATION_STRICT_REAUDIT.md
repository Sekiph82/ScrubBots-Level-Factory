# SB-LF03-009-C001-R02 — VERIFIED REAL CANONICAL INVOKE REMEDIATION — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited chain

- R02 implementation: `b15f0469cf2a96dae36f4d02f98a18625ff1dd07`
- R02 terminal builder-log commit: `2a91d8581fbdb872e211690f9f5270b6c9be2cdd`
- R02 master publication: `a5e16ffd445f4e242bb91c2566ad101e93eae984`
- canonical gameplay authority independently rechecked: `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Independent finding

## MAJOR-001 — LevelData source identity is still not cryptographically bound to LevelData content

R02 successfully establishes real canonical Godot execution from an independent clean exact-SHA checkout. The committed runner identity is pinned, the Godot executable is checked, and real canonical legal-move execution is proven. Later SB-LF03-012 R02 evidence also exercises `apply_placement` and `solve`.

However the R02 prompt explicitly required the supplied `level_data_source_sha256` to be consistent with the actual LevelData payload rather than merely transported alongside it.

The runner currently checks only:

`payload.level_data_source_sha256 == request.level_data_source_sha256`

It never computes SHA-256 from the LevelData source bytes/content that are reconstructed into `LevelData`.

Therefore a caller can change the LevelData cells/palette/dimensions and keep the same arbitrary hash string in both places; the bridge will accept the claimed identity. This leaves provenance identity detached from the gameplay input actually executed.

## Regression evidence

R02 builder evidence reports:
- real canonical Godot execution from an independent temporary exact-SHA clean checkout;
- final full pytest: `852 passed, 1 skipped, 1 warning`;
- focused LF06 integration: `10 passed`;
- focused declarative real-operation regression: `9 passed`;
- TASKS builder diff zero.

Passing tests are evidence, not a substitute for the contract checks above.

## Architecture / safety

The owner primary ScrubBots checkout remained untouched. No Python gameplay clone, WFC gameplay authority, provider-credit/network test dependency, or fabricated canonical result was accepted.

## Final disposition

**CHANGES_REQUIRED**

## Required next action

Bind the bridge to exact LevelData source bytes. Prefer carrying exact immutable LevelData source bytes (or an already accepted canonical serialization) in the request, compute SHA-256 from those bytes on the Python side and in/for the runner contract, parse/reconstruct gameplay LevelData from those same verified bytes, and reject any mismatch. Do not create a second incompatible LevelData serialization. Add a tamper test that changes one LevelData field while retaining the old hash and prove invoke fails closed.
