extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R05 loaded PNG batch UI PASS"

class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var source_ids: Array[String] = []
	var planned_job: Dictionary = {}

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "loaded-png-batch-create":
			source_ids = request.get("source_ids", []).duplicate()
			return {"batch_id": "batch-loaded-fixture", "counts": {"success": source_ids.size(), "failed": 0}}
		if operation == "png-batch-create":
			return {"job": planned_job.duplicate(true)}
		return {"state": "UNAVAILABLE", "reason": "Read-only R05 UI fixture."}

	func prepare_studio_extension_call(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": "prepare:" + operation, "request": request.duplicate(true)})
		return {}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		return {"state": "UNAVAILABLE"}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R05LoadedBatchViewport"
	viewport.size = Vector2i(1536, 864)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.name = "FactoryStudioR05LoadedBatch"
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
	var all_ids: Array[String] = []
	for index in range(9):
		var source_id := "owner-upload-" + ("%064x" % (index + 1))
		all_ids.append(source_id)
		ui.call("_upsert_imported_source", {
			"path": "", "source_id": source_id,
			"display_filename": "%03d_32x32px.png" % (index + 2),
			"width": 32, "height": 32, "disposition": "IMPORTED",
		})
	var result_items: Array[Dictionary] = []
	for index in range(all_ids.size()):
		result_items.append({
			"index": index, "source_id": all_ids[index],
			"original_filename": "%03d_32x32px.png" % (index + 2),
			"column_count": 3 if index < 4 else 4 if index < 8 else 5,
			"status": "FAILED", "reason": "fixture reason %d" % (index + 1),
			"attempt_id": "attempt-%d" % (index + 1),
		})
	gateway.planned_job = {
		"job_id": "png-batch-fixture", "import_batch_id": "batch-loaded-fixture",
		"state": "QUEUED", "snapshot_source_count": 9,
		"items": result_items,
		"counts": {"total": 9, "ready": 0, "failed": 9, "rejected": 0, "skipped": 0, "remaining": 9},
		"planned_quotas": {"3": 4, "4": 4, "5": 1}, "ready_mix": {"3": 0, "4": 0, "5": 0},
	}
	ui.call("configure_gateway", gateway)
	ui.call("_show_screen", "LEVEL FACTORY")
	ui.set("_batch_job_id", "png-batch-historical-four")
	ui.set("_batch_import_id", "batch-import-historical-four")
	ui.set("_batch_snapshot", {
		"job_id": "png-batch-historical-four", "import_batch_id": "batch-import-historical-four",
		"state": "RUNNING", "items": [{"source_id": all_ids[0]}],
	})
	await process_frame

	var second_page_wheel := InputEventMouseButton.new()
	second_page_wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
	second_page_wheel.pressed = true
	second_page_wheel.global_position = (ui.get_node("RuntimeBottomStrip") as Control).get_global_rect().get_center()
	ui.call("_unhandled_input", second_page_wheel)
	_check(int(ui.get("_imported_page")) == 1, "nine-source gallery did not expose its second page")
	(ui.get_node("LevelVariation1") as Button).emit_signal("pressed")
	_check(str(ui.get("_selected_import_source_id")) == all_ids[8], "second-page thumbnail did not select the ninth source")
	_check(str(ui.get("_batch_job_id")) == "png-batch-historical-four", "thumbnail selection replaced the active historical job identity")
	_check(str(ui.get("_batch_snapshot").get("import_batch_id", "")) == "batch-import-historical-four", "thumbnail selection rewrote the active job snapshot")
	_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")) in ["loaded-png-batch-create", "png-batch-create", "pipeline", "png-batch-run"]), "thumbnail selection created a batch or dispatched pipeline work")
	_check(gateway.source_ids.is_empty(), "thumbnail selection changed loaded batch scope")
	for call in gateway.calls:
		_check(not str(call.get("operation", "")).contains("pipeline") and not str(call.get("operation", "")).contains("batch-run"), "thumbnail selection dispatched solver work: %s" % str(call.get("operation", "")))

	ui.call("_run_level_pipeline")
	_check(gateway.source_ids == all_ids, "explicit Run did not snapshot all nine loaded sources in gallery order")
	_check(gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")) == "prepare:png-batch-run"), "explicit Run did not prepare the canonical batch worker")
	_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")) == "pipeline"), "UI fixture executed a native per-source pipeline")
	_check(str(ui.get("_batch_job_id")) == "png-batch-fixture", "explicit Run did not retain the planned job identity")

	var activity_panel := Control.new()
	activity_panel.name = "R05ActivityPanel"
	ui.add_child(activity_panel)
	var activity_scroll := ScrollContainer.new()
	activity_scroll.name = "R05ActivityScroll"
	activity_panel.add_child(activity_scroll)
	var activity_rows := VBoxContainer.new()
	activity_rows.name = "R05ActivityRows"
	activity_scroll.add_child(activity_rows)
	ui.set("_activity_panel", activity_panel)
	ui.set("_activity_scroll", activity_scroll)
	ui.set("_activity_rows", activity_rows)
	ui.call("_render_batch_item_results", gateway.planned_job)
	await process_frame
	_check(activity_rows.get_node_or_null("BatchCountsSummary") != null, "batch evidence summary was not rendered")
	for index in range(9):
		var row := activity_rows.get_node_or_null("BatchResult_%03d" % index) as Label
		_check(row != null, "result row %d is missing" % index)
		if row != null:
			_check(row.text.contains("FAILED") and row.text.contains("fixture reason %d" % (index + 1)), "result row %d omitted its failed status or reason" % index)
			_check(row.tooltip_text.contains(all_ids[index]), "result row %d omitted the bound source identity" % index)
	var rejected_job := gateway.planned_job.duplicate(true)
	rejected_job["state"] = "COMPLETE"
	rejected_job["counts"] = {"total": 9, "ready": 8, "failed": 0, "rejected": 1, "skipped": 0, "remaining": 0}
	ui.set("_batch_snapshot", rejected_job)
	ui.set("_batch_job_id", str(rejected_job["job_id"]))
	ui.call("_refresh_run_button_caption")
	_check((ui.get_node("RunLevelPipeline") as Button).text.contains("Finished With Failures"), "rejected-only completion was mislabeled as READY")

	ui.call("_show_screen", "PIXEL ART")
	_check(not (ui.get_node("LevelVariation1") as Button).visible, "Level Factory thumbnail leaked into PIXEL ART")
	ui.call("_show_screen", "RELEASE POOL")
	_check(not (ui.get_node("LevelVariation1") as Button).visible, "Level Factory thumbnail leaked into RELEASE POOL")
	ui.queue_free()
	await process_frame
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
