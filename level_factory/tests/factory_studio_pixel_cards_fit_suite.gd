extends SceneTree

## Owner report 2026-11-13: in a small window the three PIXEL ART candidate cards
## under "Palette V3 LOCKED" did not fit the Details panel; the third card ran past
## the panel's right edge. A Button grows to fit its caption, so a long candidate
## id widened the card beyond its responsive width.

const PASS_MARKER := "PIXEL ART candidate cards and activity table fit PASS"

var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var instance := (load("res://scenes/factory_studio.tscn") as PackedScene).instantiate()
	root.add_child(instance)
	await process_frame
	var ui := instance.get_node("MasterUI") as Control
	ui.set("_studio_read_queue", [])
	ui.call("_show_screen", "PIXEL ART")
	var image := Image.create(32, 32, false, Image.FORMAT_RGBA8)
	image.fill(Color8(255, 69, 0))
	var png := OS.get_temp_dir().path_join("sb-pixel-card-fit.png")
	image.save_png(png)
	for index in range(3):
		ui.call("_set_runtime_button", "ArtworkVariation%d" % (index + 1), "candidate-owner-6633713a925e69424167647fa452e0c5", png)
	ui.set("_pixel_art_activity_events", [{"time": "2026-11-13 00:04:12", "state": "RUNNING", "stage": "GENERATE",
		"message": "PixelLab Pro 4x4 request accepted; waiting for the provider to return the atlas"}])
	for client in [Vector2(833, 550), Vector2(1100, 720), Vector2(1536, 1024), Vector2(2560, 1440)]:
		ui.size = client
		ui.call("_apply_responsive_layout")
		await process_frame
		var panel := ui.get_node("RuntimeDetailsPanel") as Control
		var panel_right := panel.position.x + panel.size.x
		var previous_right := panel.position.x
		for index in range(3):
			var card := ui.get_node("ArtworkVariation%d" % (index + 1)) as Control
			var left := card.position.x
			var right := card.position.x + card.size.x
			_check(right <= panel_right + 0.5, "%s: card %d ends at %.1f past the Details panel edge %.1f" % [client, index + 1, right, panel_right])
			_check(left >= previous_right - 0.5, "%s: card %d overlaps the previous card (%.1f < %.1f)" % [client, index + 1, left, previous_right])
			previous_right = right
		# Owner report 2026-11-13: the PIXEL ART ACTIVITY table also left the
		# workspace column (over the canvas) and the window bottom.
		var table := ui.get_node("PixelArtActivityTable") as Control
		var left_panel := ui.get_node("RuntimeLeftPanel") as Control
		var canvas := ui.get_node("RuntimeCanvasPanel") as Control
		_check(table.position.x + table.size.x <= canvas.position.x + 0.5,
			"%s: activity table ends at x=%.1f over the canvas starting at %.1f" % [client, table.position.x + table.size.x, canvas.position.x])
		_check(table.position.x + table.size.x <= left_panel.position.x + left_panel.size.x + 0.5,
			"%s: activity table is wider than the workspace panel" % [client])
		_check(table.position.y + table.size.y <= client.y + 0.5,
			"%s: activity table ends at y=%.1f below the window %.1f" % [client, table.position.y + table.size.y, client.y])
	instance.free()
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for message in _errors:
		push_error(message)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
