extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R05 loaded PNG batch UI PASS"

class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var source_ids: Array[String] = []
	var planned_job: Dictionary = {}
	var extension_responses: Dictionary = {}

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if extension_responses.has(operation):
			var response: Variant = extension_responses[operation]
			return response.duplicate(true) if response is Dictionary else response
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
	ui.call("_apply_responsive_layout")
	await process_frame
	var original_dock_rects := _dock_rect_snapshot(ui)
	ui.size = Vector2(1200, 800)
	viewport.size = Vector2i(1200, 800)
	ui.call("_apply_responsive_layout")
	await process_frame
	ui.size = Vector2(1536, 864)
	viewport.size = Vector2i(1536, 864)
	ui.call("_apply_responsive_layout")
	await process_frame
	_check(_dock_rect_snapshot(ui) == original_dock_rects, "existing R04-R04 thumbnail dock geometry drifted after resize-back")
	_check((ui.get_node("RuntimeBottomHeading") as Label).text.contains("9 PNG"), "gallery count does not show all nine loaded PNGs")

	var dock_center := (ui.get_node("RuntimeBottomStrip") as Control).get_global_rect().get_center()
	for _step in range(4):
		var wheel := InputEventMouseButton.new()
		wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
		wheel.pressed = true
		wheel.global_position = dock_center
		ui.call("_unhandled_input", wheel)
	_check(int(ui.get("_imported_window_start")) == 4, "nine-source gallery did not slide to the clamped five-source window")
	_check((ui.get_node("RuntimeBottomHeading") as Label).text.contains("9 PNG") and not (ui.get_node("RuntimeBottomHeading") as Label).text.contains("1/2"), "gallery still exposes page-based navigation")
	_check((ui.get_node("LevelVariation5") as Button).text.contains("010"), "ninth source is not visible in the fifth thumbnail slot")
	(ui.get_node("LevelVariation5") as Button).emit_signal("pressed")
	_check(str(ui.get("_selected_import_source_id")) == all_ids[8], "sliding-window thumbnail did not select the ninth source")
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
	var phase := ui.get("_activity_phase_label") as Label
	_check(phase != null and phase.tooltip_text.contains("Planned 3/4/5 4/4/1"), "batch quota summary was not retained with the activity status")
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
	_test_loaded_batch_restore_nullable_contract(ui, gateway, all_ids)

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


