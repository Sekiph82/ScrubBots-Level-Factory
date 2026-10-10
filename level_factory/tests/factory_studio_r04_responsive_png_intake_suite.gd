extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R04 responsive PNG intake PASS"

class RecordingGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var imported_paths: Array[String] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "batch-import":
			var items: Array[Dictionary] = []
			for value in request.get("paths", []):
				var path := str(value)
				if path.contains("FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.png"):
					items.append({"disposition": "REJECTED", "error": "1536×1024 exceeds the 20–59 logical grid limit."})
					continue
				var identity := "owner-upload-" + path.get_file().get_basename()
				var reused := imported_paths.has(path)
				if not reused:
					imported_paths.append(path)
				items.append({"disposition": "ALREADY_IMPORTED" if reused else "IMPORTED", "source_id": identity})
			return {"state": "SUCCESS", "batch_id": "r04-ui-dispatch", "items": items}
		if operation == "pipeline":
			return {"state": "CAPTURED", "disposition": "FAILED", "source_id": request.get("source_id", "")}
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		return {"state": "UNAVAILABLE", "reason": "Unexpected test operation: " + operation}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var geometry_helper := UI_SCRIPT.new()
	var geometry_small: Dictionary = geometry_helper.call("responsive_geometry", Vector2(920, 610))
	var geometry_reference: Dictionary = geometry_helper.call("responsive_geometry", Vector2(1536, 1024))
	var geometry_wide: Dictionary = geometry_helper.call("responsive_geometry", Vector2(1920, 1080))
	geometry_helper.free()
	_check(is_equal_approx(float(geometry_small.get("scale", 0.0)), 610.0 / 1024.0), "small window did not scale to the available client area")
	_check(is_equal_approx(float(geometry_reference.get("scale", 0.0)), 1.0) and geometry_reference.get("offset") == Vector2.ZERO, "reference layout changed at 1536×1024")
	_check(is_equal_approx(float(geometry_wide.get("scale", 0.0)), 1080.0 / 1024.0) and is_equal_approx(float(geometry_wide.get("offset", Vector2.ZERO).x), 150.0), "widescreen layout did not remain proportional and centered")

	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	ui.size = Vector2(1536, 1024)
	var canvas := TextureRect.new()
	canvas.name = "MasterCanvas"
	ui.add_child(canvas)
	var file_dialog := FileDialog.new()
	file_dialog.name = "FileDialog"
	ui.add_child(file_dialog)
	root.add_child(ui)
	await process_frame
	var gateway := RecordingGateway.new()
	ui.call("configure_gateway", gateway)

	var project_root := ProjectSettings.globalize_path("res://..").simplify_path()
	var easy_path := project_root.path_join("tests/golden/fixtures/m08/golden-easy.png")
	var rectangular_path := project_root.path_join("tests/golden/fixtures/m08/golden-rectangular.png")
	var owl_path := project_root.path_join("tests/fixtures/owner_void/017_a_single_brown_owl_centered_simple_clear_32px.png")
	var master_path := ProjectSettings.globalize_path("res://assets/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.png")
	for path in [easy_path, rectangular_path, owl_path, master_path]:
		_check(FileAccess.file_exists(path), "required in-repository PNG fixture is missing: " + path)

	ui.call("_on_file_selected", easy_path)
	await process_frame
	var single: Dictionary = ui.call("last_import_snapshot")
	_check(single.get("selected_count") == 1 and single.get("imported_count") == 1, "single PNG dispatch did not report its actual imported item")
	_check(single.get("preview_source_id") == "owner-upload-golden-easy", "single PNG preview identity did not match the imported source")
	_check((ui.get_node("SelectedArtworkPreview") as TextureRect).visible, "single valid PNG did not populate the Visual Review Canvas")
	_check(_count_calls(gateway, "batch-import") == 1 and _count_calls(gateway, "pipeline") == 0, "single PNG selection did not dispatch once to import or invoked the solver")
	_close_import_dialog(ui)

	ui.call("_on_files_selected", PackedStringArray([easy_path, rectangular_path, owl_path, master_path]))
	await process_frame
	var multiple: Dictionary = ui.call("last_import_snapshot")
	_check(multiple.get("selected_count") == 4 and multiple.get("imported_count") == 2 and multiple.get("reused_count") == 1 and multiple.get("rejected_count") == 1, "multi-PNG import counts or idempotent reuse status were not truthful: %s" % multiple)
	_check(multiple.get("preview_source_id") == "owner-upload-golden-easy", "multi-PNG preview did not use the first valid source in deterministic selection order")
	var statuses: Array = multiple.get("items", [])
	_check(statuses.size() == 4, "per-item selection statuses did not match selected file count: %d" % statuses.size())
	_check(str(statuses[0]).contains("ALREADY_IMPORTED"), "same-file reimport did not report explicit idempotent reuse")
	_check(str(statuses[1]) == "golden-rectangular.png\nIMPORTED · owner-upload-golden-rectangular", "second fixture source identity was omitted: %s" % str(statuses[1]))
	_check(str(statuses[2]) == "017_a_single_brown_owl_centered_simple_clear_32px.png\nIMPORTED · owner-upload-017_a_single_brown_owl_centered_simple_clear_32px", "third fixture source identity was omitted: %s" % str(statuses[2]))
	_check(str(statuses[3]).contains("REJECTED") and str(statuses[3]).contains("1536×1024"), "oversized UI-master PNG did not show its rejection reason")
	_check(_count_calls(gateway, "batch-import") == 2 and _count_calls(gateway, "pipeline") == 0, "PNG selection unexpectedly invoked the solver")
	_check((ui.get_node("SelectedArtworkPreview") as TextureRect).visible, "valid preview was lost after multi-selection containing a rejected file")
	_close_import_dialog(ui)

	ui.call("_run_level_pipeline")
	await process_frame
	_check(_count_calls(gateway, "pipeline") == 1, "explicit Run Pipeline did not produce exactly one canonical pipeline dispatch")
	for call in gateway.calls:
		if call.get("operation") == "pipeline":
			_check(call.get("request", {}).get("source_id") == "owner-upload-golden-easy", "explicit pipeline did not bind to the selected preview source")
	ui.queue_free()
	_finish()


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
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)
