# SB-LFX-018 R05 V13-C/D R06 | Install Readiness, Writer Exclusion & Native Route

Document role: READ-ONLY OWNER DECISION PACKET
Prepared: 2026-10-21 (Europe/Istanbul)
Repository: `Sekiph82/ScrubBots-Level-Factory`
Preparation base: `ead8875b4c552cdadf00af61d2b321d5f1ab0d0b`
Scope: install readiness, exclusion feasibility, prospective manifest migration, native test route

## Current disposition

No Release apply, owner process inspection, Godot invocation, GUI launch, or owner-data read/write was performed. R06 adds no product source change: a lock added only to new source cannot exclude older installed processes that do not participate. Preserve `WriterExclusionEstablished=$false`, `PROCESS_QUIESCENCE_UNPROVEN`, `INSTALL_BLOCKED_MANIFEST_DRIFT_PENDING_OWNER_DECISION`, `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK`, `INSTALLED_GUI_OPEN`, and `NO_APPLY`.

## Writer and launch graph

This is tracked-source analysis at the preparation base. It is not evidence about currently running processes or installed Release bytes.

| Entry | Source path | Observed route and implication |
| --- | --- | --- |
| Desktop shortcut | `scripts/install_factory_studio_shortcut.ps1` | Creates the owner-facing launcher shortcut; an installed shortcut can be invoked outside the scoped updater. |
| PowerShell launcher | `scripts/launch_factory_studio.ps1` | Starts Godot with `--path <project>`; it has no verified common exclusion handshake. |
| Studio gateway | `level_factory/scripts/factory_studio_shell.gd`, `factory_core_gateway.gd` | GUI delegates operations through `OS.execute` to the Python launcher. |
| Python entry point | `level_factory/scripts/factory_core_launcher.py` | Exposes operations including `png-batch-run` and `png-batch-control`; direct terminal/task invocation can bypass the GUI wrapper. |
| Solver child | `src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py` | Starts `godot --headless --path <project> -s <bridge>` through `subprocess.Popen`; cancellation can terminate its own child tree. |
| ALPIX job | `factory_core_launcher.py`, `src/scrubbots_pixel_factory/alpix_batch.py` | The launcher reaches `run_csv_job`; renderer invocation uses a subprocess runner. |

A process snapshot cannot close the launch-after-snapshot race. PID reuse and missing executable/command-line metadata also prevent a PID-only assertion. A named mutex/file lock is cooperative; no evidence shows legacy deployed launchers/workers honor a new one, and direct launcher routes remain. Therefore no truthful source-only `WriterExclusionEstablished=$true` design is supported. To proceed later, the owner must authorize an operational exclusion boundary that prevents all Studio/worker starts for the full apply and rollback window, or a separately engineered and installed all-entrypoint enforcement change must be reviewed and proven before apply.

## Source SHA refresh and migration matrix

SHA-256 values below were freshly computed from tracked source files in this checkout. The manifest expected and installed columns are the last recorded R04 observations from `SB_LFX_018_R05_V13_CD_R04_PROSPECTIVE_MANIFEST_MIGRATION_DECISION_PACKET.md`; R06 did not reread owner-untracked `Release/` paths. Thus the R04 values are historical comparison data, not R06 current-state proof or authority.

