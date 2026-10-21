# SB-LFX-018 R05 V13-C/D R07 | OWNER-APPROVED STAGED INVENTORY, MIGRATION DESIGN AND BOUNDED NATIVE VALIDATION

Document role: CODEX BUILDER EVIDENCE REPORT

Prepared: 2026-10-21 (Europe/Istanbul)
Repository: `Sekiph82/ScrubBots-Level-Factory`
Canonical checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Starting synchronized source: `8a817c3ebc9ec96d78762401b1658ed61309ac7d`
Scope: owner-authorized R07-A read-only inventory, R07-B prospective design, and conditionally gated R07-C native project parse.

## Authority and preservation boundary

The exact R07 prompt and GPT-owned tracker authorize three sequential stages. R07 does not authorize a Release install/rollback, manifest edit, installed GUI manipulation, process termination/suspension, original job replay, CI/Actions, paid provider, R2, staging or production work. `TASKS.md`, prompts, audits, HANDOFF, and previous log content remain unmodified. This report and the append-only existing builder log are the only intended evidence writes.

`git fetch --prune origin` found local HEAD `b7ee861983183ee2008d5eb509fb601395be9136` behind `origin/main` `8a817c3ebc9ec96d78762401b1658ed61309ac7d` by four commits and ahead by zero. Tracked worktree and index were clean; owner-untracked files were preserved. `git merge --ff-only origin/main` succeeded. No new clone, worktree, TEMP directory, reset, clean, stash, or deletion was used.

## R07-A — exact live read-only inventory

### Process snapshot and launch routes

A read-only `Get-CimInstance Win32_Process` snapshot returned 595 processes. The bounded Godot/Python/application-route candidate set had 32 entries with PID, PPID, name, executable path, creation time, and command line populated; sensitive-looking command lines were redacted before display. The only Factory Studio path text in a command line belonged to the task's own PowerShell inspection shell; excluding that self-observation, no process executable or command line matched the Factory Studio Release root, `factory_core_launcher`, `png_batch`, `scrubbots_solver`, or `alpix_batch` runtime routes. Python MCP service entries were unrelated Blender MCP workers; no process was started, stopped, suspended, attached to, or signaled.

One live Godot process is present: PID 13860, `Godot_v4.7.2-stable_win64.exe`, launched via the WinGet Godot link with `--headless --path "C:\Users\sekip\Desktop\Beach Cocktails - Merge" --install-android-build-template`, creation time 2026-10-18 21:11:51 local. It belongs to a different project. It was not touched. A separate Godot AI attach service is also present, on its configured local ports; it was not used for this task.

The source launch graph remains multi-entrypoint: the shortcut invokes the PowerShell launcher; the launcher starts Godot on a project; the Studio gateway uses `OS.execute` to invoke the Python core launcher; direct Python batch/control operations exist; the solver bridge spawns a Godot headless child; and ALPIX work has its own Python runner path. Thus a cooperative lock added only to new source cannot exclude existing Release binaries, direct Python/Godot entrypoints, or already-running descendants.

### Six manifest artifacts

All six named artifacts were read directly from `Release\ScrubBots Factory Studio` without recursive traversal. Each is JSON format version 1; every managed entry has a relative path and 64-character SHA-256; no duplicate managed paths were found. Counts and current SHA-256 values match the exact R04 packet:

