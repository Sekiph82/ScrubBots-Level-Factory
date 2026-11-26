from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\level_factory\scripts\factory_studio_exact_ui.gd")
s = p.read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert old in s, old
    s = s.replace(old, new, 1)


# The three former status-only stage buttons now drive the game release (same geometry and names).
rep('_place_control("ValidateReleaseAssets", Rect2(1207, 530, 291, 36), _show_publish_stage.bind("VALIDATE_ASSETS"))',
    '_place_control("ValidateReleaseAssets", Rect2(1207, 530, 291, 36), _open_game_release_count)')
rep('_place_control("BuildReleasePack", Rect2(1207, 568, 291, 36), _show_publish_stage.bind("BUILD_SCRUBPACK"))',
    '_place_control("BuildReleasePack", Rect2(1207, 568, 291, 36), _plan_game_release)')
rep('_place_control("UploadR2Status", Rect2(1207, 606, 291, 36), _show_publish_stage.bind("UPLOAD_R2"))',
    '_place_control("UploadR2Status", Rect2(1207, 606, 291, 36), _confirm_send_to_game)')
rep('"ValidateReleaseAssets": "Validate Assets",', '"ValidateReleaseAssets": "Levels to add: %d" % _game_release_count,')
rep('"BuildReleasePack": "Build Scrubpack", "UploadR2Status": "Upload Status",',
    '"BuildReleasePack": "Plan Game Release", "UploadR2Status": "Send to Game",')
rep('"ValidateReleaseAssets": "Status only: displays the most recent preflight validation state. It does not start asset validation.",',
    '"ValidateReleaseAssets": "Sets how many Release Pool levels the next game release adds after the game\'s current last level.",')
rep('"BuildReleasePack": "Status only: displays the most recent preflight pack-build state. It does not build or upload a pack.",',
    '"BuildReleasePack": "Builds the release plan: picks that many Release Pool levels in the game\'s EASY/MEDIUM/HARD/VERY_HARD cadence. Nothing is written to the game.",')
rep('"UploadR2Status": "Status only: displays the most recent preflight upload state. It does not upload to R2.",',
    '"UploadR2Status": "After your confirmation, writes the planned levels into the local ScrubBots game (one catalog commit, checked with Godot). Players get them in the next game build.",')