| Controlled path | Manifest expected (R04) | Installed (R04) | Current source (R06) | R04 classification |
| --- | --- | --- | --- | --- |
| `level_factory/scripts/factory_core_launcher.py` | `563353c20c608e98484585db8322e423b9fc4641609c92dc4d83ee3fa160a5ea` | same | `60735cf39d632facca42919cbaee0aafb14a084d3d3d39ab55f268b0a44e2a4b` | SOURCE_UPDATE |
| `level_factory/scripts/factory_studio_exact_ui.gd` | `2ce9a247698ecd2c098def1c5986db2a90921af3566a8d1872d17456c5137457` | same | `7c4de3f4b716f13feade5bbb48529a754891fd82233d25c47ac96b1fadbe0a5e` | SOURCE_UPDATE |
| `scripts/launch_factory_studio.ps1` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | same | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | UNCHANGED |
| `level_factory/scripts/factory_studio_shell.gd` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | same | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | UNCHANGED |
| `level_factory/scripts/factory_studio_workspace_page.gd` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | same | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | UNCHANGED |
| `level_factory/scripts/factory_core_gateway.gd` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | same | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | UNCHANGED |
| `level_factory/project.godot` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | same | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | UNCHANGED |
| `src/scrubbots_pixel_factory/output/bundle.py` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | same | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | UNCHANGED |
| `src/scrubbots_pixel_factory/semantic/providers/registry.py` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | same | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | UNCHANGED |
| `src/scrubbots_pixel_factory/png_batch.py` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | same | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | UNCHANGED |
| `src/scrubbots_pixel_factory/studio_extensions.py` | `b5a5b6ec2ec969ddf3de9c2fd6fb536476440185b8bf458b0995662587be7ee9` | same | `6d2e51fdaf01700f3ab798933d129966269819d642980205294010bc5d41b2ad` | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py` | `640acc3804ae99e98623a046088e7c29f87201e8ee6dda828983b0427fca9a72` | same | `f3ebd2ec8439e1bf9424d129c892ab8c555d036799aa04f7f90ede4112d38a51` | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py` | `17f3a425d310eb5999dc147f1c15d14833ed353e014e4c7e3b7a8f7f36b59a25` | same | `d86617e377a38854533e4cb784cb752fcfbad4882a3ed0e9872d77dc08ad0dfb` | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | same | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | UNCHANGED |
| `src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py` | `cdc5521902433e5d9370fb3585bf5898974964fcac81aa207d35941765f201dc` | same | `6769c1aa26f66244cf1a527add20dd958c90dd65201abf02441eb081aeac527b` | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py` | `1f8776da86260ce27529b63213f4c632fe1cbb459197d49e3011ee0e3cb92bf0` | same | `d645bdb37897f466ff14f18a76fcaab6bdadaf7e92e422cacfbf894fb9b3ae97` | PROPOSED ADD; review required |
| `src/scrubbots_pixel_factory/supply_pipeline/verify.py` | `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2` | `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744` | `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3` | UNAPPROVED DRIFT; blocker |
| `src/scrubbots_pixel_factory/alpix_batch.py` | `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282` | same | `cea1af97f95de96d0a8c7187bafd4e2e68dd9fa2939f09be4d2a5c95d5b8185c` | PROPOSED ADD; review required |

R04 classified 8 planned source changes, 1 unapproved `verify.py` drift, and 9 unchanged entries. Three proposed overlay additions were `supply_exporter.py`, `verify.py`, and `alpix_batch.py`. R06 recomputed current source SHA-256 for all 18 controlled paths listed above. The currently installed `verify.py` bytes, manifest snapshots, and their freshness remain unverified in R06.

R04 reported six manifests with no `verify.py` overlay path or per-file receipt. Their six artifact hashes and per-manifest counts remain available in the linked R04 decision packet. R06 did not reopen those owner files. Any next migration must prospectively approve one exact forward manifest transition; it must never fabricate an earlier receipt or silently bless drift. The installer must re-preflight all 18 paths, all six manifests, and all actual current source/installed hashes immediately before any separately authorized operation.

## Native Godot route

Project `level_factory/project.godot` names the Studio main scene. The existing launcher invokes Godot against the project; the solver child does likewise in headless mode. The official Godot [command-line documentation](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html) describes `--path` as selecting a project and `--headless` as running the engine, while the [project organization documentation](https://docs.godotengine.org/en/4.7/tutorials/best_practices/project_organization.html) describes project-contained resource import. No documentation-backed option was found that proves parsing this project is write-free with respect to `.uid`, `.import`, `.godot`, or user cache/config. No command was run. Native source parse and installed GUI screenshots therefore remain unavailable without a narrowly approved owner write boundary. A future approval must name the exact generated paths to preserve/accept and separately authorize any installed GUI opening; one consent does not imply the other.

## Consolidated owner decision

Choose independently:

1. **Leave installation unchanged** and keep all gates open; or
2. **Authorize prospective review only** of a new migration limited to the exact 18-path matrix above and the three named additions. This does not authorize `-Apply`, settle current installed hashes, establish writer exclusion, or permit native project writes; a new preflight and explicit operation decision would still be required.
3. Separately, **authorize a bounded native Godot parse** against the canonical project, after reviewing the possibility of generated `level_factory/**/*.uid`, `*.import`, `level_factory/.godot/**`, and Godot user cache/config files. This does not authorize GUI launch or Release apply.
4. Separately, **authorize an owner-controlled no-start window** for all Studio and worker routes across a future apply plus rollback interval, or request an independently enforced all-entrypoint design before that interval can be claimed safe.

Until those decisions and technical checks exist, perform no install. The precise next action after owner response is to refresh the read-only manifest/source/installed hash matrix and decide whether a supported global exclusion boundary exists; if not, stop before apply.
