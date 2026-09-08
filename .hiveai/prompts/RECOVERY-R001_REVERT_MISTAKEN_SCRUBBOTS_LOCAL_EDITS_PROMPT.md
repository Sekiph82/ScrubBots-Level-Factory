# RECOVERY-R001 — Revert Mistaken ScrubBots Local Edits

Document role: CODEX RECOVERY PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor and tracker owner: ChatGPT  
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Wrongly modified local repository: `C:\Users\sekip\Desktop\ScrubBots`

## Objective

Revert **only** the local edits that Codex introduced by mistake in the previous interrupted session inside the main SCRUBBOTS repository.

Do not implement any SCRUBBOTS feature.
Do not continue M19-C001.
Do not sync, reset, restore, clean, commit, or push the SCRUBBOTS repository as part of the rollback.

The worktree was already dirty before the mistaken session. Preserving every pre-existing user/agent change is mandatory.

## Evidence from the interrupted session

The mistaken session recorded source edits to exactly these four files:

1. `scripts/gameplay/dispatch/production_target_access.gd`
2. `scripts/gameplay/targeting/target_selector.gd`
3. `tests/support/access_query_double.gd`
4. `tests/support/dispatch_routing_double.gd`

The transcript recorded a combined edit summary of `+110 -31`.

No commit or push of these mistaken edits was recorded.

## Absolute safety rules

DO NOT run any of the following against `C:\Users\sekip\Desktop\ScrubBots`:

- `git reset --hard`
- `git restore .`
- `git checkout -- .`
- `git clean`
- `git stash`
- `git pull`
- `git merge`
- `git rebase`
- any command that replaces an entire dirty file merely with HEAD/origin content
- any commit or push

Do not touch `project.godot` or any file other than the four explicitly listed above.

Do not assume that a current diff in one of the four files belongs entirely to the mistaken session.

## Required rollback method

Use a **surgical hunk-level/manual reversal** of only the changes listed below.

Before changing anything, capture and place in the recovery log:

- `git -C 'C:\Users\sekip\Desktop\ScrubBots' rev-parse --show-toplevel`
- `git -C 'C:\Users\sekip\Desktop\ScrubBots' branch --show-current`
- `git -C 'C:\Users\sekip\Desktop\ScrubBots' rev-parse HEAD`
- `git -C 'C:\Users\sekip\Desktop\ScrubBots' status --short`
- `git -C 'C:\Users\sekip\Desktop\ScrubBots' diff -- <each of the four files>`

Do not fetch/pull/synchronize the ScrubBots repo. This is local worktree recovery only.

### A. production_target_access.gd

Remove only the mistaken-session additions/behavior and restore the pre-session behavior shown below.

Remove these added preloads:

- `BoardState = preload("res://scripts/gameplay/board/board_state.gd")`
- `RouteResult = preload("res://scripts/gameplay/routing/route_result.gd")`
- `RouteValidator = preload("res://scripts/gameplay/routing/route_validator.gd")`

Restore `_init(...)` to direct assignment:

```gdscript
func _init(routing_system, routing_access, board, origin: Vector2 = Vector2.ZERO) -> void:
    _routing_system = routing_system
    _routing_access = routing_access
    _board = board
    _origin = origin
```

Restore `set_origin` to:

```gdscript
func set_origin(origin: Vector2) -> void:
    _origin = origin
    _last_index = -1
    _last_route = null
```

Remove the mistaken-session `is_coherent_with(...)` function.

Restore `is_targetable` to the pre-session behavior:

```gdscript
func is_targetable(index: int) -> bool:
    if _routing_system == null or _board == null:
        return false
    var req = RouteRequest.for_target(_board, _origin, index)
    if req == null:
        return false
    var r = _routing_system.compute_route(req, _board, _routing_access)
    if r != null and r.success:
        _last_index = index
        _last_route = r
        return true
    return false
```

Restore `consume_route` to:

```gdscript
func consume_route(index: int):
    if index == _last_index:
        return _last_route
    return null
```

Remove the mistaken-session helper functions:

- `_clear_memo()`
- `_clear_binding()`
- `_is_valid_bundle(...)`

Preserve every unrelated pre-existing local change in this file.

### B. target_selector.gd

Remove only this mistakenly added function and its accompanying comment:

```gdscript
## Read-only exact bundle coherence for orchestration callers. The dispatcher
## must use the same BoardState and ReservationState that this selector was
## initialized with; dimensions/content equality is not sufficient.
func is_bound_to(board, reservation_state) -> bool:
    return _bound and _board != null and _reservations != null \
            and _board == board and _reservations == reservation_state
```

Preserve every other local change.

### C. access_query_double.gd

Remove only these mistakenly added fields:

```gdscript
var on_set_origin: Callable = Callable()
var _coherence_board = null
var _coherence_routing_system = null
var _coherence_routing_access = null
```

Remove only these mistakenly added functions:

```gdscript
func configure_coherence(board, routing_system, routing_access) -> void:
    _coherence_board = board
    _coherence_routing_system = routing_system
    _coherence_routing_access = routing_access

func is_coherent_with(board, routing_system, routing_access) -> bool:
    return _coherence_board == board and _coherence_routing_system == routing_system \
            and _coherence_routing_access == routing_access

func set_origin(_origin: Vector2) -> bool:
    if on_set_origin.is_valid():
        on_set_origin.call()
    return true

func consume_route(_index: int):
    return null
```

Also remove the mistaken-session explanatory comments that belong specifically to those functions.

Preserve every unrelated pre-existing local change.

### D. dispatch_routing_double.gd

Remove only:

```gdscript
var on_compute: Callable = Callable()
```

and remove only this callback block from `compute_route(...)`:

```gdscript
if on_compute.is_valid():
    on_compute.call()
```

Do not alter the existing `mode`, `call_count`, or other pre-session behavior.

## Verification after rollback

After surgical reversal:

1. Run `git diff --` separately for each of the four files.
2. Compare the remaining diff carefully with the pre-session evidence and the exact reversal list above.
3. If any remaining diff exists, **do not automatically remove it**. Treat it as potentially pre-existing and preserve it unless it is clearly one of the mistaken-session hunks listed above.
4. Run `git status --short`.
5. Confirm no files outside the four targets were modified by this recovery.
6. Do not run M19 feature tests as proof of implementation. This is rollback, not implementation.
7. Do not commit or push the ScrubBots repository.

## Recovery log

Create the matching builder log in the Level Factory authority repository:

`.hiveai/codex-logs/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_CODEX_LOG.md`

Exact H1:

`# RECOVERY-R001 — Revert Mistaken ScrubBots Local Edits`

Immediately below:

`Document role: CODEX BUILDER LOG`

The log must record:

- pre-rollback ScrubBots root/branch/HEAD/status,
- pre-rollback diffs of all four files,
- exact manual/hunk reversals performed,
- any pre-existing diffs preserved,
- post-rollback diffs for all four files,
- post-rollback status,
- explicit statement that no reset/restore/clean/stash/pull/merge/rebase was used,
- explicit statement that no ScrubBots commit or push was performed,
- any uncertainty that remains.

Commit and push **only the recovery log** to `Sekiph82/ScrubBots-Level-Factory` on `main`.

Do not edit `tasks.md`, `.hiveai/HANDOFF.md`, `.hiveai/CYCLE_INDEX.md`, or audit files. ChatGPT owns tracker/audit state.

## Exit

Stop after the local mistaken edits are surgically reverted and the matching recovery log is pushed to the Level Factory repository.

Do not begin PAG-M00-C001.
