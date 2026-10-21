# SB-LFX-018 R05 V13-C/D R04 | Prospective Release Manifest Migration Decision Packet

Document role: READ-ONLY OWNER DECISION PACKET
Prepared: 2026-10-21 (Europe/Istanbul)
Repository: `Sekiph82/ScrubBots-Level-Factory`
Preparation base: `755ea8726d343f29c2a543e126f7871b79c55c54`
Scope: prospective decision about the existing Factory Studio scoped-overlay manifest only

## Decision boundary

This packet records the currently observed Release state and the exact scope that a future, prospective owner decision could review. It is not an install approval, an old receipt, evidence that a historical install was approved, or permission to run the installer. No manifest bytes, Release application files, job, Pool, owner PNG, or live process were changed or inspected through an application invocation for this packet.

The present disposition remains **`INSTALL_BLOCKED_MANIFEST_DRIFT`**. The installed `verify.py` digest is known to match a published historical source revision, but no manifest overlay path or per-file receipt binds that file to an approved transaction. Source provenance cannot substitute for installation authority.

## Current manifest authority and exact `verify.py` hashes

The main installed manifest is `.factory-studio-install-manifest.json`, SHA-256 `9e5bda945b9f86606c5afe484e6cf7cc66c7f5a69744795250fa8631fb5a3f3d`. Its fresh read-only inventory contains 2,318 managed paths, 20 overlay paths, and 17 overlay receipts. The expected, installed, and current repository-source hashes for `src/scrubbots_pixel_factory/supply_pipeline/verify.py` are:

| Authority | SHA-256 |
| --- | --- |
| Manifest expected | `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2` |
| Installed bytes | `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744` |
| Current source bytes | `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3` |

The current source digest is associated with R03 source commit `e08f3fc8167baf8ba44d213ae9b0840698d2f33f`. The installed digest was previously identified as a CRLF checkout of commit `17643de6756ba3d9552351eb237db19bd8d0c269`; that historical correspondence still does not authorize installation. The previous report that `verify.py` is absent from all six manifests was builder-reported; the following exact six local artifacts were re-read read-only for this packet, and none names `verify.py` in `overlayPaths` or binds it in an overlay receipt:

| Manifest artifact | SHA-256 | Managed paths | Overlay paths | Receipts | `verify.py` overlay paths / file receipts |
| --- | --- | ---: | ---: | ---: | ---: |
| `.factory-studio-install-manifest.json` | `9e5bda945b9f86606c5afe484e6cf7cc66c7f5a69744795250fa8631fb5a3f3d` | 2318 | 20 | 17 | 0 / 0 |
| `.factory-studio-install-manifest.json.r04-backup-a527041` | `0c885ee848c93c9a2ec50e485838c1209d6005cfdd111249c46bd16525393cc4` | 2077 | 1 | 1 | 0 / 0 |
| `.factory-studio-install-manifest.json.r04-r01-backup-54105bc` | `de434a436f6dff409c5cccb4c27f1e5eb798eeb1a333f9d6c0b3cecc8420cdce` | 2077 | 1 | 1 | 0 / 0 |
| `.r04-ui-overlay-rollback-manifest-c7ab656d263a.json` | `c7ab656d263a5c5dbf77f0400a41da45c86ca8f830272872923f19251e300995` | 2316 | 9 | 1 | 0 / 0 |
| `.r05-m01-rollback-manifest-56c9f32518fe.json` | `56c9f32518fe01b2354942600c8d19662cab0713a23b42551304fccfbc0493eb` | 2316 | 9 | 1 | 0 / 0 |
| `.r05-m01-rollback-v2-manifest-94c6f6b51dc2.json` | `94c6f6b51dc28e1c1208e04146f0573760ca6af03114657cff0e7b0b9a7a6ec7` | 2316 | 9 | 2 | 0 / 0 |

The rollback manifests are recovery snapshots, not receipts authorizing this transition.

## Fresh bounded overlay preflight

This was a read-only comparison of the exact 18 managed paths listed by the scoped installer against the main manifest, installed files, and current repository files. No installer process query, file write, or `-Apply` was run.

