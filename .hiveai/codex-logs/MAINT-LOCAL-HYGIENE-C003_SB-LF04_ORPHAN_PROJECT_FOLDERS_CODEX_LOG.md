# MAINT-LOCAL-HYGIENE-C003 — Preserve, Merge and Remove SB-LF04 Orphan Project Folders

Document role: CODEX BUILDER LOG

## Session start and synchronization preflight

- Starting timestamp: 2026-10-03 17:59:52 +03:00 (Europe/Istanbul).
- Canonical persistent root: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; git rev-parse --show-toplevel confirmed this exact root.
- Repository identity: Sekiph82/ScrubBots-Level-Factory; origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git; branch main.
- Persistent main starting HEAD: 7c6051589d0a95fc785d7f182ccd0d7f8d7013ce; fetched origin/main: 4324e792be5000cb7f757f43b56302015ab4ffd; ahead/behind: 0/25.
- Persistent checkout status snapshot before any merge/deletion: 178 changed paths (123 tracked modified, 55 untracked); extensive pre-existing owner-local test changes, generated .uid sidecars and the three owner-authorized target worktree directories. Eighteen existing stashes. Eleven registered worktrees at snapshot time. No persistent file, branch, stash or worktree was changed during preflight/classification, except that the subsequent authorized MAINT temp worktree was registered.
- git fetch origin main --prune succeeded. origin/main:TASKS.md sets Current Task to MAINT-LOCAL-HYGIENE-C003, status OWNER_AUTHORIZED / PRESERVE_MERGE_THEN_DELETE_ALL_THREE.
- Read current GitHub prompt .hiveai/prompts/MAINT-LOCAL-HYGIENE-C003_SB-LF04_ORPHAN_PROJECT_FOLDERS_PROMPT.md, current TASKS.md, root AGENTS.md, and GOVERNANCE.md. No tracker, audit, prompt or prior log was edited.
- Clean integration/log worktree created at %TEMP%\ScrubBots-Level-Factory\MAINT-LOCAL-HYGIENE-C003, branch codex/maint-local-hygiene-c003, starting from origin/main 4324e792be5000cb7f757f43b56302015ab4ffd. It is the only new worktree for this task.

## Pre-deletion target inventory and comparison

All three exact paths are normal directories (not symlinks, junctions or reparse points) and registered Git worktrees of this same canonical repository. Each has the canonical origin URL. Each is detached (git branch --show-current is empty); all have zero commits ahead of current origin/main, so their histories are ancestors/superseded by canonical main. Their local trees contain committed historical project files, but no target-only commits or tracked modifications. Stash list count is 18 in each linked worktree because stashes are shared in the common repository; no stash was applied or altered. Shared local branch refs are main and codex/sb-lf07-r04-selective; none is unique to these detached targets.

### Target 1 — Scrubbots - Pixel Art Generator-SB-LF04-001

- Original state: registered worktree; origin canonical; detached HEAD 86c0b828ceaa307374f267feac41021efefa5406; origin/main is 621 commits ahead / target 0 commits ahead; unique commits: none; staged/tracked diffs: none; untracked status: 50 .uid files only.
- Inventory: 1,335 files, including 957 meaningful tracked source/config/docs/tests/data files from the superseded ancestor commit; 314 ignored generated files (principally .godot editor/import cache, Python __pycache__, and .pytest_cache).
- All 50 untracked sidecars are generated Godot script UID sidecars; each has a corresponding .gd source file. They are not present in current canonical origin/main and are not referenced outside their sidecar files anywhere in the target. Their UID set exactly matches target 3's sidecar set. They differ from persistent root's independently generated, untracked sidecars; those root files remain untouched. No unique legitimate source/evidence was found.
- Disposition before deletion: REDUNDANT_READY_TO_DELETE. Preservation mapping: none. Integration commit: none.

