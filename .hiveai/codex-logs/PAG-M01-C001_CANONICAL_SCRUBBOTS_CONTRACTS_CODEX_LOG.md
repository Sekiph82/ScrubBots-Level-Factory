# PAG-M01-C001 — Canonical SCRUBBOTS Contracts
Document role: CODEX BUILDER LOG

## Cycle authority and starting evidence

- Implementation repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
- Authoritative prompt, read directly from GitHub:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_PROMPT.md`
- Previous independent strict audit:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_STRICT_AUDIT.md`
- Pinned contract commit: `Sekiph82/Scrubbots@b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`
- Pinned palette:
  `https://github.com/Sekiph82/Scrubbots/blob/b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd/data/palettes/scrubbots_palette_v2.json`
- Pinned rules:
  `https://github.com/Sekiph82/Scrubbots/blob/b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd/tasks.md`
- Start timestamp: `2026-09-08T21:02:07.4784967+03:00`

The canonical local mirror is
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`. Repository
identity is `Sekiph82/ScrubBots-Level-Factory`; origin is
`https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch is `main`.
The initial status was dirty only because of a pre-existing local edit to
`.hiveai/PROJECT.json`, changing its `repository` value from the short GitHub
owner/name to the full authorized URL. That edit is preserved, unstaged, and
outside this cycle's product scope.

Safe synchronization was performed only on this mirror:

1. `git fetch origin main` reported `HEAD...origin/main = 0 7`.
2. `git merge --ff-only origin/main` fast-forwarded from
   `f7d6c4b23e82cbf3d78396a46321f3f42ae33070` to
   `82c29c71f007371bc58059432b1e9678a0e1291d`.
3. After sync, local HEAD equaled `origin/main` at
   `82c29c71f007371bc58059432b1e9678a0e1291d`; the only dirty path remained
   the preserved `.hiveai/PROJECT.json` edit.

The separate `C:\Users\sekip\Desktop\ScrubBots` checkout was not inspected,
edited, committed, or pushed. No reset, rebase, clean, force-push, or discard
operation was used.

## Mandatory reads and contract preflight

Read completely from the authorized Level Factory checkout:

- `.hiveai/PROJECT.json`
- `.hiveai/RULES.md`
- `.hiveai/STATE.json`
- `.hiveai/HANDOFF.md`
- `tasks.md`
- `AGENTS.md`
- `GOVERNANCE.md`
- `.hiveai/audits/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_STRICT_AUDIT.md`
- `reference/audits/README.md`
- `reference/audits/scrubbots/coordination/sessions/META-C005/CHATGPT_AUDIT_V01.md`
- this C001 prompt directly from GitHub

The pinned palette JSON was read directly from the pinned GitHub URL. The
pinned main-game `tasks.md` contract sections were read directly from GitHub.
The current main-game `main` HEAD was queried from GitHub and is exactly
`b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`, matching the pinned contract
commit. The current task source confirms unchanged EASY/MEDIUM/HARD/VERY_HARD
dimension bands, rectangular legality, C01..C16 palette membership, BG01
`#202533` exclusion, and actual-used-color bands EASY 3..5, MEDIUM 6..7,
HARD 8..9, VERY_HARD 10..12. No contract drift was found.

The active M01 scope is PAG-0101..PAG-0133 only. M00 is closed by the cited
audit. PAG-M02 is not started. No task, H!veAI state, handoff, cycle-index,
event, prompt, prior log, or audit file will be modified.

## Implementation plan

Add only the generator-independent M01 contract layer:

- vendored machine-readable canonical palette data under `data/palette/`;
- immutable validated palette API with C-ID/RGB/HEX lookup and BG01 rejection;
- strict production difficulty enum and independent width/height validation;
- narrow SHA-256/domain-separated deterministic selection helpers for legal
  dimensions and palette subsets, without M02 `GenerationRequest` or RNG;
- actual-used-color counting/validation and explicit subset validation;
- focused unit/integration tests for exact values, boundaries, invalid inputs,
  deterministic behavior, rectangles, and M01 acceptance.

The package remains dependency-free at runtime, offline-only, independent of
the main ScrubBots checkout at runtime, and free of generator/M02 code.

This log was created before the first product/source edit as required by the
prompt and by the prior audit's process finding.

## Implementation chronology

