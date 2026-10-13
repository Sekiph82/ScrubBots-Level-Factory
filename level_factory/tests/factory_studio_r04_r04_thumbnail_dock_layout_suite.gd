extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const SOURCE_002 := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const SOURCE_003 := "owner-upload-e26b81cc6cc364364e3bb1b5eefbb79b88556c49aabbb5d8ca8cdc6fabda8fe1"
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R04 thumbnail dock layout PASS"

class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		return {"state": "UNAVAILABLE", "reason": "R04 dock suite uses read-only fixtures."}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R04ThumbnailDockViewport"
	viewport.size = Vector2i(1536, 864)
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)

	var ui := Control.new()
	ui.name = "FactoryStudioR04ThumbnailDock"
	ui.set_script(UI_SCRIPT)
	ui.size = Vector2(1536, 864)
	var canvas := TextureRect.new()
	canvas.name = "MasterCanvas"
	ui.add_child(canvas)
	var dialog := FileDialog.new()
	dialog.name = "FileDialog"
	ui.add_child(dialog)
	viewport.add_child(ui)
	await process_frame
	await process_frame

	var gateway := ReadOnlyGateway.new()
	ui.call("configure_gateway", gateway)
	var release_root := ProjectSettings.globalize_path("res://").path_join("..").path_join("Release/ScrubBots Factory Studio").simplify_path()
	var source_002_path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % SOURCE_002)
	var source_003_path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % SOURCE_003)
	_check(FileAccess.file_exists(source_002_path), "read-only owner 002 fixture is unavailable")
	_check(FileAccess.file_exists(source_003_path), "read-only owner 003 fixture is unavailable")
	ui.call("_upsert_imported_source", {"path": source_002_path, "source_id": SOURCE_002, "display_filename": "002_32x32px.png", "width": 32, "height": 32, "disposition": "IMPORTED"})
	ui.call("_upsert_imported_source", {"path": source_003_path, "source_id": SOURCE_003, "display_filename": "003_32x32px.png", "width": 32, "height": 32, "disposition": "IMPORTED"})
	for source_number in range(3, 9):
		var source_id := "owner-upload-r04dock-%02d" % source_number
		ui.call("_upsert_imported_source", {"path": source_002_path, "source_id": source_id, "display_filename": "source-%02d.png" % source_number, "width": 32, "height": 32, "disposition": "IMPORTED"})
	ui.call("_upsert_imported_source", {"path": source_002_path, "source_id": "owner-upload-r04dock-09", "display_filename": "source-09.png", "width": 32, "height": 32, "disposition": "IMPORTED"})
	ui.call("_show_screen", "LEVEL FACTORY")
	await process_frame

	var tested_sizes: Array[Vector2] = [
		Vector2(1536, 864), Vector2(1536, 932), Vector2(1536, 1024),
		Vector2(1920, 1080), Vector2(1200, 800), Vector2(1100, 720),
		Vector2(1536, 864)
	]
	var initial_rects: Dictionary = {}
	for size_index in range(tested_sizes.size()):
		var client := tested_sizes[size_index]
		ui.size = client
		viewport.size = Vector2i(client)
		ui.call("_apply_responsive_layout")
		await process_frame
		var strip := ui.get_node("RuntimeBottomStrip") as Control
		var center := ui.get_node("RuntimeCanvasPanel") as Control
		var preview := ui.get_node("VisualReviewClip") as Control
		var strip_rect := strip.get_global_rect()
		var center_rect := center.get_global_rect()
		var preview_rect := preview.get_global_rect()
		var heading := ui.get_node("RuntimeBottomHeading") as Control
		var heading_rect := heading.get_global_rect()
		_check(_contains_with_padding(strip_rect, heading_rect, 7.5), "bottom heading is outside dock padding at %s: dock=%s heading=%s" % [client, strip_rect, heading_rect])
		_check(center_rect.end.y <= strip_rect.position.y + 0.5, "bottom dock overlaps or rises above center panel at %s: center=%s dock=%s" % [client, center_rect, strip_rect])
		_check(preview_rect.end.y <= strip_rect.position.y + 0.5, "preview canvas reaches or overlaps the bottom dock at %s: preview=%s dock=%s" % [client, preview_rect, strip_rect])
		_check(preview_rect.position.y >= center_rect.position.y - 0.5 and preview_rect.end.y <= center_rect.end.y + 0.5, "preview host escaped central canvas at %s" % client)
		var cards: Array[Rect2] = []
		for index in range(5):
			var button := ui.get_node("LevelVariation%d" % (index + 1)) as Button
			var button_rect := button.get_global_rect()
			_check(button.visible, "Level Factory slot %d is not visible at %s" % [index + 1, client])
			_check(_contains_with_padding(strip_rect, button_rect, 7.5), "thumbnail %d escapes dock padding at %s: dock=%s button=%s" % [index + 1, client, strip_rect, button_rect])
			_check(button_rect.size.x >= 44.0 and button_rect.size.y >= 44.0, "thumbnail %d lost its minimum click target at %s: %s" % [index + 1, client, button_rect.size])
			_check(not button_rect.intersects(preview_rect), "thumbnail %d overlaps the Visual Review canvas at %s" % [index + 1, client])
			for previous in cards:
				_check(not button_rect.intersects(previous), "thumbnail buttons overlap at %s" % client)
			cards.append(button_rect)
		if size_index == 0:
			initial_rects = _dock_rect_snapshot(ui)
		elif size_index == tested_sizes.size() - 1:
			_check(_dock_rect_snapshot(ui) == initial_rects, "resize-back changed dock control geometry")

	var heading_label := ui.get_node("RuntimeBottomHeading") as Label
	_check(heading_label.text.contains("9 PNG") and not heading_label.text.contains("1/2"), "Level Factory dock heading still exposes page-based gallery navigation: %s" % heading_label.text)
	var first := ui.get_node("LevelVariation1") as Button
	var second := ui.get_node("LevelVariation2") as Button
	first.emit_signal("pressed")
	_check(str(ui.get("_selected_import_source_id")) == SOURCE_002, "first thumbnail did not select the pinned 002 source")
	second.emit_signal("pressed")
	_check(str(ui.get("_selected_import_source_id")) == SOURCE_003, "second thumbnail did not select the distinct 003 source")
	var strip_for_wheel := (ui.get_node("RuntimeBottomStrip") as Control).get_global_rect()
	for _step in range(4):
		var wheel := InputEventMouseButton.new()
		wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
		wheel.pressed = true
		wheel.global_position = strip_for_wheel.get_center()
		ui.call("_unhandled_input", wheel)
	_check(int(ui.get("_imported_window_start")) == 4, "wheel over the bottom dock did not slide the five-source window")
	_check(heading_label.text.contains("9 PNG") and not heading_label.text.contains("2/2"), "sliding window heading exposes old page numbering: %s" % heading_label.text)
	_check((ui.get_node("LevelVariation5") as Button).text.contains("source-09"), "last source is not visible in slot five of the clamped five-wide window")
	(ui.get_node("LevelVariation5") as Button).emit_signal("pressed")
	_check(str(ui.get("_selected_import_source_id")) == "owner-upload-r04dock-09", "page 2 first thumbnail did not select source 9")
	for call in gateway.calls:
		var operation := str(call.get("operation", ""))
		_check(operation not in ["pipeline", "batch-run", "run-pipeline", "solve", "replay", "load-check"], "thumbnail selection dispatched a solver or pipeline operation: %s" % operation)

	ui.call("_show_screen", "PIXEL ART")
	_check(not (ui.get_node("LevelVariation1") as Button).visible, "Level Factory thumbnail became visible on PIXEL ART")
	ui.call("_show_screen", "RELEASE POOL")
	_check(not (ui.get_node("LevelVariation1") as Button).visible, "Level Factory thumbnail became visible on RELEASE POOL")
	ui.queue_free()
	await process_frame
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)


func _contains_with_padding(outer: Rect2, inner: Rect2, padding: float) -> bool:
	return (
		inner.position.x >= outer.position.x + padding - 0.5
		and inner.position.y >= outer.position.y + padding - 0.5
		and inner.end.x <= outer.end.x - padding + 0.5
		and inner.end.y <= outer.end.y - padding + 0.5
	)


func _dock_rect_snapshot(ui: Control) -> Dictionary:
	var result := {}
	for node_name in ["RuntimeBottomStrip", "RuntimeBottomHeading", "LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5"]:
		result[node_name] = (ui.get_node(node_name) as Control).get_global_rect()
	return result


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