Untracked UID path inventory (identical in targets 1 and 3):
- `level_factory/scripts/factory_core_gateway.gd.uid`
- `level_factory/scripts/factory_studio_art_editor.gd.uid`
- `level_factory/scripts/factory_studio_art_preview.gd.uid`
- `level_factory/scripts/factory_studio_art_revalidation.gd.uid`
- `level_factory/scripts/factory_studio_batch_import.gd.uid`
- `level_factory/scripts/factory_studio_candidates.gd.uid`
- `level_factory/scripts/factory_studio_comparison.gd.uid`
- `level_factory/scripts/factory_studio_cost.gd.uid`
- `level_factory/scripts/factory_studio_dashboard.gd.uid`
- `level_factory/scripts/factory_studio_evidence_panel.gd.uid`
- `level_factory/scripts/factory_studio_failures.gd.uid`
- `level_factory/scripts/factory_studio_import_validation.gd.uid`
- `level_factory/scripts/factory_studio_import.gd.uid`
- `level_factory/scripts/factory_studio_library.gd.uid`
- `level_factory/scripts/factory_studio_navigation.gd.uid`
- `level_factory/scripts/factory_studio_pipeline.gd.uid`
- `level_factory/scripts/factory_studio_presets.gd.uid`
- `level_factory/scripts/factory_studio_puzzle_config_gate.gd.uid`
- `level_factory/scripts/factory_studio_readiness.gd.uid`
- `level_factory/scripts/factory_studio_reproduce.gd.uid`
- `level_factory/scripts/factory_studio_revisions.gd.uid`
- `level_factory/scripts/factory_studio_search.gd.uid`
- `level_factory/scripts/factory_studio_session.gd.uid`
- `level_factory/scripts/factory_studio_shell.gd.uid`
- `level_factory/scripts/factory_studio_similarity.gd.uid`
- `level_factory/scripts/factory_studio_target_controls.gd.uid`
- `level_factory/scripts/factory_studio_workspace_page.gd.uid`
- `level_factory/tests/factory_studio_action_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_art_revalidation_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_batch_import_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_candidate_review_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_comparison_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_cost_center_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_dashboard_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_exact_reproduce_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_exact_reproduce_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_failures_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_import_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_import_validation_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_library_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_pipeline_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_presets_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_puzzle_config_gate_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_readiness_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_revisions_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_runtime_suite.gd.uid`
- `level_factory/tests/factory_studio_search_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_session_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_similarity_r01_integration_suite.gd.uid`
- `level_factory/tests/factory_studio_truth_separation_integration_suite.gd.uid`

### Target 2 — Scrubbots - Pixel Art Generator-SB-LF04-001-R01

- Original state: registered worktree; origin canonical; detached HEAD d91e330d6ea0379db7f44d8567d992d4c406054e; origin/main is 614 commits ahead / target 0 commits ahead; unique commits: none; staged/tracked/untracked diffs: none.
- Inventory: 1,058 files, including 959 meaningful tracked source/config/docs/tests/data files from the superseded ancestor commit; 81 ignored generated files, principally Python __pycache__ and .pytest_cache.
- No unique legitimate files, branch, commit, evidence or stash found.
- Disposition before deletion: REDUNDANT_READY_TO_DELETE. Preservation mapping: none. Integration commit: none.

### Target 3 — Scrubbots - Pixel Art Generator-SB-LF04-001-R01-VERIFY

- Original state: registered worktree; origin canonical; detached HEAD 3fe47c0c7f6ba6e922c1de359f2dcef7409d27a2; origin/main is 615 commits ahead / target 0 commits ahead; unique commits: none; staged/tracked diffs: none; untracked status: same 50 .uid sidecars listed under target 1.
- Inventory: 1,342 files, including 962 meaningful tracked source/config/docs/tests/data files from the superseded ancestor commit; 315 ignored generated files (principally .godot editor/import cache, Python __pycache__, and .pytest_cache).
- The 50 sidecars have matching .gd source files, are absent from canonical origin/main, and have zero references outside sidecars within the target. No unique legitimate source/evidence was found.
- Disposition before deletion: REDUNDANT_READY_TO_DELETE. Preservation mapping: none. Integration commit: none.

No P1/P2 or other unrelated worktree, branch or stash was modified. No product/config/docs/tests/data/evidence were copied because no unique legitimate work was found. No tests or compile checks were run because no product change was integrated; post-deletion checks are recorded below after execution.

## Deletion and final verification

Deletion has not yet occurred. This log records the required pre-deletion snapshot; append the exact worktree removal commands, per-target absence checks, worktree registration check, collateral status comparison, final GitHub publication SHA and push verification after the three authorized targets are removed.

## Worktree path reconciliation before deletion

- The first exact-path deletion precheck stopped safely before removing anything because git worktree list reported stale former sibling paths (for example C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-SB-LF04-001) instead of the three prompt-authorized nested target paths. The prompt-authorized targets are nested under the canonical root. None of the former sibling paths exists.
- Read-only inspection of each exact target .git pointer and its corresponding .git/worktrees/<id>/gitdir showed the same registered worktree metadata: each nested target points to the shared repository’s worktree metadata, while that metadata's back-pointer still names the now-absent old sibling <path>/.git. Thus the three exact target folders are moved/relocated registered worktrees with stale registration paths, not independent clones. The four stale git worktree list entries include a separate SB-LF07-R04 path and remain outside this task unless reconciliation proves otherwise.
- No files were removed by the stopped precheck. Persistent root files, target contents, stashes and worktree metadata were unchanged at this point. Next: repair only the three exact target worktree registrations with git worktree repair <exact-authorized-target-path>, verify their registrations point to the authorized nested paths and status is unchanged, then remove those exact worktrees as this prompt directs.
- Reconciliation command: git worktree repair with exactly the three authorized nested paths. The first invocation printed gitdir incorrect diagnostics while repairing and exited 0; immediate inspection confirmed all three metadata back-pointers now resolve to the exact nested target .git files and git worktree list names the nested target paths. A second identical repair completed cleanly with exit 0. Target file/status inventories and HEADs remained unchanged (50 untracked .uid sidecars / clean / 50 sidecars respectively). No other stale entry, including unrelated SB-LF07-R04, was modified.
- With exact registrations repaired, deletion will use git worktree remove for each of the three exact authorized paths; --force is used only for targets 1 and 3 because their only changes are the inventoried generated UID sidecars. Target 2 is clean and is removed without force.

