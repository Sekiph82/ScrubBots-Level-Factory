extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const FIXTURE_DIR := "res://tests/fixtures/factory_studio_r04_r01/"
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R04-R01 preview scope queue PASS"

class RecordingGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var imported_paths: Array[String] = []
	var batch_import_count := 0

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "batch-import":
			batch_import_count += 1
			var result_items: Array[Dictionary] = []
			var paths: Array = request.get("paths", [])
			for index in range(paths.size()):
				var path := str(paths[index])
				var reused := imported_paths.has(path) or (batch_import_count == 1 and index < 2)
				if not imported_paths.has(path):
					imported_paths.append(path)
				var source_id := "owner-upload-" + path.get_file().get_basename()
				result_items.append({"disposition": "ALREADY_IMPORTED" if reused else "IMPORTED", "source_id": source_id})
			return {"state": "SUCCESS", "batch_id": "r04-r01-focused", "items": result_items}
		if operation == "pipeline":
			return {"state": "CAPTURED", "disposition": "FAILED", "source_id": request.get("source_id", "")}
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		if operation == "release-pool":
			return {"state": "READY", "pool_size": 0, "entries": []}
		return {"state": "UNAVAILABLE", "reason": "Unexpected test operation: " + operation}


var _errors: Array[String] = []
var _render_capture_available := true


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R04R01FocusedViewport"
	viewport.size = Vector2i(1536, 1024)
	viewport.transparent_bg = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	ui.size = Vector2(1536, 1024)
	var canvas := TextureRect.new()
	canvas.name = "MasterCanvas"
	ui.add_child(canvas)
	var file_dialog := FileDialog.new()
	file_dialog.name = "FileDialog"
	ui.add_child(file_dialog)
	viewport.add_child(ui)
	await process_frame
	var gateway := RecordingGateway.new()
	ui.call("configure_gateway", gateway)
	ui.call("_show_screen", "LEVEL FACTORY")

	var fixture_paths: Array[String] = []
	for filename in ["import_01_20x20.png", "import_02_20x59.png", "import_03_32x32.png", "import_04_59x20.png"]:
		var path := ProjectSettings.globalize_path(FIXTURE_DIR + filename)
		fixture_paths.append(path)
		_check(FileAccess.file_exists(path), "focused PNG fixture is missing: " + filename)
	ui.call("_on_files_selected", PackedStringArray(fixture_paths))
	await process_frame
	_close_import_dialog(ui)
	var initial: Dictionary = ui.call("last_import_snapshot")
	_check(initial.get("selected_count") == 4 and initial.get("imported_count") == 2 and initial.get("reused_count") == 2 and initial.get("rejected_count") == 0, "four-source import status did not retain 2 reused / 2 imported: %s" % initial)
	var queue: Array = ui.call("imported_queue_snapshot")
	_check(queue.size() == 4, "accepted multi-PNG items were not retained as four unique browse records")
	var pipeline_count := _count_calls(gateway, "pipeline")
	_check(pipeline_count == 0, "PNG selection dispatched the solver")
	for index in range(4):
		var button := ui.get_node("LevelVariation%d" % (index + 1)) as Button
		_check(button.icon != null, "accepted PNG %d has no selectable thumbnail image" % (index + 1))
		var visible_status := "REUSED" if str(queue[index].get("disposition", "")) == "ALREADY_IMPORTED" else str(queue[index].get("disposition", ""))
		_check(button.text.contains(str(queue[index].get("display_filename", "")).get_basename().left(9)) and button.text.contains(visible_status), "thumbnail %d omits its filename or import/reuse status" % (index + 1))
		_check(button.tooltip_text.contains(str(queue[index].get("display_filename", ""))), "thumbnail %d omits its full filename tooltip" % (index + 1))
		_check(button.tooltip_text.replace("\n", "").contains(str(queue[index].get("source_id", ""))), "thumbnail %d omits its source identity" % (index + 1))
		ui.call("_select_variation", index)
		var state: Dictionary = ui.call("preview_state_snapshot")
		_check(str(state.get("source_id", "")) == str(queue[index].get("source_id", "")), "thumbnail %d selected a mismatched Run Pipeline source" % (index + 1))
		_check(str(state.get("active_path", "")) == str(queue[index].get("path", "")), "thumbnail %d preview path did not match the selected source" % (index + 1))
		_check((ui.get_node("VisualReviewClip/VisualReviewContent/SelectedArtworkPreview") as TextureRect).visible, "Level Factory lost the selected thumbnail preview")
	_check(_count_calls(gateway, "pipeline") == 0, "thumbnail selection dispatched the solver")

	ui.call("_select_variation", 1)
	var host_rect: Rect2 = (ui.call("preview_state_snapshot") as Dictionary).get("host_rect", Rect2())
	var canvas_interior := Rect2(401, 160, 780, 640)
	_check((ui.call("preview_state_snapshot") as Dictionary).get("host_clip_contents", false), "Visual Review Canvas host does not clip child drawing")
	_check(canvas_interior.encloses(host_rect), "preview clip host is outside the Visual Review Canvas interior: %s" % host_rect)
	var live := ui.get_node("RuntimeLiveData") as Label
	_check(live.text.contains("import_02_20x59.png") and live.text.replace("\n", "").contains(str(queue[1].get("source_id", ""))), "persistent selected filename/source status is incomplete")
	var wide := Vector2(1920, 1080)
	ui.size = wide
	ui.call("_apply_responsive_layout")
	var wide_host: Rect2 = (ui.call("preview_state_snapshot") as Dictionary).get("host_rect", Rect2())
	_check(wide_host.position.x >= 0.0 and wide_host.position.y >= 0.0 and wide_host.end.x <= wide.x and wide_host.end.y <= wide.y, "responsive clipped canvas escaped 1920×1080 client bounds")
	ui.size = Vector2(920, 610)
	ui.call("_apply_responsive_layout")
	var small_host: Rect2 = (ui.call("preview_state_snapshot") as Dictionary).get("host_rect", Rect2())
	_check(small_host.position.x >= 0.0 and small_host.position.y >= 0.0 and small_host.end.x <= 920.0 and small_host.end.y <= 610.0, "responsive clipped canvas escaped 920×610 client bounds")
	ui.size = Vector2(1536, 1024)
	ui.call("_apply_responsive_layout")
	var distinct_render_image := Image.create(20, 59, false, Image.FORMAT_RGBA8)
	distinct_render_image.fill(Color8(255, 0, 255, 255))
	ui.call("_render_preview_image", distinct_render_image, "in-memory-render-bounds-probe")
	await process_frame
	await process_frame
	var fitted_image := viewport.get_texture().get_image()
	if fitted_image == null or fitted_image.is_empty():
		_render_capture_available = false
	else:
		var fitted_bounds := _find_fixture_bounds(fitted_image, Color8(255, 0, 255, 255), host_rect)
		_check(int(fitted_bounds.get("count", 0)) > 0, "actual viewport render contained no selected 20×59 fixture pixels")
		_check(int(fitted_bounds.get("outside", 0)) == 0, "fitted source texture rendered outside clipped host bounds")
		var fitted_rect: Rect2 = fitted_bounds.get("rect", Rect2())
		if fitted_rect.size.y > 0.0:
			_check(absf(fitted_rect.size.x / fitted_rect.size.y - (20.0 / 59.0)) < 0.025, "Fit changed the 20×59 source aspect ratio: %s" % fitted_rect)
	ui.call("_set_zoom", 12.0)
	await process_frame
	await process_frame
	var zoom_image := viewport.get_texture().get_image()
	if zoom_image == null or zoom_image.is_empty():
		_render_capture_available = false
	else:
		var zoom_bounds := _find_fixture_bounds(zoom_image, Color8(255, 0, 255, 255), host_rect)
		_check(int(zoom_bounds.get("count", 0)) > 0 and int(zoom_bounds.get("outside", 0)) == 0, "zoomed preview pixels escaped the clipped host")
	ui.call("_fit_canvas")
	_check(is_equal_approx(float((ui.call("preview_state_snapshot") as Dictionary).get("zoom", 0.0)), 1.0), "Fit did not restore the complete-image view")

	ui.call("_show_screen", "PIXEL ART")
	var pixel_state: Dictionary = ui.call("preview_state_snapshot")
	_check(not pixel_state.get("visible", true) and str(pixel_state.get("active_path", "")) == "", "Level Factory PNG leaked into PIXEL ART")
	ui.call("_show_screen", "RELEASE POOL")
	var release_state: Dictionary = ui.call("preview_state_snapshot")
	_check(not release_state.get("visible", true) and str(release_state.get("active_path", "")) == "", "Level Factory PNG leaked into empty RELEASE POOL")
	_check(str(release_state.get("source_id", "")) == str(queue[1].get("source_id", "")), "tab changes drifted the explicit Run Pipeline source")
	ui.call("_show_screen", "LEVEL FACTORY")
	var restored: Dictionary = ui.call("preview_state_snapshot")
	_check(restored.get("visible", false) and str(restored.get("active_path", "")) == str(queue[1].get("path", "")), "returning to LEVEL FACTORY did not restore its own selected import")
	_check(str(restored.get("source_id", "")) == str(queue[1].get("source_id", "")), "returning tabs changed the selected Run Pipeline source")
	_close_import_dialog(ui)

	ui.call("_on_files_selected", PackedStringArray(fixture_paths))
	await process_frame
	_close_import_dialog(ui)
	var repeated: Dictionary = ui.call("last_import_snapshot")
	_check(repeated.get("reused_count") == 4 and (ui.call("imported_queue_snapshot") as Array).size() == 4, "reimport duplicated queue identities or lost ALREADY_IMPORTED status")
	var additional_paths: Array[String] = []
	for index in range(5, 11):
		additional_paths.append(ProjectSettings.globalize_path(FIXTURE_DIR + "import_%02d_20x20.png" % index))
	ui.call("_on_files_selected", PackedStringArray(additional_paths))
	await process_frame
	_close_import_dialog(ui)
	queue = ui.call("imported_queue_snapshot")
	_check(queue.size() == 10, "ten accepted source identities did not remain available for bounded paging")
	ui.call("_page_imported_sources", 1)
	var last_slot := ui.get_node("LevelVariation2") as Button
	_check(last_slot.text.contains("import_10") and last_slot.tooltip_text.replace("\n", "").contains(str(queue[9].get("source_id", ""))), "second bounded thumbnail page does not expose the final queued source")
	ui.call("_select_variation", 1)
	var paged_selection: Dictionary = ui.call("preview_state_snapshot")
	_check(str(paged_selection.get("source_id", "")) == str(queue[9].get("source_id", "")) and str(paged_selection.get("active_path", "")) == str(queue[9].get("path", "")), "paged thumbnail selected a mismatched preview/source pair")
	_check(_count_calls(gateway, "pipeline") == 0, "paged thumbnail selection dispatched the solver")
	ui.call("_page_imported_sources", -1)
	ui.call("_select_variation", 3)
	var selected_for_run: String = str((ui.call("imported_queue_snapshot") as Array)[3].get("source_id", ""))
	ui.call("_run_level_pipeline")
	await process_frame
	_check(_count_calls(gateway, "pipeline") == 1, "explicit Run Pipeline did not invoke exactly one pipeline call")
	for call in gateway.calls:
		if call.get("operation") == "pipeline":
			_check(str(call.get("request", {}).get("source_id", "")) == selected_for_run, "Run Pipeline did not use the thumbnail's selected immutable source id")
	_close_import_dialog(ui)
	viewport.queue_free()
	_finish()