FUNCS = '''

# Owner 2026-11-25: Release Pool sends an owner-chosen number of levels into the game build.
func _open_game_release_count() -> void:
	if _game_release_count_dialog == null:
		_game_release_count_dialog = ConfirmationDialog.new()
		_game_release_count_dialog.title = "Levels to add to the game"
		_game_release_count_spin = SpinBox.new()
		_game_release_count_spin.min_value = 1
		_game_release_count_spin.max_value = 1000
		_game_release_count_spin.step = 1
		_game_release_count_dialog.add_child(_game_release_count_spin)
		_game_release_count_dialog.confirmed.connect(_apply_game_release_count)
		add_child(_game_release_count_dialog)
	_game_release_count_spin.value = _game_release_count
	_game_release_count_dialog.popup_centered(Vector2i(360, 120))


func _apply_game_release_count() -> void:
	_game_release_count = int(_game_release_count_spin.value)
	_game_release_plan = {}
	var button := get_node_or_null("ValidateReleaseAssets") as Button
	if button != null:
		button.text = _control_caption("ValidateReleaseAssets")
	_append_release_pool_activity("GAME RELEASE", "COUNT SET", "levels to add=%d; build the plan next" % _game_release_count)


func _plan_game_release() -> void:
	if _game_release_busy:
		_report("A game release step is already running.")
		return
	_game_release_busy = true
	_game_release_plan = {}
	_append_release_pool_activity("GAME RELEASE PLAN", "STARTED", "levels to add=%d; reading the Release Pool (about a minute)" % _game_release_count)
	_report("Planning %d levels for the game..." % _game_release_count)
	if not _queue_studio_read_extension("campaign-build", {"k": _game_release_count, "locks": {}}, {"kind": "game-release-plan"}):
		_game_release_busy = false
		_append_release_pool_activity("GAME RELEASE PLAN", "UNAVAILABLE", "Studio service could not start the planner.")


func _game_release_summary(plan: Dictionary) -> String:
	var classes := {}
	var first := 0
	var last := 0
	for row in plan.get("slots", []):
		if row.get("chosen_id") == null:
			continue
		var cls := str(row.get("class", "?"))
		classes[cls] = int(classes.get(cls, 0)) + 1
		if first == 0:
			first = int(row.get("n", 0))
		last = int(row.get("n", 0))
	var parts := PackedStringArray()
	for cls in ["EASY", "MEDIUM", "HARD", "VERY_HARD"]:
		parts.append("%s %d" % [cls, int(classes.get(cls, 0))])
	return "levels %d..%d (%d) · %s · shortages %d" % [first, last, plan.get("publishable_prefix", []).size(), " · ".join(parts), plan.get("shortages", []).size()]


func _apply_game_release_plan(result: Dictionary) -> void:
	_game_release_busy = false
	if str(result.get("plan_hash", "")).is_empty():
		var reason := str(result.get("error", result.get("reason", result.get("state", "planner returned no plan"))))
		_append_release_pool_activity("GAME RELEASE PLAN", "FAILED", reason.left(300))
		_report("Game release plan failed: %s" % reason.left(160))
		return
	_game_release_plan = result
	var summary := _game_release_summary(result)
	_append_release_pool_activity("GAME RELEASE PLAN", "READY", summary)
	_report("Plan ready: %s" % summary)


func _confirm_send_to_game() -> void:
	if _game_release_busy:
		_report("A game release step is already running.")
		return
	if str(_game_release_plan.get("plan_hash", "")).is_empty() or _game_release_plan.get("publishable_prefix", []).is_empty():
		_append_release_pool_activity("SEND TO GAME", "BLOCKED", "Build the game release plan first.")
		_report("Build the game release plan first.")
		return
	if _game_release_send_dialog == null:
		_game_release_send_dialog = ConfirmationDialog.new()
		_game_release_send_dialog.title = "Send levels to the game"
		_game_release_send_dialog.confirmed.connect(_send_to_game)
		add_child(_game_release_send_dialog)
	_game_release_send_dialog.dialog_text = "Write these levels into the ScrubBots game?\\n\\n%s\\n\\nPlayers get them in the next game build." % _game_release_summary(_game_release_plan)
	_game_release_send_dialog.popup_centered(Vector2i(620, 200))


func _send_to_game() -> void:
	_game_release_busy = true
	_append_release_pool_activity("SEND TO GAME", "STARTED", _game_release_summary(_game_release_plan))
	_report("Sending levels to the game...")
	if not _queue_studio_read_extension("campaign-publish", {"plan_hash": str(_game_release_plan.get("plan_hash", ""))}, {"kind": "game-release-send"}):
		_game_release_busy = false
		_append_release_pool_activity("SEND TO GAME", "UNAVAILABLE", "Studio service could not start the publisher.")


func _apply_game_release_send(result: Dictionary) -> void:
	_game_release_busy = false
	_game_release_plan = {}
	if str(result.get("disposition", "")) != "PUBLISHED":
		var reason := str(result.get("error", result.get("reason", result.get("state", "publisher returned no result"))))
		_append_release_pool_activity("SEND TO GAME", "FAILED", reason.left(300))
		_report("Send to game failed: %s" % reason.left(160))
		return
	var orders: Array = result.get("orders", [])
	var first := str(orders.front()) if not orders.is_empty() else "-"
	var last := str(orders.back()) if not orders.is_empty() else "-"
	var detail := "%d levels written: %s..%s · catalog %s" % [orders.size(), first, last, str(result.get("catalog_sha256", "")).left(12)]
	_append_release_pool_activity("SEND TO GAME", "PUBLISHED", detail)
	_report("Sent to game: %s" % detail)
'''
rep("\n\nfunc _finish_generation(result: Dictionary) -> void:", FUNCS + "\n\nfunc _finish_generation(result: Dictionary) -> void:")
rep('''	elif kind == "restore-batch-run":
		_apply_restored_batch_run(result, context)''', '''	elif kind == "game-release-plan":
		_apply_game_release_plan(result)
	elif kind == "game-release-send":
		_apply_game_release_send(result)
	elif kind == "restore-batch-run":
		_apply_restored_batch_run(result, context)''')
rep("var _settings_real_play_timeout: LineEdit\n",
    "var _settings_real_play_timeout: LineEdit\nvar _game_release_count := 800\nvar _game_release_plan: Dictionary = {}\n"
    "var _game_release_busy := false\nvar _game_release_count_dialog: ConfirmationDialog\nvar _game_release_count_spin: SpinBox\n"
    "var _game_release_send_dialog: ConfirmationDialog\n")
p.write_text(s, encoding="utf-8")
print("ok")
