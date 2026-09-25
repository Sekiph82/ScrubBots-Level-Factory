# SB-LF07-005-C001-R03 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: SB-LF07-005-C001-R03 typed seed/parent mutation provenance on the authentic M03/M04/M05 path.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `7f4399f6eb25d7c4acb090bf83a951e364e8d18f`; tracked tree clean before this log; owner-untracked files preserved.
- Frozen SB-LF07-002/003 behavior and tests remain unchanged except compatibility wiring.

## Contracts read before edits

- R03 master/index, original SB-LF07-005 criteria/C001 audit, R01/R02 prompts/logs and strict re-audits.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, accepted M03 solver evidence, M04 difficulty/Challenge Score, M05 Unified QA/LevelData, and current M07 provenance/runner contracts.

## Frozen finding and R03 boundary

- R02 left production provenance on anonymous validation digests; the authentic bounded runner did not automatically preserve unique producer-native M03/M04/M05 references.
- R03 must construct typed references only from the exact authentic adapters and validation envelope, while preserving explicit root registration and missing-parent/cycle protections.

## Chronological implementation and verification

- Added `provenance_from_authentic_validation`, which accepts only the exact `AuthenticEvidenceAdapter` triplet and matching `ValidationEnvelope`, revalidates the adapter/envelope binding, and derives exactly one `TypedEvidenceReference` for each ordered stage `M03_SOLVER`, `M04_DIFFICULTY`, and `M05_QA`. Authentic provenance carries producer digests and no anonymous-only evidence digest.
- Extended `AuthenticTargetCandidate` to retain the authentic M03 adapter and require all three envelope records to equal the adapter records. Updated the authentic bounded runner to emit typed references automatically for every applied attempt.
- Preserved `MutationProvenance` root registration, missing-parent, duplicate-child, and cycle protections; the new constructor delegates to the existing immutable provenance object and does not alter those graph rules.
- Added an actual runner/provenance-path adversarial test covering unique stage references, producer-digest presence, stage swap, missing adapter, request/seed replay drift, and automatic runner emission.
- First test run exposed a pre-existing stage-target helper mismatch (`SafetyConstraintEvidence` required a string version while the helper supplied integer `1`); the new test used the accepted typed target contract directly so Task 005 did not silently broaden or alter Task 006 behavior.
- Second test run exposed the owner-source gate correctly stopping the authentic runner before attempts when source art is present without a passed source context; the test supplied an explicit passed context, as required by the runner contract.
- Third test run exposed the test passing `CandidateIdentity` instead of the required `MutationCandidate`; corrected the runner test to retain and pass the exact parent candidate.
- Focused result: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_004_revalidation.py tests/unit/test_sb_lf07_005_provenance.py` — 15 passed.
- Offline/network boundary: typed provenance uses accepted in-process producer objects and immutable canonical digests only; no runtime network or telemetry dependency added.
- Dependency/license/security: no dependency or license changes; malformed, missing, swapped, replayed, or digest-drifted producer evidence fails closed.
- Changed files: `src/scrubbots_pixel_factory/mutation_evidence.py`, `src/scrubbots_pixel_factory/mutation_targeting.py`, `src/scrubbots_pixel_factory/mutation_attempts.py`, package exports, `tests/unit/test_sb_lf07_004_revalidation.py`, `tests/unit/test_sb_lf07_005_provenance.py`, and this builder log.

## Publication checkpoints

- Implementation commit: `15c8e05ea45674e394183a20fe8c74c0d23f2ef1` (`Remediate SB-LF07-005 typed mutation provenance`), pushed to `origin/main`.
- Terminal log-only commit: `ad1da0cf36f237fb4bde1ac7ad45a4631c0cfee4`, pushed successfully.
- Final local HEAD and `origin/main` equality at the task checkpoint: `ad1da0cf36f237fb4bde1ac7ad45a4631c0cfee4`.