| Path | Manifest SHA-256 | Installed SHA-256 | Source SHA-256 | Overlay / receipts | Result |
| --- | --- | --- | --- | --- | --- |
| `level_factory/scripts/factory_core_launcher.py` | `563353c20c608e98484585db8322e423b9fc4641609c92dc4d83ee3fa160a5ea` | `563353c20c608e98484585db8322e423b9fc4641609c92dc4d83ee3fa160a5ea` | `60735cf39d632facca42919cbaee0aafb14a084d3d3d39ab55f268b0a44e2a4b` | 1 / 3 | SOURCE_UPDATE |
| `level_factory/scripts/factory_studio_exact_ui.gd` | `2ce9a247698ecd2c098def1c5986db2a90921af3566a8d1872d17456c5137457` | `2ce9a247698ecd2c098def1c5986db2a90921af3566a8d1872d17456c5137457` | `7c4de3f4b716f13feade5bbb48529a754891fd82233d25c47ac96b1fadbe0a5e` | 1 / 8 | SOURCE_UPDATE |
| `scripts/launch_factory_studio.ps1` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | `7e11da14f13d4fd9638e4c3eb118d1256f939c2a9f2c875ad2d3b77a225f130d` | 1 / 1 | UNCHANGED |
| `level_factory/scripts/factory_studio_shell.gd` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | `e36e7b008c898ab1077044f1862ce2c03a502e5fd498f232a08308bcf6d8d028` | 1 / 2 | UNCHANGED |
| `level_factory/scripts/factory_studio_workspace_page.gd` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | `71b14d9aee4436949bc5728520648dbfeea997329d7e90b117437e6de5bdd2fc` | 1 / 1 | UNCHANGED |
| `level_factory/scripts/factory_core_gateway.gd` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | `2b0a11c3ca42d8e9fb6b60db9fdd676d03d532834030c26a284fe3ae209f185a` | 1 / 1 | UNCHANGED |
| `level_factory/project.godot` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | `4adb4b9b939d8af178516e86a170ab1e8d725f32d8b4d3f1b8464e4759c655c7` | 1 / 1 | UNCHANGED |
| `src/scrubbots_pixel_factory/output/bundle.py` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | `d12e0092e3d9d06e63a5a3189db424ebdb9182e6274e0e9448052703c7e453cd` | 1 / 1 | UNCHANGED |
| `src/scrubbots_pixel_factory/semantic/providers/registry.py` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | `b547d6bc1a18c7d5a447d88b6a6641f37b8df7cefb99a1837ad6c2cba4fabedf` | 1 / 1 | UNCHANGED |
| `src/scrubbots_pixel_factory/png_batch.py` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | `c58579e7ae7bb14bdbdd37e4a6896fe857feba436d39d131ce35701197f18d48` | 1 / 4 | UNCHANGED |
| `src/scrubbots_pixel_factory/studio_extensions.py` | `b5a5b6ec2ec969ddf3de9c2fd6fb536476440185b8bf458b0995662587be7ee9` | `b5a5b6ec2ec969ddf3de9c2fd6fb536476440185b8bf458b0995662587be7ee9` | `6d2e51fdaf01700f3ab798933d129966269819d642980205294010bc5d41b2ad` | 1 / 6 | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py` | `640acc3804ae99e98623a046088e7c29f87201e8ee6dda828983b0427fca9a72` | `640acc3804ae99e98623a046088e7c29f87201e8ee6dda828983b0427fca9a72` | `f3ebd2ec8439e1bf9424d129c892ab8c555d036799aa04f7f90ede4112d38a51` | 1 / 1 | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py` | `17f3a425d310eb5999dc147f1c15d14833ed353e014e4c7e3b7a8f7f36b59a25` | `17f3a425d310eb5999dc147f1c15d14833ed353e014e4c7e3b7a8f7f36b59a25` | `d86617e377a38854533e4cb784cb752fcfbad4882a3ed0e9872d77dc08ad0dfb` | 1 / 1 | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | `a5813f3aee5f9373b1f45c4b0bc045d263040cb64f37472a5f2bc61d6130b4ad` | 1 / 6 | UNCHANGED |
| `src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py` | `cdc5521902433e5d9370fb3585bf5898974964fcac81aa207d35941765f201dc` | `cdc5521902433e5d9370fb3585bf5898974964fcac81aa207d35941765f201dc` | `6769c1aa26f66244cf1a527add20dd958c90dd65201abf02441eb081aeac527b` | 1 / 2 | SOURCE_UPDATE |
| `src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py` | `1f8776da86260ce27529b63213f4c632fe1cbb459197d49e3011ee0e3cb92bf0` | `1f8776da86260ce27529b63213f4c632fe1cbb459197d49e3011ee0e3cb92bf0` | `d645bdb37897f466ff14f18a76fcaab6bdadaf7e92e422cacfbf894fb9b3ae97` | 0 / 0 | SOURCE_UPDATE; AUTHORIZED ADDITION REVIEW REQUIRED |
| `src/scrubbots_pixel_factory/supply_pipeline/verify.py` | `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2` | `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744` | `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3` | 0 / 0 | UNKNOWN DRIFT; INSTALL BLOCKER |
| `src/scrubbots_pixel_factory/alpix_batch.py` | `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282` | `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282` | `cea1af97f95de96d0a8c7187bafd4e2e68dd9fa2939f09be4d2a5c95d5b8185c` | 0 / 0 | SOURCE_UPDATE; AUTHORIZED ADDITION REVIEW REQUIRED |