| Artifact | SHA-256 | Managed | Overlay paths | Receipts |
| --- | --- | ---: | ---: | ---: |
| `.factory-studio-install-manifest.json` | `9e5bda945b9f86606c5afe484e6cf7cc66c7f5a69744795250fa8631fb5a3f3d` | 2318 | 20 | 17 |
| `.factory-studio-install-manifest.json.r04-backup-a527041` | `0c885ee848c93c9a2ec50e485838c1209d6005cfdd111249c46bd16525393cc4` | 2077 | 1 | 1 |
| `.factory-studio-install-manifest.json.r04-r01-backup-54105bc` | `de434a436f6dff409c5cccb4c27f1e5eb798eeb1a333f9d6c0b3cecc8420cdce` | 2077 | 1 | 1 |
| `.r04-ui-overlay-rollback-manifest-c7ab656d263a.json` | `c7ab656d263a5c5dbf77f0400a41da45c86ca8f830272872923f19251e300995` | 2316 | 9 | 1 |
| `.r05-m01-rollback-manifest-56c9f32518fe.json` | `56c9f32518fe01b2354942600c8d19662cab0713a23b42551304fccfbc0493eb` | 2316 | 9 | 1 |
| `.r05-m01-rollback-v2-manifest-94c6f6b51dc2.json` | `94c6f6b51dc28e1c1208e04146f0573760ca6af03114657cff0e7b0b9a7a6ec7` | 2316 | 9 | 2 |

The main manifest contains `verify.py` as a managed path with no overlay path and no file receipt. None of the six artifacts names `verify.py` in its overlay paths or binds it in a file receipt. Rollback manifests remain snapshots, not installation authority.

### Exact 18-path matrix

Every listed source and installed file exists. The two roots and all path components for these 18 paths were resolved and checked; no symlink/reparse path or root escape was found. SHA-256 was recomputed from the current source and installed bytes. `Expected` is the main manifest's managed-file digest; `Receipts` counts exact path bindings in receipt file lists, not the high-level receipt count.

