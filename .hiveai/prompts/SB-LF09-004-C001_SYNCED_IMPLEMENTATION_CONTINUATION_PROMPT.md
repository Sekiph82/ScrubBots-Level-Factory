# SB-LF09-004-C001 — Telemetry-Calibrated Difficulty Policy

Document role: CODEX IMPLEMENTATION CONTINUATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Canonical local root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Owner-approved policy:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/policies/SB_LF09_004_ANALYTICS_DATA_POLICY_V01.md

Strict audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_AUDIT_CRITERIA.md

Prior blocked attempt:
- no product implementation occurred;
- MAINT-GIT-HYGIENE-C002 synchronized canonical local `main`;
- do not repeat or resurrect the old maintenance sprint;
- continue SB-LF09-004 from current `origin/main`.

## Mandatory local ↔ GitHub main sync preflight

Do this before creating/editing product files:

1. Work only inside:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify exact repository:
   `Sekiph82/ScrubBots-Level-Factory`
3. Verify current branch:
   `main`
4. Run:
   - `git fetch origin --prune`
   - `git status --short --branch`
   - `git rev-parse HEAD`
   - `git rev-parse origin/main`
   - `git rev-list --left-right --count HEAD...origin/main`
   - `git stash list`
   - `git worktree list --porcelain`
5. If local main is clean and only behind, fast-forward with `git merge --ff-only origin/main`.
6. If legitimate tracked local work exists, preserve it non-destructively and use a normal merge only when safe.
7. Never use reset, rebase, stash, clean, force checkout, force push, or discard owner work.
8. Never create a branch, sibling Desktop clone, or Desktop worktree.
9. Existing generated `.uid` files or old prunable worktree registrations must not be deleted merely to make status clean.
10. Product implementation may begin only after local HEAD == origin/main and ahead/behind == 0/0, or after an explicitly documented safe reconciliation that ends at that state.
11. If safe synchronization is impossible, stop before product edits.

## Implementation

Implement SB-LF09-004 exactly under the approved V01 policy.

Build a versioned, deterministic, privacy-safe, advisory-only telemetry calibration subsystem that consumes gameplay aggregate evidence and compares it to accepted deterministic M04 difficulty truth.

Hard boundaries:
- M03/M04 remains canonical difficulty authority.
- No automatic Challenge Score/lane mutation.
- No live per-player personalization.
- No live/online learning.
- No LevelData/gameplay/source-art mutation.
- No core runtime internet dependency.
- No provider/network spend merely for tests.
- Analytics absent => UNAVAILABLE.
- <100 valid sessions => INSUFFICIENT_DATA.
- raw telemetry retention <=90 days.
- aggregate calibration retention <=12 months.
- no prohibited PII.

Implement:
1. closed/versioned approved telemetry session schema;
2. allowed-field validation;
3. retention-aware evidence selection;
4. duplicate/session identity protection;
5. deterministic aggregate evidence;
6. immutable advisory calibration report;
7. exact M04 analysis / Challenge Score / lane/version binding;
8. >=100-session recommendation threshold;
9. ADVISORY_READY / INSUFFICIENT_DATA / UNAVAILABLE / INCONCLUSIVE / ERROR dispositions;
10. deterministic observed-vs-predicted divergence;
11. offline/unavailable path preserving canonical M04 truth;
12. privacy/retention/threshold/tamper/mismatch/determinism tests.

Do not implement future production auto-calibration or promotion logic.

## Builder governance

- Do not edit root `TASKS.md`.
- Do not edit `.hiveai/audits/**`.
- Do not create another tracker/control plane.
- Create the builder log before product edits:
  `.hiveai/codex-logs/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_CODEX_LOG.md`
- Record the preflight and the fact that the prior attempt stopped before implementation.

## Verification

Run:
- focused SB-LF09-004 tests;
- retained SB-LF09-001/002/003;
- affected M03/M04/M05/M06/M07/M08/Palette regressions;
- full `python -m pytest -q -p no:cacheprovider`;
- `python -m compileall -q src tests`;
- Godot headless;
- `git diff --check`.

Commit implementation separately from terminal log publication.
Push directly to `main`.
Fetch again and prove local HEAD == origin/main and ahead/behind == 0/0.
Then stop for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_CODEX_LOG.md
