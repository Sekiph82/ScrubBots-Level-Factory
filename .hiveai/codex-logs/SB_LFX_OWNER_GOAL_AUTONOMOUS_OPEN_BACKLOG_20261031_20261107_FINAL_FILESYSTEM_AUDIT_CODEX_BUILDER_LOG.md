# SB-LFX OWNER GOAL | AUTONOMOUS OPEN-BACKLOG EXECUTION | 2026-10-31

Document role: CODEX BUILDER LOG

## Final filesystem and application-state audit — 2026-11-07

### Starting state

- Canonical Desktop checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`; starting HEAD and `origin/main` `2df42944cb8553e9f521201f8c92da321349daed`, ahead/behind `0/0`.
- `python -B scripts/codex/scrubbots_task_queue.py --json --allow-existing-work` passed. No tracked source changes existed. Existing untracked owner/Release artifacts were left untouched and unstaged.
- PixelLab `Final` and `Grid Files` folders were not accessed. The ScrubBots game repository remained read-only.

### Protected retained inventory and Release Pool

- Corrected read-only verification resolved inventory paths from the repository root and verified both retained roots against their manifests: 30 unique level IDs in each, exact ID set match with each copied production catalog, 193/193 declared asset entries hash/size-correct per root (30 levels, 30 metadata, 30 previews, 10 game source-art files, 29 supply plans, 60 files in 20 candidate bundles, and 4 files in the Chef desktop variant).
- Actual file enumeration found exactly `Failed`, `Pending`, `Ready`, and `Rejected` under each Release Pool root, with zero files in each tree.
- Desktop active `owner-uploads` directory is empty and Desktop `studio-derived-candidates` is absent. The installed Release still exposes the eight previously documented ACL-denied candidate directories; their payloads cannot be inventoried or removed through the permitted file operation.
- `current-game-runtime` was retained. It contains the pinned game/runtime source needed by Factory plus historical `.lf_solver_jobs` records (11 in Desktop copy; 271 in installed copy). No Factory Studio process targeting this checkout was found. Historical job evidence was not deleted.

### Runtime and shortcut observations

- Read-only process query found no process whose executable or command line targeted the Factory Studio installation/launcher/runtime. A separate `godot-ai.exe attach --port 8000 --ws-port 9500` process was observed but had no Factory path; it was not controlled or terminated.
- Desktop `ScrubBots Factory Studio.lnk` already targets PowerShell with `-File` pointing to the canonical Release `scripts\launch_factory_studio.ps1`, with the Release directory as working directory. No shortcut change was needed.
- No native UI/restart test was run. This is filesystem/process evidence, not native application acceptance.

### Recovery and command corrections

- The cold recovery archive still contains 19 exact source PNG SHA-256 matches. One cached raster did not reproduce the historical PNG hash; its nonmatching re-encoding remains removed. Exact source JSON recovery remains 0/20.
- Two exploratory inventory verification commands failed because the retained inventory has `factory_candidate_variants` and Release-relative paths not handled by the first parser. The corrected bounded verifier passed with 0 missing/hash errors across both inventories. These failures did not modify data.
- No source tests were added or run; no product code changed. No hosted CI, paid provider, game write, or `Final`/`Grid Files` operation occurred.

### Outcome

- The requested cleanup remains PARTIAL: eight installed candidate directories are inaccessible under current tool policy, one original source PNG byte identity and 20 source JSON records lack exact backups. No safe authorized operation remains that can remove or reconstruct those items. Keep the existing goal open and do not claim completion.
