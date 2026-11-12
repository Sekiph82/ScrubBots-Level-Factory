extends SceneTree

## R04 responsive layout and PNG intake, rewritten 2026-11-12.
##
## Unchanged: the proportional responsive geometry and the multi-PNG intake
## statuses (imported / reused / rejected, no solver call). Updated to the
## current product: the manual "Select PNG" control was removed (f95a9cab), a
## single selected file in the PixelLab-only UI is a PixelLab Pro 4×4 atlas
## import, and Run Pipeline only plans a batch of Release Pool Pending sources
## (it never dispatches a per-source pipeline for an arbitrary selection).

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
		if operation == "pixellab-pro-4x4-import":
			return {"state": "ERROR", "error": "fixture: not a PixelLab atlas", "source_ids": [], "frame_statuses": []}
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		return {"state": "UNAVAILABLE", "reason": "Unexpected test operation: " + operation}

	func prepare_studio_extension_call(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": "prepare:" + operation, "request": request.duplicate(true)})
		return {}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	# Region-based responsive geometry (left / center / right regions, clamped
	# vertical scale) replaced the single proportional scale; 1100×720 is the
	# declared minimum supported client size.
	var geometry_helper := UI_SCRIPT.new()
	var reference: Dictionary = geometry_helper.call("responsive_geometry", Vector2(1536, 1024))
	var wide: Dictionary = geometry_helper.call("responsive_geometry", Vector2(1920, 1080))
	geometry_helper.free()
	_check(is_equal_approx(float(reference.get("scale_x", 0.0)), 1.0) and is_equal_approx(float(reference.get("scale_y", 0.0)), 1.0)
		and absf(float(reference.get("left_scale", 0.0)) - 1.0) < 0.01, "reference layout changed at 1536×1024: %s" % [reference])
	_check(reference.get("minimum_supported_size") == Vector2(1100, 720), "minimum supported client size changed: %s" % [reference.get("minimum_supported_size")])
	_check(float(wide.get("left_width", 0.0)) > float(reference.get("left_width", 0.0)) and float(wide.get("center_width", 0.0)) > float(reference.get("center_width", 0.0)),
		"widescreen regions did not grow proportionally: %s" % [wide])

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
	ui.set("_studio_read_queue", [])
	_check(ui.get_node_or_null("SelectArtwork") == null, "the removed manual Select PNG control reappeared")

	# Every master control keeps its hitbox inside every supported client area.
	for client in [Vector2(1100, 720), Vector2(1536, 1024), Vector2(1920, 1080), Vector2(2560, 1440)]:
		ui.size = client
		ui.call("_apply_responsive_layout")
		for button in ui.get("_master_buttons"):
			var rect := (button as Control).get_global_rect()
			_check(rect.position.x >= -0.1 and rect.position.y >= -0.1 and rect.end.x <= client.x + 0.1 and rect.end.y <= client.y + 0.1,
				"%s hitbox escaped the %s client area: %s" % [(button as Control).name, client, rect])
	ui.size = Vector2(1536, 1024)
	ui.call("_apply_responsive_layout")

	var project_root := ProjectSettings.globalize_path("res://..").simplify_path()
	var easy_path := project_root.path_join("tests/golden/fixtures/m08/golden-easy.png")
	var rectangular_path := project_root.path_join("tests/golden/fixtures/m08/golden-rectangular.png")
	var owl_path := project_root.path_join("tests/fixtures/owner_void/017_a_single_brown_owl_centered_simple_clear_32px.png")
	var master_path := ProjectSettings.globalize_path("res://assets/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.png")
	var fixtures_present := true
	for path in [easy_path, rectangular_path, owl_path, master_path]:
		if not FileAccess.file_exists(path):
			fixtures_present = false
			_check(false, "required in-repository PNG fixture is missing: " + path)

	# A single selected file in the PixelLab-only UI is a PixelLab Pro 4×4 atlas import.
	ui.set("_width", 56)
	ui.set("_height", 56)
	ui.call("_on_file_selected", easy_path)
	await process_frame
	_check(_count_calls(gateway, "pixellab-pro-4x4-import") == 1 and _count_calls(gateway, "batch-import") == 0,
		"single selected PNG did not route to the PixelLab Pro 4×4 atlas import")
	_check(not bool(ui.get("_operation_running")), "a failed atlas import left the UI busy")
	await _close_import_dialog(ui)

	# Multi-file intake: truthful per-item statuses, idempotent reuse, no solver call.
	if fixtures_present:
		ui.call("_on_files_selected", PackedStringArray([easy_path, rectangular_path]))
		await process_frame
		await _close_import_dialog(ui)
		ui.call("_on_files_selected", PackedStringArray([easy_path, rectangular_path, owl_path, master_path]))
		await process_frame
		var multiple: Dictionary = ui.call("last_import_snapshot")
		_check(multiple.get("selected_count") == 4 and multiple.get("imported_count") == 1 and multiple.get("reused_count") == 2 and multiple.get("rejected_count") == 1,
			"multi-PNG import counts or idempotent reuse status were not truthful: %s" % multiple)
		_check(multiple.get("preview_source_id") == "owner-upload-golden-easy", "multi-PNG preview did not use the first valid source in selection order")
		var statuses: Array = multiple.get("items", [])
		_check(statuses.size() == 4, "per-item selection statuses did not match the selected file count: %d" % statuses.size())
		if statuses.size() == 4:
			_check(str(statuses[0]).contains("ALREADY_IMPORTED") and str(statuses[1]).contains("ALREADY_IMPORTED"), "same-file reimport did not report explicit idempotent reuse")
			# Status rows wrap long identities and append the content SHA.
			var owl_status := str(statuses[2]).replace("\n", "")
			_check(owl_status.begins_with("017_a_single_brown_owl_centered_simple_clear_32px.png") and owl_status.contains("IMPORTED")
				and owl_status.contains("owner-upload-017_a_single_brown_owl_centered_simple_clear_32px"), "third fixture source identity was omitted: %s" % str(statuses[2]))
			_check(str(statuses[3]).contains("REJECTED") and str(statuses[3]).contains("1536×1024"), "oversized UI-master PNG did not show its rejection reason")
		# Imported PNG previews are scoped to LEVEL FACTORY.
		ui.call("_show_screen", "LEVEL FACTORY")
		_check((ui.get("_preview_rect") as TextureRect).visible, "valid preview was lost after a multi-selection containing a rejected file")
		await _close_import_dialog(ui)
	_check(_count_calls(gateway, "pipeline") == 0 and _count_calls(gateway, "prepare:png-batch-run") == 0, "PNG selection invoked the solver")

	# Run Pipeline plans only Release Pool Pending sources; with no Pending
	# statuses loaded it must not dispatch a per-source pipeline.
	ui.call("_run_level_pipeline")
	await process_frame
	_check(_count_calls(gateway, "pipeline") == 0 and _count_calls(gateway, "pending-png-batch-create") == 0 and _count_calls(gateway, "prepare:png-batch-run") == 0,
		"Run Pipeline dispatched work without Pending Release Pool sources")
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
