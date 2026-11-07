# SB-LFX OWNER GOAL | AUTONOMOUS OPEN-BACKLOG EXECUTION | 2026-10-31

Document role: CODEX BUILDER LOG

## Scope

Install the already published PixelLab MCP full-gallery-atlas fix into the existing Factory Studio Release, using its scoped transactional installer. The existing paid generation and its gallery asset are reused; no provider generation call is authorized or performed. The owner explicitly prohibited access to PNGs in `data/output/Pixellab/Final` and `data/output/Pixellab/Grid Files`; those directories are not to be read, inventoried, or changed.

## Start record

- Starting timestamp: 2026-11-07 (local session date; exact wall-clock time not captured in this log entry).
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Repository: `Sekiph82/ScrubBots-Level-Factory`; origin URL verified as `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Branch: `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting HEAD and `origin/main`: `a86b6a0ef461ed30ff1dfd428ae1e206d60ace52`; ahead/behind `0/0`.
- `python -B scripts/codex/scrubbots_task_queue.py --json --allow-existing-work` passed canonical root, origin, ancestry, task and prompt authority checks. It reported the existing legacy-reset task as externally blocked; this installation request is directly authorized by the owner's latest chat instruction and root `AGENTS.md` recovery authorization.
- Initial tracked worktree: no tracked modifications (`git diff --name-status` empty; `git diff --check` passed). Numerous unrelated untracked owner files exist and will not be staged or changed.
- Relevant existing source: `src/scrubbots_pixel_factory/studio_extensions.py` SHA-256 `81c946339d8ab1d728d39c98638bead92bae02f7a42a4f1e594aec3a6f2f3e2e`; launcher `level_factory/scripts/factory_core_launcher.py` SHA-256 `1588da15da4a639086415ef7ad5cc548cae03b4fe42f1c8f403225d8073e5c0b`.
- Installed counterparts differ and lack the current MCP gallery retrieval implementation: installed `studio_extensions.py` SHA-256 `3a7d046a35dacb6ea516179d6004e388c0962d195dc43d711981e8e14e86d27f`; installed launcher SHA-256 `7d383e204588c8c4374ce06660087171de5b16f87ca8f71d8f027f632b9dee9b`.
- Installed manifest SHA-256: `5b05c52187160d1615d2f274df63f3b60f46d861f374e4194df5bf128a20d4d4`. The unrelated installed `supply_pipeline/verify.py` exactly matches its manifest entry and current source at SHA-256 `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3`.
- No Factory Studio process was present in the process inventory at start.

## Contracts read

- Root `AGENTS.md` supplied in the active chat.
- `.codex/skills/scrubbots-factory/SKILL.md`.
- Root `TASKS.md`, authoritative active prompt `SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, and `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`.
- `scripts/install_factory_studio_scoped_overlay.ps1`, its scoped transaction module, and `tests/unit/test_scoped_overlay_manifest_drift_contract.py`.
- Existing published PixelLab source fix is commit `f96de91d` (`Fix PixelLab MCP gallery atlas retrieval`); prior evidence says gallery retrieval must select `gallery:<asset_id>` and use the full sheet URL rather than the 56x56 inline frame.

## Initial installation preflight

The authorized installer was run without `-Apply`, scoped to the required source files. It refused before mutation because the current manifest digest did not match the installer's enumerated historical `verify.py` repair manifests. This check is unrelated to the requested targets. The installed `verify.py` bytes do match its manifest hash exactly. Planned remediation is a fail-closed scoped-install branch: when `verify.py` is not selected, require its installed bytes to match its manifest entry and skip only the unrelated historical repair-chain gate; when it is selected, preserve all existing historical provenance checks unchanged.

## Change record

### Scoped installer correction

- Changed only `scripts/install_factory_studio_scoped_overlay.ps1` and `tests/unit/test_scoped_overlay_manifest_drift_contract.py` for the source commit.
- The installer now skips the historical `verify.py` repair-chain gate only when `verify.py` is not among the selected target paths. It verifies that the installed file exists, is not a reparse path, and exactly matches its installed manifest SHA-256. Selecting `verify.py` still requires one of the existing recognized historical receipt chains.
- Added a regression contract test for the unselected-file equality condition and the selected-file refusal path.
- Focused test: `python -B -m pytest -q -p no:cacheprovider tests/unit/test_scoped_overlay_manifest_drift_contract.py` — **10 passed** in 0.12s.
- PowerShell parser: `[System.Management.Automation.Language.Parser]::ParseFile(...)` — **PASS**, no syntax errors.
- `git diff --check` — **PASS**.
- First scoped preflight (read-only) — **PASS**; exactly the two authorized source files were planned, no overlay additions or manifest drift.
- Implementation commit: `80bfb86090787fbf3b863349fdf5c9e580327187` (`fix(installer): allow verified scoped PixelLab overlay`). Normal push to `main` succeeded.
- The first post-push verification wrapper returned exit 1 because PowerShell compared the ahead/behind string against a single-quoted literal containing `` `t ``; the actual push had succeeded and both SHAs were already equal. Reran verification by splitting the numeric output: `HEAD == origin/main == 80bfb86090787fbf3b863349fdf5c9e580327187`, ahead 0, behind 0.

### Installed Release update

- Re-ran the read-only official installer preflight after publication; it planned only `level_factory/scripts/factory_core_launcher.py` and `src/scrubbots_pixel_factory/studio_extensions.py`, with zero manifest drift.
- Applied the official scoped transaction: `scripts/install_factory_studio_scoped_overlay.ps1 -Apply -OnlyPaths @('level_factory/scripts/factory_core_launcher.py','src/scrubbots_pixel_factory/studio_extensions.py')` — **COMMITTED**.
- The transaction reported writer exclusion using Windows FileStream deny-write handles on every existing replacement target and install manifest, plus a denied independent PowerShell write-open probe on every existing live target. Staged hashes were checked before atomic replacement.
- Installed SHA-256 checks match the published source exactly:
  - `level_factory/scripts/factory_core_launcher.py`: `1588da15da4a639086415ef7ad5cc548cae03b4fe42f1c8f403225d8073e5c0b`.
  - `src/scrubbots_pixel_factory/studio_extensions.py`: `81c946339d8ab1d728d39c98638bead92bae02f7a42a4f1e594aec3a6f2f3e2e`.
- New installed manifest SHA-256: `479df5dee360ac5d635266e0b78e2e3dee35b4cac3fa3ae38ef4322bb901f20e`. Its latest receipt binds both files to source commit `80bfb86090787fbf3b863349fdf5c9e580327187` and records the writer-exclusion method.
- Source verification: the launcher now calls `generate_pixellab_pro_4x4_atlas_mcp`; the extension requests `get_image(job_id="gallery:<asset_id>")`, extracts the full-sheet URL, and validates atlas dimensions before slicing. The existing paid generation was not repeated.
- The Desktop shortcut already targets this Release launcher and did not need modification. No GUI was launched; native visible behavior remains NOT RUN.
- The two protected PixelLab PNG directories and all PNG files within them were not accessed. The separate ScrubBots game repository was not accessed or changed. No CI/Actions or provider calls were made.

### Publication and final state

- Builder-log commit and final parity verification will be recorded here after publication.
- The published source commit is verified at `origin/main`; the Release folder is owner-local/untracked and was not staged.
