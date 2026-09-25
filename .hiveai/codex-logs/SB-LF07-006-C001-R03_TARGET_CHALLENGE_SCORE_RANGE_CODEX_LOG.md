# SB-LF07-006-C001-R03 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: SB-LF07-006-C001-R03 truthful typed Challenge Score targeting and safety-constraint availability.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `ad1da0cf36f237fb4bde1ac7ad45a4631c0cfee4`; tracked tree clean before this log; owner-untracked files preserved.
- Frozen SB-LF07-002/003 behavior and tests remain unchanged except compatibility wiring.

## Contracts read before edits

- R03 master/index, original SB-LF07-006 criteria/C001 audit, R01/R02 prompts/logs and strict re-audits.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, accepted M04 Challenge Score policy contract, M05 Unified QA, M07 authentic evidence/target contracts, and retained M03/M04/M05/M06/Palette V3 tests.

## Frozen finding and R03 boundary

- R02 derived policy identity from a candidate-specific producer digest and treated generic Unified QA ACCEPT as load/risk/retention truth.
- R03 must use the stable accepted M04 Challenge Score policy identity, bind candidate scores to authentic M04 evidence, and report absent load/risk/retention authority as unavailable/inconclusive rather than synthesizing PASS.

## Chronological implementation and verification

- Replaced candidate-specific M04 producer-digest targeting with the stable accepted M04 Challenge Score policy identity: Challenge Score schema/version plus `CHALLENGE_SCORE_POLICY_VERSION` (`DIFFICULTY_V1`). Candidate scores remain read only from the authentic M04 adapter record and are still range-checked.
- Confirmed no accepted repository producer currently supplies authoritative load, risk, or retention truth. `build_typed_target` now marks all three typed safety constraints false with explicit `UNAVAILABLE` availability; it never derives them from generic Unified QA ACCEPT. The existing selection path therefore returns `INCONCLUSIVE` and cannot MATCH while those constraints are unavailable.
- Updated policy comparison to use the same stable accepted policy identity for each candidate and target, independent of candidate-specific producer digest.
- Added an authentic target test proving stable policy identity, all three unavailable constraints, and no MATCH despite an in-range authentic M04 score and M05 ACCEPT.
- Focused result: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_006_targeting.py tests/unit/test_sb_lf07_005_provenance.py` — 15 passed.
- Affected M07 result: enumerated `tests/unit/test_sb_lf07_*` files and ran pytest — 69 passed.
- Offline/network boundary: targeting uses stable local policy constants and authentic in-process adapter objects; no cloud, telemetry, or runtime network dependency added.
- Dependency/license/security: no dependency or license changes; unavailable safety authority fails closed as INCONCLUSIVE and cannot be promoted to PASS/MATCH by generic QA acceptance.
- Changed files: `src/scrubbots_pixel_factory/mutation_targeting.py`, `tests/unit/test_sb_lf07_006_targeting.py`, and this builder log.

## Publication checkpoints

- Implementation commit: `5600c42efdcbca03b28f55a55216c4d0d3fcbfe1` (`Remediate SB-LF07-006 truthful target constraints`), pushed to `origin/main`.
- Terminal log-only commit: pending after this chronological entry is committed.
- Final local HEAD and `origin/main` equality: implementation push completed; final equality is recorded after the log-only push.