| Managed path | Expected SHA-256 | Installed SHA-256 | Current source SHA-256 | Overlay / receipts | Disposition |
| --- | --- | --- | --- | --- | --- |
| `level_factory/scripts/factory_core_launcher.py` | `563353c20c608e98484585db8322e423b9fc4641609c92dc4d83ee3fa160a5ea` | `563353c20c608e98484585db8322e423b9fc4641609c92dc4d83ee3fa160a5ea` | `60735cf39d632facca42919cbaee0aafb14a084d3d3d39ab55f268b0a44e2a4b` | yes / 3 | prospective source update |
| `level_factory/scripts/factory_studio_exact_ui.gd` | `2ce9a247698ecd2c098def1c5986db2a90921af3566a8d1872d17456c5137457` | `2ce9a247698ecd2c098def1c5986db2a90921af3566a8d1872d17456c5137457` | `7c4de3f4b716f13feade5bbb48529a754891fd82233d25c47ac96b1fadbe0a5e` | yes / 8 | prospective source update |
| `scripts/launch_factory_studio.ps1` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | yes / 1 | unchanged |
| `level_factory/scripts/factory_studio_shell.gd` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | yes / 2 | unchanged |
| `level_factory/scripts/factory_studio_workspace_page.gd` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | yes / 1 | unchanged |
| `level_factory/scripts/factory_core_gateway.gd` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | yes / 1 | unchanged |
| `level_factory/project.godot` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | yes / 1 | unchanged |
| `src/scrubbots_pixel_factory/output/bundle.py` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | yes / 1 | unchanged |
| `src/scrubbots_pixel_factory/semantic/providers/registry.py` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | yes / 1 | unchanged |
| `src/scrubbots_pixel_factory/png_batch.py` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | yes / 4 | unchanged |
| `src/scrubbots_pixel_factory/studio_extensions.py` | `b5a5b6ec2ec969ddf3de9c2fd6fb536476440185b8bf458b0995662587be7ee9` | `b5a5b6ec2ec969ddf3de9c2fd6fb536476440185b8bf458b0995662587be7ee9` | `6d2e51fdaf01700f3ab798933d129966269819d642980205294010bc5d41b2ad` | yes / 6 | prospective source update |
| `src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py` | `640acc3804ae99e98623a046088e7c29f87201e8ee6dda828983b0427fca9a72` | `640acc3804ae99e98623a046088e7c29f87201e8ee6dda828983b0427fca9a72` | `f3ebd2ec8439e1bf9424d129c892ab8c555d036799aa04f7f90ede4112d38a51` | yes / 1 | prospective source update |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py` | `17f3a425d310eb5999dc147f1c15d14833ed353e014e4c7e3b7a8f7f36b59a25` | `17f3a425d310eb5999dc147f1c15d14833ed353e014e4c7e3b7a8f7f36b59a25` | `d86617e377a38854533e4cb784cb752fcfbad4882a3ed0e9872d77dc08ad0dfb` | yes / 1 | prospective source update |
| `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | yes / 6 | unchanged |
| `src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py` | `cdc5521902433e5d9370fb3585bf5898974964fcac81aa207d35941765f201dc` | `cdc5521902433e5d9370fb3585bf5898974964fcac81aa207d35941765f201dc` | `6769c1aa26f66244cf1a527add20dd958c90dd65201abf02441eb081aeac527b` | yes / 2 | prospective source update |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py` | `1f8776da86260ce27529b63213f4c632fe1cbb459197d49e3011ee0e3cb92bf0` | `1f8776da86260ce27529b63213f4c632fe1cbb459197d49e3011ee0e3cb92bf0` | `d645bdb37897f466ff14f18a76fcaab6bdadaf7e92e422cacfbf894fb9b3ae97` | no / 0 | prospective overlay addition/update |
| `src/scrubbots_pixel_factory/supply_pipeline/verify.py` | `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2` | `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744` | `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3` | no / 0 | UNKNOWN DRIFT; hard block |
| `src/scrubbots_pixel_factory/alpix_batch.py` | `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282` | `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282` | `cea1af97f95de96d0a8c7187bafd4e2e68dd9fa2939f09be4d2a5c95d5b8185c` | no / 0 | prospective overlay addition/update |

Eight paths have manifest-matching installed bytes with differing current source bytes and are prospective content updates; nine are byte-identical and unchanged. `verify.py` is a separate expected/installed/source mismatch and has no overlay authority or receipt. The three prospective overlay additions remain `supply_exporter.py`, `verify.py`, and `alpix_batch.py`; the `verify.py` addition is not approved by source lineage and blocks a complete deployable set.

### Original job and Release Pool

The exact COMPLETE owner job was read by direct path only: `png-batch-875545d48a14a0d6b4d542f554919e8d.json`; SHA-256 `33c11885032f9b9b6050ea642c4870e04e8424dacc00de749b51234ce9f94193`; state digest `56823da1561858e6275e180b0c766b46daacf6f735e7200cfce47b0369d98490`; 140 total, 102 READY, 4 FAILED, 34 REJECTED, zero remaining. The 131-file Release Pool was enumerated only at its exact directory; tree digest `e227c95f85635a48522dbdd5aefeb2ead51f2e25070fb8f4b315746ebbc9a81d`. Both values match the prior builder record. No PNG/job/pool data was written or re-run. This count is not a verified READY count.

One earlier broad recursive Release listing emitted access-denied errors on protected `studio-derived-candidates` directories. It was not retried; the exact six manifests, exact 18 paths, job file and Pool directory were then read directly. A first path-ancestor check reached a null parent at the volume root and printed errors; it was corrected with a bounded parent walk, which then passed for all 18 paths under both roots. Both failed commands were read-only and made no file changes.

**R07-A result: `R07_A_LIVE_READONLY_INVENTORY_PASS`.** The process snapshot is point-in-time, not writer exclusion.

## R07-B — prospective migration and exclusion design

No source-only writer lock was added. The graph has legacy/direct Python, Godot GUI/headless and ALPIX child routes; a new cooperative mutex would not bind old deployed entrypoints or callers that bypass it. Snapshotting processes also leaves a start-after-snapshot race. `WriterExclusionEstablished` remains false and `PROCESS_QUIESCENCE_UNPROVEN` remains.

The prospective controlled migration can advance only after a separate decision resolves the `verify.py` authority gap and an enforceable global maintenance boundary exists. A future exact transaction would:

1. Re-read and validate all six manifests and all 18 installed/source hashes, path identities, ACLs and reparse points immediately before any separately authorized apply; require no drift or unknown files.
2. Stage only the eight allowlisted source payloads and proposed receipt/manifest bytes in a protected same-volume transaction area; hash each source and staged payload, require byte equality, record exact old/new manifest bytes, and refuse on any unapproved path or changed preflight. No such staging occurred in R07.
3. Keep the nine unchanged paths untouched. Do not replace `verify.py` or add its trusted hash while expected `0f4b7f…`, installed `90e560…`, and current source `151a95…` remain unapproved. Proposed overlay additions are limited to the three named paths; the manifest must contain a genuine new receipt created by that future transaction, never an edited historical receipt.
4. Replace under a proven OS-level exclusive maintenance boundary, verify every installed SHA and the new receipt, and on any failure restore each exact old byte set independently and verify hashes before reporting rollback success. Preserve the owner job, Pool, PNGs and all non-allowlisted files.

The currently inspected same-user processes can directly start Godot/Python or use legacy scripts; no existing global OS gate was found that blocks every such route. A future design needs an owner-approved maintenance boundary outside cooperative source code (for example, a reviewed OS application-control/maintenance policy plus a separately constrained updater identity), with proof that old entrypoints cannot run and no process can write the Release tree from preflight through commit/rollback. Such a policy has broad Windows impact and requires its own exact scope and proof plan. No policy, launcher, lock, installed file, or manifest was changed here. No synthetic test was added because no code changed.

**R07-B result: `R07_B_MIGRATION_DESIGN_READY`; `PROCESS_QUIESCENCE_UNPROVEN`; `INSTALL_BLOCKED_MANIFEST_DRIFT`.** Design readiness is prospective documentation only, not apply authorization.

## R07-C — bounded native Godot gate

Godot 4.7 command documentation confirms `--check-only` parses only with `--script`; `--import` starts the editor and waits for all resource imports. The latter is not an acceptable bounded route for this task. Godot 4.7 documents Windows editor data/config under `%APPDATA%\Godot` and cache under `%LOCALAPPDATA%\Godot`; `user://` may resolve to editor app data. These destinations are outside the source project. See [Godot 4.7 command-line tutorial](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html), [Godot 4.7 editor data paths](https://docs.godotengine.org/en/4.7/classes/class_editorpaths.html), and [Godot project file system](https://docs.godotengine.org/en/4.7/tutorials/scripting/filesystem.html).

