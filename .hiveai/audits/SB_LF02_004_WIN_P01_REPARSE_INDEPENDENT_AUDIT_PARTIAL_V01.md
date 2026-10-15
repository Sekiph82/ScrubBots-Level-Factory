# SB-LF02-004-WIN-P01 | Independent GPT reparse/source audit | PARTIAL F01

Date: 2026-10-16 Europe/Istanbul
Repo: `Sekiph82/ScrubBots-Level-Factory`
Builder-tested source SHA: `3810255c5909224bac821fc17f54e1322543a1fb`; builder final GitHub main `170f61eb0fbe9176dd3b94d9557cc1f7d76cd3d1`.
Base GPT main: `08276cdea7d34b6e3d7dec27ddc36aaa30547afe`.
**Verdict: WIN-P01 SOURCE PARTIAL / F01 REVIEW-CHAIN ROOT REPARSE ESCAPE OPEN. Real NTFS ART_FIRST guard testing NOT RUN; race-free path handles NOT PROVEN.**

## Independent evidence
GPT directly fetched canonical remote main, compare and implementation commit. Net modified files: `src/scrubbots_pixel_factory/owner_upload.py`, `src/scrubbots_pixel_factory/generators/router/art_first.py`, `tests/unit/test_sb_lf02_004_art_first.py`, single preexisting builder log; **no workflow changes**. Builder log reports a normal main push with 0 ahead/behind and 3,220 unchanged untracked entries, but GPT cannot independently inspect Windows filesystem/dirty state.
Builder reports **5 focused in-memory PASS** for synthetic reparse guards and resolved-path escapes, **3 read-only native OS path classification PASS** (two Windows junctions, one symlink), AST and `git diff --check` PASS; no pytest, new scratch, CI or Actions. GPT did not run builder's local tests. In particular, no native symlink/junction was created or passed through ART_FIRST to prove actual OS-level security; native application gate remains **NOT RUN**. Path-based `lstat`, `resolve` and `read_bytes` are distinct operations; no race-free open-handle guarantees were established.

## Source-confirmed improvements
- `owner_upload.py::_path_is_reparse_point` checks `lstat` symbolic link bit, Windows `FILE_ATTRIBUTE_REPARSE_POINT` and (where available) `Path.is_junction`, treating unexpected `OSError` fail-closed. This is stronger than `Path.is_symlink()` on Windows.
- `owner_upload_root` checks each *canonical* upload-root path component before resolving it, requires expected path and repository containment; actual Windows local root reportedly has no reparse components.
- `art_first.py::_load_source` refuses reparse-point store/source directories, requires strict expected resolved parent for source, and uses bounded symlink/reparse rejecting `_safe_file`. `_candidate_and_review` now enforces strict expected store/directory parents and refuses candidate store/dir reparse points. Existing exact logical source/byte/candidate/review output classes unchanged.
- No game, owner 140 PNGs, accepted 002, 9 READY, installed Studio/Release, R2/cloud touched by the published GitHub diff.

## F01 (blocking P01 full path/review-chain security claim)
In the CURRENT `src/scrubbots_pixel_factory/generators/router/art_first.py` after the changes:
```python
review_root = extensions_root() / "owner-review"  # studio_extensions.extensions_root() already resolves()
if review_root.is_symlink() or not review_root.is_dir():
    ...
paths = sorted(path for path in review_root.iterdir() ... )
...
raw = _safe_file(path, review_root, ...)
chain, invalid = validate_owner_review_chain(...)
```
The **same ART_FIRST approved-source contract depends on this review chain**, which can authorize `review_disposition=ACCEPT`. The review directory and `studio-extensions` parent are not guarded using the newly added `_path_is_reparse_point`, and `review_root.is_symlink()` does **not** identify Windows directory junctions. Worse, `studio_extensions.extensions_root()` calls `.resolve()`, potentially erasing visible symlink/reparse identity in a parent before the caller checks. `_safe_file(path, review_root,...)` ensures files are inside the **supplied review_root**, not that this root belongs to the canonical Studio output area. Therefore a replaced junction/reparse segment can redirect the ACCEPT review evidence directory outside its authority root while ordinary `is_symlink()` remains false for a junction. This is a **source-level reachable trust-boundary design defect**, not a claim of a demonstrated exploit on the owner's machine. No native guard test or real malicious junction was run.

**Corrective F01 only:** Derive the expected raw Studio extensions directory directly from the already verified `owner_upload_root().parent`, inspect the `studio-extensions` component before any `.resolve()`, verify actual resolved location and strict expected parent. Likewise reject reparse/junction at `owner-review` and require its strict resolved parent to equal the verified extensions root. Keep tests' current injected `extensions_root` contract compatible only when it is the same expected canonical source-store relative root; never silently accept arbitrary external injected review authority. For all files, continue existing `_safe_file` checks, source/ACCEPT chain and identity hash verification. Do **not** modify general-purpose Studio extension root implementation, global Source Library layout, owner evidence or production Pool to fix this ART_FIRST-specific path issue.

Add isolated in-memory guards for redirected `studio-extensions` parent and owner-review directory junction, assert refusal before review file enumeration/read. Preserve existing code paths, do not create new NTFS links, scratch or filesystem artifacts. Use `python -B` / `PYTHONDONTWRITEBYTECODE`, AST and diff checks. Real native Windows P01 gate remains **UNVERIFIED** if no permitted test fixture exists.

## Decision
WIN-P01 **PARTIAL / OPEN F01** pending source correction. Prior `SB-LF02-004` ART_FIRST source-consumption and `SB-LF02-008` no-fabrication source-contract closures are not revoked in their earlier narrow scopes; this follow-up reparse security gate is separate. Real Windows app-path link behavior, time-of-check/time-of-use race-free handle reads, authentic upstream AI creator provenance and `SB-LFX-018/R05` genuine game/native/production remain **OPEN/UNVERIFIED**. No Actions, CI or hosted tests permitted under owner budget lock.