func _test_loaded_batch_restore_nullable_contract(ui: Control, gateway: ReadOnlyGateway, source_ids: Array[String]) -> void:
	var composite_items: Array[Dictionary] = []
	var gameplay_sources: Array = ui.get("_gameplay_sources")
	for index in range(source_ids.size()):
		var source_id: String = source_ids[index]
		var source: Dictionary = gameplay_sources[index]
		composite_items.append({
			"source_id": source_id,
			"source_sha256": str(source.get("source_sha256", "")),
			"source_record_sha256": str(source.get("source_record_sha256", "")),
		})
	var composite := {"batch_id": "batch-restored-fixture", "items": composite_items}
	var saved_items: Array[Dictionary] = []
	for index in range(source_ids.size()):
		saved_items.append({
			"index": index, "source_id": source_ids[index],
			"source_sha256": str(gameplay_sources[index].get("source_sha256", "")),
			"source_record_sha256": str(gameplay_sources[index].get("source_record_sha256", "")),
			"status": "FAILED", "attempt_id": "restore-attempt-%d" % index,
		})
	var saved_job := {
		"job_id": "saved-restore-fixture", "import_batch_id": "batch-restored-fixture",
		"state": "PAUSED", "items": saved_items,
		"counts": {"total": 9, "ready": 7, "failed": 2, "remaining": 2},
	}
	var cases := [
		{"name": "no matching composite", "resolved": {"disposition": "NO_MATCHING_COMPOSITE", "batch": null}, "latest": null, "mismatch": false},
		{"name": "ambiguous null composite", "resolved": {"disposition": "LEGACY_COMPOSITE_AMBIGUOUS", "batch": null}, "latest": null, "mismatch": true},
		{"name": "snapshot mismatch null composite", "resolved": {"disposition": "SOURCE_SNAPSHOT_MISMATCH", "batch": null}, "latest": null, "mismatch": true},
		{"name": "no matching job", "resolved": {"disposition": "MATCHED", "batch": composite}, "latest": {"disposition": "NO_MATCHING_JOB", "job": null}, "mismatch": false},
		{"name": "batch job source mismatch", "resolved": {"disposition": "MATCHED", "batch": composite}, "latest": {"disposition": "BATCH_JOB_SOURCE_MISMATCH", "job": null}, "mismatch": true},
		{"name": "valid paused job", "resolved": {"disposition": "MATCHED", "batch": composite}, "latest": {"disposition": "MATCHED", "job": saved_job}, "mismatch": false},
	]
	for test_case in cases:
		_reset_restore_state(ui, gateway)
		var latest: Variant = test_case["latest"]
		gateway.extension_responses = {"loaded-png-batch-find": test_case["resolved"]}
		if latest is Dictionary:
			gateway.extension_responses["png-batch-latest"] = latest
		ui.call("_restore_loaded_png_batch_readonly")
		var case_name := str(test_case["name"])
		_check(bool(ui.get("_batch_job_source_mismatch")) == bool(test_case["mismatch"]), "%s produced the wrong lineage gate" % case_name)
		if bool(test_case["mismatch"]):
			var run_button := ui.get_node("RunLevelPipeline") as Button
			_check(run_button.disabled and run_button.text.contains("mismatch"), "%s did not visibly block Resume/Retry" % case_name)
			ui.call("_run_level_pipeline")
			_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")).contains("create") or str(call.get("operation", "")).contains("run")), "%s explicit Run created or started a new job" % case_name)
		_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")).contains("create") or str(call.get("operation", "")).contains("run")), "%s created or started work" % case_name)
		if case_name in ["no matching composite", "ambiguous null composite", "snapshot mismatch null composite"]:
			_check(str(ui.get("_batch_import_id")) == "" and str(ui.get("_batch_job_id")) == "", "%s fabricated restored batch/job identity" % case_name)
			_check((ui.get("_batch_snapshot") as Dictionary).is_empty(), "%s changed saved job snapshot" % case_name)
		elif case_name in ["no matching job", "batch job source mismatch"]:
			_check(str(ui.get("_batch_import_id")) == "batch-restored-fixture" and str(ui.get("_batch_job_id")) == "", "%s fabricated a saved job identity" % case_name)
			_check((ui.get("_batch_snapshot") as Dictionary).is_empty(), "%s fabricated READY/job state" % case_name)
		else:
			_check(str(ui.get("_batch_job_id")) == "saved-restore-fixture", "valid saved job identity was not restored")
			var restored: Dictionary = ui.get("_batch_snapshot")
			var counts: Dictionary = restored.get("counts", {})
			_check(int(counts.get("total", 0)) == 9 and int(counts.get("ready", 0)) == 7 and int(counts.get("failed", 0)) == 2, "valid saved job counts changed")
			_check((ui.get_node("RunLevelPipeline") as Button).text.contains("Resume Batch · 2 remaining"), "valid saved job did not preserve resume status")
	_reset_restore_state(ui, gateway)
	gateway.extension_responses = {
		"loaded-png-batch-find": {"disposition": "MATCHED", "batch": composite},
		"png-batch-latest": {"disposition": "MATCHED", "job": saved_job.duplicate(true)},
	}
	var malformed_job: Dictionary = gateway.extension_responses["png-batch-latest"]["job"]
	malformed_job["counts"] = null
	ui.call("_restore_loaded_png_batch_readonly")
	var sanitized_snapshot: Dictionary = ui.get("_batch_snapshot")
	_check(str(ui.get("_batch_job_id")) == "saved-restore-fixture", "malformed optional counts discarded a valid job")
	_check(sanitized_snapshot.get("counts", null) is Dictionary and (sanitized_snapshot["counts"] as Dictionary).is_empty(), "malformed optional counts were not safely isolated in local UI state")
	_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")).contains("create") or str(call.get("operation", "")).contains("run")), "malformed counts started work")
	_reset_restore_state(ui, gateway)
	ui.call("_restore_loaded_png_batch_readonly")
	_check(str(ui.get("_batch_job_id")) == "", "fresh restore reused stale job identity")
	_check(not gateway.calls.any(func(call: Dictionary) -> bool: return str(call.get("operation", "")).contains("create") or str(call.get("operation", "")).contains("run")), "fresh restore started work")


func _reset_restore_state(ui: Control, gateway: ReadOnlyGateway) -> void:
	ui.set("_batch_import_id", "")
	ui.set("_batch_job_id", "")
	ui.set("_batch_composite_snapshot", {})
	ui.set("_batch_snapshot", {})
	ui.set("_batch_job_source_mismatch", false)
	ui.set("_batch_legacy_reconciliation", false)
	gateway.calls.clear()
	gateway.extension_responses.clear()


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)


func _dock_rect_snapshot(ui: Control) -> Dictionary:
	var result := {}
	for node_name in ["RuntimeBottomStrip", "RuntimeBottomHeading", "LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5"]:
		result[node_name] = (ui.get_node(node_name) as Control).get_global_rect()
	return result
