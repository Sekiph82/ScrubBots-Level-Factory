# SB-LF07-010-C001 — Deterministic Mutation Regression Closure
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-010-C001`, final task in the authorized M07 batch.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `ce5f42c9f8b30d998d4ce1df9d73ef2b874779be`.
- Initial status: equal to origin; pre-existing untracked LF04 worktree directories and Godot UID files preserved and not staged.

## Required records and contracts read before edits

- Live `TASKS.md`, M07 master prompt/index, this task prompt and strict criteria.
- `AGENTS.md`, `GOVERNANCE.md`, and accepted SB-LF07-001..009 implementation/log evidence.
- Palette V3 contract and retained M03/M04/M05/M06 boundaries.

This log was created before SB-LF07-010 product implementation and tests.

## Planned implementation boundary

- Add a declarative, versioned, checksummed executable corpus covering the full M07 contract and genuine negative tamper cases.
- Prove repeated clean runs produce identical canonical digests/attempt sequences and parent/source/Pallette V3 invariants remain unchanged.
- Do not edit `TASKS.md` or audits and do not declare M07 PASS/CLOSED.

## Chronological implementation and verification

- 2026-09-25: Added `tests/fixtures/sb_lf07_mutation_regression_v1.json`, a versioned ten-contract M07 corpus. Its canonical payload checksum is `1476462748abb8a7bc33c4ccfb470542c2c1962e2bedfc53c71f720f5fea5d0b`.
- 2026-09-25: Added `tests/unit/test_sb_lf07_010_regression.py`. The regression tests exercise the real hardening and easing operators, M03/M04/M05 truth-chain eligibility, deterministic repeated mutation and bounded-attempt digests, provenance, targeting, efficiency telemetry exclusion, owner-source byte preservation, Palette V3 C01..C16/BG01, and negative request-digest tampering.
- 2026-09-25: The first focused command failed (`1 failed, 35 passed`) because the negative test attempted to retain a stale evidence digest after changing the request digest. The test was corrected to construct a re-digested tampered evidence record (`evidence_digest=None`); the failed command and correction are retained in this chronology.
- 2026-09-25: Focused command `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_001_mutation_interface.py tests/unit/test_sb_lf07_002_hardening.py tests/unit/test_sb_lf07_003_easing.py tests/unit/test_sb_lf07_004_revalidation.py tests/unit/test_sb_lf07_005_provenance.py tests/unit/test_sb_lf07_006_targeting.py tests/unit/test_sb_lf07_007_attempts.py tests/unit/test_sb_lf07_008_efficiency.py tests/unit/test_sb_lf07_009_owner_source.py tests/unit/test_sb_lf07_010_regression.py` passed: `36 passed`.
- 2026-09-25: Full command `python -m pytest -q -p no:cacheprovider` passed: `1021 passed, 2 skipped in 326.04s`. The two skips are the pre-existing explicit canonical ScrubBots checkout/bridge capability skips in SB-LF03-002 and SB-LF04-012; no new skip or xfail was introduced.
- 2026-09-25: `python -m compileall -q src tests` passed with exit code 0.
- 2026-09-25: `godot_console.exe --headless --editor --path level_factory --quit` passed with exit code 0 under Godot 4.7.2.
- 2026-09-25: `git diff --check` passed with exit code 0. `git diff --exit-code -- TASKS.md` passed with exit code 0; the root task ledger was not edited.
- 2026-09-25: The fixture pins canonical authority commit `edf672f61989d28fd1931917ab49b2d64cc416d6`, retains Palette V3, and exercises no size/color/difficulty proxy mutation. Owner-source bytes and dimensions remain unchanged. No audit file, prompt, or sibling repository was modified. No task was self-promoted to PASS or CLOSED.

## Publication checkpoints

- Implementation/evidence commit: `81d5a6d` (`test: add SB-LF07-010 deterministic regression corpus`).
- Terminal log-only commit: to be recorded after commit and push.
- Final local HEAD and `origin/main` equality: to be recorded after terminal log publication.
