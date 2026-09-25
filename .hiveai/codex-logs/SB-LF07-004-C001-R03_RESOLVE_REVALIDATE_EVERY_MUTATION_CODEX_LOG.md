# SB-LF07-004-C001-R03 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: SB-LF07-004-C001-R03 authentic producer-native identity binding.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting Level Factory HEAD and `origin/main`: `2d00a63e9fabb9893e3b3c03a38ac9a3215b2e41`; tracked tree clean; owner-untracked files preserved.
- Frozen SB-LF07-002/003 behavior and tests are out of scope except compatibility wiring.

## Contracts read before edits

- R03 master/index, original SB-LF07-004 criteria/C001 audit, R01/R02 prompts/logs and strict re-audits.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, accepted M03 solver evidence, M04 difficulty/Challenge Score, M05 Unified QA/LevelData and Palette V3 contracts.

## Frozen finding and R03 boundary

- R02 authentic-type adapters still relabel unrelated accepted producer objects as evidence for the mutation child.
- M03 must bind native solver identity/provenance; M04 must bind source/solver/authority/metrics/policy/child; M05 must bind exact LevelData/source identity and bytes.
- Adapter records may be constructed only after native checks; missing native provenance remains UNAVAILABLE/INCONCLUSIVE.
- Legacy synthetic revalidation remains fixture-only and cannot establish production eligibility.

## Chronological implementation and verification

- Added producer-native checks in `mutation_evidence.py` without weakening the frozen mutation contract. M03 now requires the accepted `SolverEvidenceReport` to carry the exact child payload level identity, source SHA, request digest, child state digest, provider identity/version, and canonical M03 authority. M04 now requires the accepted `DifficultyAnalysis` and `ChallengeScoreResult` to bind to the authentic M03 adapter, exact source, metrics digest, score digest, policy version, and mutation authority. M05 now requires exact accepted `LevelDataIdentity` bytes, source SHA, LevelData SHA, payload level identity, non-empty stage evidence, and one shared non-UNAVAILABLE stage authority.
- Preserved the distinction between an internal mutation candidate ID and the payload's accepted LevelData `level_id`; the adapter binds to the payload identity when present and falls back to the candidate ID only for payloads without that field.
- Added an adversarial authentic producer-chain test covering the positive path plus unrelated solver, stale difficulty source, and unrelated QA LevelData rejections. The test also verifies the authentic adapters reach the existing eligibility envelope without fabricating producer evidence.
- First focused run exposed the intended new positive-path mismatch: the test used the internal mutation candidate ID where the accepted LevelData identity used its payload level ID. Corrected the binding to use the exact child payload identity, then reran successfully.
- First affected-suite command used a PowerShell wildcard directly and produced `no tests ran`; corrected by enumerating target files with `rg --files` before invoking pytest.
- Focused result: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_004_revalidation.py` — 8 passed.
- Affected M07 result: enumerated `tests/unit/test_sb_lf07_*` files and ran pytest — 67 passed.
- Offline/network boundary: adapter code uses only accepted local producer objects and canonical identities; no runtime HTTP, telemetry, image service, or API-key dependency added.
- Dependency/license/security: no dependency or license changes; missing or stale native authority is rejected as a contract error and is not converted to a synthetic PASS.
- Changed files: `src/scrubbots_pixel_factory/mutation_evidence.py`, `tests/unit/test_sb_lf07_004_revalidation.py`, and this builder log.

## Publication checkpoints

- Implementation commit: `94d29ddf7a6df6d0f4ee9d005d52ebd2ddcb7c30` (`Remediate SB-LF07-004 authentic producer binding`), pushed to `origin/main`.
- Terminal log-only commit: `7f4399f6eb25d7c4acb090bf83a951e364e8d18f`, pushed successfully.
- Final local HEAD and `origin/main` equality at the task checkpoint: `7f4399f6eb25d7c4acb090bf83a951e364e8d18f`.