func _find_fixture_bounds(image: Image, target: Color, clip_rect: Rect2) -> Dictionary:
	if image == null or image.is_empty():
		return {"count": 0, "outside": 0, "rect": Rect2()}
	var minimum := Vector2i(image.get_width(), image.get_height())
	var maximum := Vector2i(-1, -1)
	var count := 0
	var outside := 0
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			var pixel := image.get_pixel(x, y)
			if absf(pixel.r - target.r) > 0.08 or absf(pixel.g - target.g) > 0.08 or absf(pixel.b - target.b) > 0.08 or pixel.a < 0.9:
				continue
			count += 1
			minimum.x = mini(minimum.x, x)
			minimum.y = mini(minimum.y, y)
			maximum.x = maxi(maximum.x, x)
			maximum.y = maxi(maximum.y, y)
			if not clip_rect.has_point(Vector2(x + 0.5, y + 0.5)):
				outside += 1
	var rect := Rect2(Vector2(minimum), Vector2(maximum - minimum + Vector2i.ONE)) if count > 0 else Rect2()
	return {"count": count, "outside": outside, "rect": rect}


func _close_import_dialog(ui: Node) -> void:
	for child in ui.get_children():
		if child is AcceptDialog and str((child as AcceptDialog).title).begins_with("PNG import"):
			child.hide()
			child.queue_free()
	await process_frame


func _count_calls(gateway: RecordingGateway, operation: String) -> int:
	var count := 0
	for call in gateway.calls:
		if call.get("operation") == operation:
			count += 1
	return count


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)


func _finish() -> void:
	if _errors.is_empty():
		print(PASS_MARKER)
		if not _render_capture_available:
			print("OWNER_WINDOWS_SCREENSHOT_PENDING: no SubViewport pixel readback; responsive geometry checks only")
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)