Summary from these exact rows: 18 scoped entries; 8 source updates with manifest-matching installed bytes (six existing overlay paths and two proposed overlay additions); 1 unapproved `verify.py` manifest drift; 9 unchanged. Three overlay additions are proposed by the existing exact installer allowlist: `supply_exporter.py`, `verify.py`, and `alpix_batch.py`. The `verify.py` addition cannot proceed without an exact prospective owner decision and a separately reviewed safe migration; no decision may retroactively legitimize a prior install.

## Dependency and transaction scope

The proposed eight updates are the current source versions of the launcher, exact Studio UI, Studio extensions, solver budget, supply optimizer, solver, supply exporter, and ALPIX batch module. The existing call graph uses the launcher to invoke Studio/batch entry points; `studio_extensions.py` imports the supply optimizer/exporter and `verify.py`; the optimizer uses the solver budget and solver; the Studio launcher imports the ALPIX discovery/generation/job functions. The manifest drift in `verify.py` blocks replacing this closure as one authorized deployment. No runtime package, workflow, network provider, credential, or dependency change is part of R04.

R04 source-only changes are limited to `scripts/scoped_overlay_transaction.psm1`, `scripts/install_factory_studio_scoped_overlay.ps1`, and `tests/unit/test_scoped_overlay_transaction.ps1`. They make the cleanup-pending wrapper result visible, perform a fresh synthetic-testable process snapshot before replacement, rehash each target immediately before replacement, and refuse to claim quiescence without an actual exclusive-writer control. The installed wrapper supplies no such control, so `-Apply` reports `PROCESS_QUIESCENCE_UNPROVEN`; a process snapshot cannot close the remaining TOCTOU window. These source helpers do not authorize the Release files listed above.

## Rollback, process, and owner acceptance evidence

- The R03 rollback matrix is executable only through an in-memory adapter. It covers staged writes, atomic replacement faults, manifest replacement, verification, restore failures, byte/hash restoration, and evidence retention. Physical `File.Replace` behavior and Release rollback remain **NOT VERIFIED**.
- R04 focused synthetic coverage checks wrapper mapping of `COMMITTED`, `COMMITTED_CLEANUP_PENDING`, `NO_OP`, and error outcomes; a late writer with a child PID; CIM failure; missing process metadata; target bytes unchanged on blocked paths; and the unclosed TOCTOU gate. No live process was enumerated, started, stopped, suspended, attached to, or probed.
- The latest prior builder evidence reports the owner job as COMPLETE (140 total: 102 READY, 4 FAILED, 34 REJECTED, 0 remaining) with job-file SHA-256 `33c11885032f9b9b6050ea642c4870e04e8424dacc00de749b51234ce9f94193` and state digest `56823da1561858e6275e180b0c766b46daacf6f735e7200cfce47b0369d98490`; the Release Pool count was 131 JSON files with tree digest `e227c95f85635a48522dbdd5aefeb2ead51f2e25070fb8f4b315746ebbc9a81`. Those values are carried forward as prior builder-reported baselines and were **not** re-read or independently rehashed in R04. No job, Pool, source PNG, or image was opened or changed for this packet.
- No owner-native three-screen acceptance is evidenced by this packet. The exact `PIXEL ART | LEVEL FACTORY | RELEASE POOL` installed GUI screenshots, interaction/responsiveness proof, and real same-PID/child 240-second soft to 480-second total lifecycle remain open. The last recorded R03 status is `INSTALLED_GUI_OPEN`; no current process state is asserted here.
- No read-only-safe Godot 4.7.2 project parser route was established in prior R03 work: project invocation can create/update `.uid`, `.import`, or `.godot` cache files. R04 therefore did not launch Godot. `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK` remains.

## Prospective owner decision choices

1. **Keep the current installation unchanged.** Accept the continued `INSTALL_BLOCKED_MANIFEST_DRIFT` state and leave all existing Release bytes/manifests in place.
2. **Prospectively authorize review of one exact controlled manifest migration.** Review and approve the specific source/installed/expected SHA matrix and the three proposed overlay additions above. Such a decision would authorize only the exact reviewed scope after a separate safety review; it would not be an old receipt, would not automatically approve `verify.py` drift, and would not waive process quiescence, Godot cache, installation, or native GUI gates.

No choice has been made in this packet. Do not edit the manifest, add trusted hashes, copy files, run `-Apply`, or describe this document as release approval. Any later controlled apply requires explicit prospective owner authority, proven write safety, complete process handling, and separate native acceptance.
