# SB-LFX-018 R05 M01 | GPT Independent Candidate-Button Lifecycle Source Audit V01

Date: 2026-10-16 Europe/Istanbul
Repository: `Sekiph82/ScrubBots-Level-Factory`
Prior GPT main: `4fa4f63db6009a6ad7ee698ec6a2370448c7a098`
Builder source/test/updater commit: `e7231bfbebd43a37896a7b84bdccb9a906731e65`
Final builder main: `2f79883ed93b7bf85e0bb7e48d8e4bfd26e7fabc`
**VERDICT: SOURCE FIX AND BUILDER FOCUSED GODOT PASS EVIDENCE ACCEPTED IN NARROW SCOPE; INSTALLED CONTROLLER HASH BUILDER VERIFIED, OWNER NATIVE AFTER CANDIDATE-CLICK/CONSOLE SMOKE OPEN. Full M01 owner startup and R05 game/production NOT CLOSED.**

## Independent code and publication audit
GPT independently fetched current private GitHub main and compared all paths against the previous GPT main. Exactly two normal descendant commits: `e7231bf` scoped product/test/updater, `2f79883` existing chronological builder log append. The source `level_factory/scripts/factory_studio_exact_ui.gd::_refresh_release_candidate_rows()` changes ONLY `child.free()` to `child.queue_free()` after `_release_candidate_rows.remove_child(child)`. This defers destruction until the event loop unwinds, preventing synchronous deletion of the `Button` currently emitting `pressed`; existing selection callbacks, preview, Pool backend and owner-accepted Release geometry are unchanged. This is a reasonable direct correction of the owner's actual stack `_refresh_release_candidate_rows:3753` <- `_select_release_candidate_id:3799`.

The changed existing `level_factory/tests/factory_studio_r07_five_slot_release_dashboard_suite.gd` exercises `Button.emit_signal("pressed")` on in-tree nine synthetic READY rows (not merely handler calls), awaits a frame, checks removed emitting row invalid, row count stays 9, selected preview identity, exact READ ONLY candidate-preview activity, repeated press, manage selection, Select All/Clear and tab switches. The suite also asserts no gateway preflight/upload/accept/reject/publish, solver, replay, batch or load-check calls. **Minor test-strength nuance:** its one equality `row_instance_ids.size()==row_instance_ids.duplicate().size()` does NOT check uniqueness, because copying an array always retains length; the existing actual nine-row count/removed emitting instance assertions do establish more relevant row-lifecycle facts, and this weak assertion is not grounds alone to block the owner native smoke. If this suite is edited again, replace that clause with actual set uniqueness or comparison against distinct ID values, without a new micro-task or broad regression.

Builder's local Godot 4.7.2 absolute binary + async in-memory stdout/stderr run reported **exit 0 in 2,660ms**, literal suite-generated `SB-LFX-018-C001-R02-R05-R09-R02-R04-R07 five-slot release dashboard PASS`, empty stderr, no Godot SCRIPT ERROR. GPT inspected source/test changes but did NOT execute Windows Godot. Test SHA at builder checkpoint `bcc57ec080f8602ecdadf9d86d2db32eb5a306a2`.

## Installed controller and retained backups (builder metadata, not direct Windows measurement)
The existing one-controller PowerShell updater was pinned to the known M01 installed controller/manifest, preserved prior R04 and M01 receipt identities and added a third receipt with a narrowly bounded fresh rollback pair. Builder reports PowerShell 7 preflight and conditional `-Apply` PASS, zero installed Studio process at writing time, no shortcut/project/launcher/icon changes, all **2,316** managed entries and nine overlay paths intact, other **2,315** SHA pairs unchanged:
- Installed controller SHA256 `dad6cde3e7b2b1ba1ecdd7d3fb868bc067681bda1e1be18f789216f5e0841c58`.
- Installed manifest SHA256 `b9307e3de98d69fb4c48757acb5fd5fc030b7a5645f8171e04f1c52f1c557f2b`.
- R04 + M01 + M01 v2 rollback pairs **six files, total 1,957,031 bytes**. New v2 controller `.r05-m01-rollback-v2-controller-11d3f59f3340.bin` 198,621 B and manifest `.r05-m01-rollback-v2-manifest-94c6f6b51dc2.json` 455,816 B. Two earlier pairs unchanged; no remaining stages per builder. **Keep all six until real owner error-free smoke**, and don't run rollback or cleanup while Studio is open.

Builder's local Git sync, free-disk/footprint, absence of temp or CI, and exact installed hashes are builder-reported; GPT verified GitHub changed paths and manual-only workflow, not the owner's disk. No GitHub Actions/CI requested or used in this independent audit.

## Genuine owner acceptance gate
Previous owner's screenshot exposed a real `ERROR: Object is locked and can't be freed` / `SCRIPT ERROR: Attempted to free a locked object` on normal Release candidate click. That old screenshot is **before the current patched installed controller** and cannot close the new owner runtime gate. Owner should manually open the **same existing Desktop ScrubBots Factory Studio shortcut**, view Release Pool, click ONE candidate to preview (read-only, not Accept/Reject/Preflight/Upload/Publish), and report: (1) any Godot terminal `ERROR`/`SCRIPT ERROR`, (2) whether READY levels remain 9, (3) whether PIXEL ART / LEVEL FACTORY / RELEASE POOL tabs navigate normally. A screenshot/terminal excerpt if an error remains. **Until owner confirms an error-free click and startup, M01 OWNER STARTUP/SMOKE is NOT VERIFIED; the approved geometry and earlier Nil-to-Dictionary source repair remain scoped PASS.**

Current-game Scrubbots main/CPX-002 solver/replay/load-check, independent producer identity and native NTFS atomic handles remain OPEN and are not in scope. No actual game or 140 PNG batch, R2/prod, provider/CI, or protected owner file deletion.