## Deletion, collateral checks and publication (2026-10-03 18:09:59 +03:00, Europe/Istanbul)

- Exact registration repair and removal chronology: after git worktree repair corrected the three stale back-pointers, git worktree list --porcelain showed each exact nested prompt target registered at its required path. git worktree remove --force <target-1> and git worktree remove <target-2> and git worktree remove --force <target-3> all exited 0. Force was limited to target 1 and target 3, whose only untracked contents were the verified generated .uid sidecars; target 2 had clean status. These were the only three Desktop directories removed.
- Final checks after removal: Test-Path returned false for each exact target; git worktree list --porcelain contains no registration for any of the three. Disposition: target 1 REDUNDANT_AND_DELETED; target 2 REDUNDANT_AND_DELETED; target 3 REDUNDANT_AND_DELETED. No unique product/evidence files or commits required preservation; no integration commit exists.
- Canonical persistent root collateral check: root still exists at the exact expected path and git rev-parse --show-toplevel identifies Sekiph82/ScrubBots-Level-Factory; origin remains canonical; branch main, HEAD 7c6051589d0a95fc785d7f182ccd0d7f8d7013ce, origin/main 4324e792be5000cb7f757f43b56302015ab4ffd, divergence 0 ahead / 25 behind. Owner-local status decreased from 178 to 175 paths, exactly accounting for the three removed untracked worktree directories; all remaining owner changes were left alone. Stash count remains 18. All pre-existing unrelated worktree HEADs remain unchanged; the only additions/removals were this MAINT worktree and the three authorized targets. The unrelated pre-existing prunable SB-LF07-R04 registration remains unchanged and does not point to any target.
- Canonical verification in the clean MAINT worktree: governance guard python -m pytest -q --tb=short tests/unit/test_sb_lf00_007_governance_authority.py::test_project_status_and_active_task_contract_are_exact passed (1 passed in 0.33s before final sync; 1 passed in 0.08s after final sync). python -m compileall -q src tests passed. git diff --check passed. godot_console.exe --headless --editor --path level_factory --quit completed successfully (Godot 4.7.2; project scan, class registration and editor layout completed).
- A final fetch advanced origin/main one commit from 4324e792be5000cb7f757f43b56302015ab4ffd to c2ce70c03f9706058e6bac6823107dc421d5740f; the only incoming path was protected TASKS.md, whose authority still names MAINT-LOCAL-HYGIENE-C003. The authorized temp worktree fast-forwarded normally to that SHA. The post-sync tracker guard passed. No TASKS change was authored.
- Correction to initial worktree count above: the original git worktree list contained 12 registrations (including the three targets), not 11. After creating the MAINT temp worktree and removing exactly the three targets, it lists 10 entries including the still-active MAINT temp worktree. This count correction does not change the fact that all unrelated pre-existing worktree paths/HEADs remain unchanged.
- Log-only change; no product dependency/license/network/offline/source-art changes. Staging is limited to this builder log. Append the final log commit SHA, normal push result, remote ref verification and final worktree status after publication.

## Published builder-log verification and record correction (2026-10-03 18:13:34 +03:00, Europe/Istanbul)

- Correction: the initial log-commit diff rendered one literal leading backslash before the starting origin/main SHA. The correct SHA throughout the preflight was 4324e792be5000cb7f757f43b56302015ab4ffd; the erroneous rendered text was not a Git reference or repository change. This append corrects the evidence without rewriting prior log history.
- First log-only commit c73a878c8d400943a10ad403dda470bd0da72638 was pushed using normal non-force git push origin HEAD:main. Push reported c2ce70c..c73a878 HEAD -> main. Subsequent git fetch origin main --prune, git rev-parse HEAD, git rev-parse origin/main, and git ls-remote origin refs/heads/main all confirmed local/remote/live main equality at c73a878c8d400943a10ad403dda470bd0da72638 (0 ahead / 0 behind).
- The only changed tracked path in the first publication was this maintenance builder log. No unique target content was staged or committed. The required task targets were all absent and unregistered at that verified publication point.
- This append is the final evidence correction/publication update. The repository remains an implementation-builder handoff; no audit or acceptance claim is made.
