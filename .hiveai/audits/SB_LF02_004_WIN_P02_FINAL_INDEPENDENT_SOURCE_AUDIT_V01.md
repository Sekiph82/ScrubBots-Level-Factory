# WIN-P02 | GPT Independent ART_FIRST Review-Root Reparse Source Audit V01

Date: 2026-10-16 Europe/Istanbul
Repository: `Sekiph82/ScrubBots-Level-Factory`
Independent code-reviewed base: `d1da2969bbdc1f9d00121844f7608bafb062cd98`
Builder implementation SHA: `1231673df8d8ff5ab3c8f93420dc3c15c9efdaa2`
Builder-published final main: `7d41c35d97e3d108edf859c6d2c72d544eb6d55d`

**VERDICT: WIN-P02 SOURCE-BOUNDARY PASS / F01 CLOSED (source/code contract only). ACTUAL NTFS ART_FIRST SYMLINK/JUNCTION AND RACE-FREE HANDLE TESTS NOT RUN/UNVERIFIED.**

## Independent GitHub inspection

GPT independently retrieved current GitHub main and compared the commits/diffs. Product/source/test commit modifies only `src/scrubbots_pixel_factory/generators/router/art_first.py` and `tests/unit/test_sb_lf02_004_art_first.py`; remaining changes are in preexisting builder log. Commits `1231673`, `7de4e60`, `0ea9ff9`, `7d41c35` preserve normal commit ancestry. The workflow directory has zero net modifications. Existing manual-only `workflow_dispatch` remains canonical. No GitHub Actions or hosted CI was initiated for this audit.

The log reports five directly invoked, **in-memory** synthetic Python checks PASS, AST parsing for two changed files PASS and `git diff --check` PASS. One source-log append attempt failed diff check due an accidental control character; correction was documented. GPT did not run Windows/Python commands and did not independently attest the builder's local 0/0 Git parity or 3,220 untracked file preservation. Existing 16 known task scratch files remain policy-protected; no deletion retry authorized.

## F01 code disposition
The previous `SB_LF02_004_WIN_P01_REPARSE_INDEPENDENT_AUDIT_PARTIAL_V01` found that using an already resolved `studio_extensions.extensions_root()` and `review_root.is_symlink()` alone could miss Windows directory junctions at the trusted review directory or an ancestor. The new `art_first.py::_validated_review_root()`:
1. Derives a *raw* `studio-extensions` directory directly from the previously verified `owner_upload_root().parent`, before relying on any externally configured resolved root.
2. Rejects reparse points via `_path_is_reparse_point` and non-directory roots; `resolve(strict=True)` and exact expected parent equality enforce physical output-root authority.
3. Requires configured `extensions_root()` (if supplied/injected) to resolve to precisely that verified canonical path, **not** a user-nominated external review authority.
4. Checks raw `owner-review` for reparse-point status/non-directory and requires its strict resolved parent and exact canonical resolved location before returning it for `iterdir`. Call site `_candidate_and_review` now obtains that checked root before review enumeration, then existing bounded `_safe_file` and current `validate_owner_review_chain` continue enforcing content and current ACCEPT truth.

Added tests cover injected reparse `studio-extensions`, reparse `owner-review`, noncanonical configured root, canonical positive helper path and candidate caller negative path (both reparse markers), with no file enumeration/read on rejected owner-review chains. Scoped F01 is closed by source inspection plus builder focused test evidence. Owner source PNG/grid/classification and ART_FIRST TEST/PREVIEW path unchanged by the P02 diff.

## Explicit verification limitations

- Existing positive **source-backed** ART_FIRST fixture and full focused pytest suite were **NOT RUN** on the new SHA to avoid writing scratch; only an in-memory canonical-root positive helper branch was checked. Do not claim full generation/export/CLI reproduction on this exact revision.
- Actual Windows junction/symbolic link was **not** presented to ART_FIRST review guards; earlier read-only Windows samples only classified native path types. Native application behavior remains **NOT RUN**. Do not infer native PASS from monkeypatch tests.
- `Path.lstat`, `resolve` and `read_bytes` use sequential path accesses; no atomic Windows handle-open or TOCTOU race resistance was established. This remains security-hardening follow-up, not production attestation.
- Authentic upstream AI creator or owner identity is not validated by OWNER_UPLOAD, and owner ACCEPT review is distinct from creator identity. `SB-LFX-018/R05` real ScrubBots game/owner Studio/production, load-check and long-run native regression remain DEFERRED/OPEN; no original 140 PNG or Release owner data was touched according to builder.

## Final decision

**Close WIN-P02 F01 for narrow independently inspected source-path trust contract.** Preserve separate **Windows real native link+handle gate UNVERIFIED**, no privilege/admin/Developer Mode workaround. Next meaningful project frontier is a **read-only R05 current evidence/authority readiness inventory** without new solver runs, owner files, Release writes, Godot app launches, game repo writes, cleanup or CI. Do not project earlier historical R05 screenshot, READY, game authorization or old solver result onto current data without exact current evidence. If native or owner consent is needed, stop with an honest gate.