### Contract implementation

The following M01-only files were added or updated:

- `data/palette/scrubbots_palette_v2.json`: the pinned owner-locked v2 palette,
  including exact C01..C16 values, production color-count bands, and BG01
  presentation metadata.
- `src/scrubbots_pixel_factory/contracts/palette.py`: immutable validated
  palette representation, schema/content validation, C-ID/RGB/HEX lookup,
  ascending ordering, and fail-closed BG01/off-palette handling.
- `src/scrubbots_pixel_factory/contracts/difficulty.py`: strict four-value
  production difficulty enum, independent axis validation, rectangular board
  legality, and narrow SHA-256 domain-separated dimension selection.
- `src/scrubbots_pixel_factory/contracts/color_usage.py`: actual-used-color
  counting, difficulty band validation, explicit subset validation, and stable
  ascending palette-subset selection.
- `src/scrubbots_pixel_factory/contracts/_stable_select.py` and
  `contracts/__init__.py`: M01-only deterministic selection primitives and
  public contract exports.
- `src/scrubbots_pixel_factory/__init__.py`: package exports for the contract
  API; no M02 `GenerationRequest` or generator API was added.
- `pyproject.toml`: package-data installation for the standalone canonical
  palette source under `data/palette`.
- `tests/unit/test_palette_contract.py`,
  `tests/unit/test_difficulty_contract.py`,
  `tests/unit/test_color_usage_contract.py`, and
  `tests/integration/test_m01_contract_acceptance.py`: exact-value,
  schema-negative, boundary, rectangle, actual-used-color, deterministic,
  standalone, source-policy, and M01 coherent-contract coverage.

The palette loader validates the pinned schema, owner lock, all sixteen
ordered IDs, exact HEX/RGB agreement, duplicate IDs/RGBs, production
color-count metadata, and BG01's presentation-only role. The contract layer
uses no runtime dependency, networking, global random state, filesystem access
outside its repository data source, or main ScrubBots runtime dependency.

### Test failures and corrections

1. The first focused M01 run collected 51 tests but failed four tests. The
   shared `CanonicalPalette` object allowed attribute mutation, so its own
   immutability test emptied `_colors` and contaminated subsequent subset
   tests; one Medium explicit-subset fixture also listed six IDs while
   expecting seven. The palette was made truly immutable with slots and a
   rejecting `__setattr__`, and the fixture was corrected. The focused rerun
   passed `51 tests`.
2. The initial full-suite attempt through
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\test.ps1 -p no:cacheprovider`
   was malformed by PowerShell argument binding: pytest received
   `no:cacheprovider` as a path and collected zero tests. It was corrected by
   invoking the venv Python directly with `-p no:cacheprovider`; the full
   regression suite then passed `60 tests`.
3. The final focused rerun passed `51 tests in 0.52s`; the final full rerun
   passed `60 tests in 0.82s` on Windows Python `3.12.10` and pytest `9.1.1`.

### Required verification evidence

- Pinned main-game HEAD query returned exactly
  `b4ecabb34b8f8f46f2999a0ecc83dfa9c61f02cd`; no contract drift was found.
- Direct semantic comparison of local JSON to the pinned GitHub palette passed
  for all sixteen colors and BG01.
- Deterministic repeated-run smoke produced identical dimensions/subsets in
  separate processes; the fixed seed sample includes rectangular dimensions
  and multiple valid subsets.
- Standalone import resolved from this Level Factory checkout's `src` tree.
- `pip check` reported no broken requirements.
- Static M01 source checks found no forbidden network imports and no
  `GenerationRequest` or generator implementation.
- Package metadata dry run reported `Would install
  scrubbots-pixel-factory-0.1.0`.
- `git diff --check` passed.

The pre-existing `.hiveai/PROJECT.json` edit remains unstaged and preserved.
No task checkbox, H!veAI acceptance state, handoff, cycle index, event, prompt,
prior log, audit, `reference/audits/`, or main ScrubBots checkout was changed.

## Finalization pending

The intended staged set is limited to the M01 contract source/data/tests,
package metadata, and this matching builder log. The implementation commit,
final log commit, push results, final status, and local/remote equality will be
appended after commit and push. Builder status remains implementation complete /
pending independent audit; this log does not declare `PASS` or `CLOSED`.