The live Godot PID 13860 is still running the unrelated Android export-template installation and may write in the same user-wide Godot editor-data/config area. The exact separate write set of that in-progress process cannot be attributed or frozen without forbidden process control. A new Godot child might also touch shared editor state in addition to permitted project-local `.godot`, `.uid` or `.import` paths; no isolation exists that stays within the approved path set. A one-script `--check-only` parse would also be narrower than a project-wide test and does not establish that no broader project/user writes occur. Therefore no Godot executable was launched by R07 and no project files/caches were changed.

**R07-C result: `NATIVE_TEST_BLOCKED_OUTSIDE_OWNER_SCOPE`.** Exact blocker: an unrelated active Godot process is performing an editor-data operation while the task lacks an enforceable way to isolate or attribute concurrent writes to shared `%APPDATA%\Godot` / `%LOCALAPPDATA%\Godot` paths. No kill, suspend, attach, GUI launch, import or retry occurred.

## Verification, changes and disposition

- No product source, tests, Release bytes/manifests, owner PNG/job/Pool data, generated project cache, workflow, dependency, prompt, audit, HANDOFF, or `TASKS.md` was changed.
- No CI/Actions, paid API, provider, R2, staging/production, installer `-Apply`, native GUI, or 140-item operation was invoked.
- The only intended tracked changes are this R07 evidence report and an append to the existing M03 builder log.
- `git diff --check` and final publication/parity checks are to be recorded in the builder log after the evidence changes.

Current dispositions: `INSTALLED_GUI_OPEN`; `RELEASE_APPLY_NOT_AUTHORIZED`; `WRITER_EXCLUSION_ESTABLISHED=false`; original 140 job and 131-file Pool preserved. A separate explicit owner decision is required before any real Release migration, policy change/process-control operation, or installed GUI manipulation.
