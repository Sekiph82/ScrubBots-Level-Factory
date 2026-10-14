extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R09 source activity scope PASS"
const FIXTURE_DIR := "res://tests/fixtures/factory_studio_r04_r01"
const FIXTURE_A := "import_01_20x20.png"
const FIXTURE_B := "import_02_20x59.png"

var _errors: Array[String] = []


class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var proof_by_source: Dictionary = {}

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "validate-source-readonly":
			var source_id := str(request.get("source_id", ""))
			var source_sha := source_id.trim_prefix("owner-upload-")
			return {
				"source_sha256": source_sha,
				"source_authority": {"source_id": source_id, "source_sha256": source_sha},
				"exact_logical_source": true,
				"void_capability": {"state": "OPEN"},
				"structural": {"disposition": "PASS"},
			}
		if operation == "restore-source-run-readonly":
			return proof_by_source.get(str(request.get("source_id", "")), {})
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		if operation == "release-pool":
			return {"state": "READY", "entries": []}
		return {"state": "UNAVAILABLE", "reason": "R09 UI test uses a read-only gateway."}

	func prepare_studio_extension_call(_operation: String, _request: Dictionary) -> Dictionary:
		return {}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		push_error("R09 navigation must never execute a solver worker")
		return {}


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R09SourceActivityScopeViewport"
	viewport.size = Vector2i(1536, 960)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.name = "FactoryStudioR09SourceActivityScope"
	ui.set_script(UI_SCRIPT)
	ui.size = Vector2(1536, 960)
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
	ui.set("_gateway", gateway)
	ui.call("_show_screen", "LEVEL FACTORY")
	var sources := _make_sources(140)
	ui.set("_imported_sources", sources)
	ui.call("_refresh_gameplay_sources")
	var composite_items := _make_composite_items(sources)
	var prior_job := _make_job(sources.slice(0, 9), 9, "COMPLETE", 8, "old-nine-job")
	var nine_run_ids := PackedStringArray()
	for item in prior_job["items"]:
		nine_run_ids.append(str(item.get("run_id", "")))
	var pool_before := {"state": "READY", "entries": _make_pool_entries(9)}
	ui.set("_release_pool", pool_before.duplicate(true))
	ui.set("_batch_import_id", "current-140-import")
	ui.set("_batch_composite_snapshot", {"batch_id": "current-140-import", "items": composite_items})
	ui.set("_batch_snapshot", prior_job.duplicate(true))
	ui.set("_batch_job_id", "old-nine-job")
	ui.set("_batch_job_source_mismatch", false)
	var prior_snapshot := prior_job.duplicate(true)

	var source_011 := _source_id_for_filename(sources, "011_32x32px.png")
	var source_009 := _source_id_for_filename(sources, "009_32x32px.png")
	var source_012 := _source_id_for_filename(sources, "012_32x32px.png")
	var selected_009 := _source_for_id(sources, source_009)
	gateway.proof_by_source[source_009] = {
		"state": "READY",
		"source_sha256": str(selected_009.get("source_sha256", "")),
		"candidate_id": "candidate-009",
		"pipeline": {
			"disposition": "READY", "run_id": "run-009", "source_id": source_009,
			"request": {"source_id": source_009, "column_count": 4},
			"primary": {"state": "WIN"},
			"difficulty": {"class": "STANDARD"},
		},
	}

	ui.call("_select_imported_source_by_id", source_011)
	_check(str(ui.get("_selected_import_source_id")) == source_011, "selection did not stay on unsolved PNG 011")
	_check(str(ui.get("_activity_state_label").text) == "SOURCE ONLY", "011 inherited READY or another status from the old nine-item job")
	_check(str(ui.get("_activity_source_label").text).contains("011_32x32px.png"), "Activity header does not identify selected 011")
	_check(_activity_row_texts(ui).is_empty(), "011 Activity contains rows from the unrelated old 002-010 job")
	_check(_detail_text(ui).contains("011_32x32px.png") and _detail_text(ui).contains("SOURCE_ONLY"), "Details do not identify 011 as SOURCE_ONLY")
	_check(str(ui.get("_active_preview_path")) == str(_source_for_id(sources, source_011).get("path", "")), "center preview does not remain on 011")
	_check(_five_card_filenames(ui) == ["009", "010", "011", "012", "013"], "five-card gallery is not centered on 011")
	_check(bool(ui.call("_batch_job_matches_loaded_sources")) == false, "old nine-item job incorrectly matches the loaded 140-source scope")
	var entire_batch_button := ui.get_node_or_null("RunLevelPipeline") as Button
	_check(entire_batch_button != null and entire_batch_button.text == "Run Entire Loaded Batch (140)" and not entire_batch_button.disabled, "the explicit 140-source batch action is not available after source-only selection")

	ui.call("_select_imported_source_by_id", source_009)
	var selected_rows := _activity_row_texts(ui)
	var selected_events: Array = ui.get("_activity_events")
	_check(str(ui.get("_activity_state_label").text) == "READY", "verified historical source 009 did not restore its own READY status")
	_check(selected_rows.size() == 1 and selected_rows[0].contains("Restored exact source-bound"), "009 view does not contain exactly its own source-bound proof")
	_check(selected_events.size() == 1 and str(selected_events[0].get("source_id", "")) == source_009, "009 Activity proof is not bound to the selected source identity")
	ui.call("_select_imported_source_by_id", source_012)
	_check(str(ui.get("_activity_state_label").text) == "SOURCE ONLY", "unsolved 012 inherited a previous source status")
	_check(_activity_row_texts(ui).is_empty(), "012 Activity retained rows from another PNG")
	ui.call("_select_imported_source_by_id", source_011)
	ui.call("_show_screen", "PIXEL ART")
	ui.call("_show_screen", "LEVEL FACTORY")
	_check(str(ui.get("_activity_state_label").text) == "SOURCE ONLY" and _activity_row_texts(ui).is_empty(), "tab switching restored unrelated old batch Activity")
	_check(ui.get("_batch_snapshot") == prior_snapshot, "historical nine-job evidence was modified while browsing sources")
	_check(ui.get("_release_pool") == pool_before, "the existing nine READY Pool entries changed during source browsing")
	_check(nine_run_ids.size() == 9 and str(prior_snapshot.get("state", "")) == "COMPLETE", "historical nine-source proof fixture was not preserved")

	_test_active_source_follow(ui, gateway, 9)
	_test_active_source_follow(ui, gateway, 140)
	var forbidden_calls := _forbidden_gateway_calls(gateway)
	_check(forbidden_calls.is_empty(), "navigation or render triggered prohibited gateway calls: %s" % ", ".join(forbidden_calls))
	viewport.free()
	await process_frame
	if _errors.is_empty():
		print(PASS_MARKER)
	else:
		for message in _errors:
			push_error(message)
		quit(1)
		return
	quit(0)


func _test_active_source_follow(ui: Control, gateway: ReadOnlyGateway, source_count: int) -> void:
	var sources := _make_sources(source_count)
	ui.set("_imported_sources", sources)
	ui.call("_refresh_gameplay_sources")
	var batch_id := "active-%d-import" % source_count
	var job := _make_job(sources, source_count, "RUNNING", 3, "active-%d-job" % source_count)
	job["import_batch_id"] = batch_id
	var composite := {"batch_id": batch_id, "items": _make_composite_items(sources)}
	ui.set("_batch_import_id", batch_id)
	ui.set("_batch_composite_snapshot", composite)
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.set("_batch_job_id", str(job.get("job_id", "")))
	ui.set("_batch_job_source_mismatch", false)
	ui.set("_operation_running", true)
	var active_source_005 := str(sources[3].get("source_id", ""))
	var active_source_006 := str(sources[4].get("source_id", ""))
	ui.call("_sync_verified_batch_follow", job)
	_check(str(ui.get("_activity_source_id")) == active_source_005 and _detail_text(ui).contains("005_32x32px.png"), "%d-item active job did not align Activity and Details to 005" % source_count)
	var items: Array = job.get("items", [])
	var finished_item: Dictionary = items[3]
	finished_item["status"] = "READY"
	var finished_run_id := "run-%d-005" % source_count
	finished_item["run_id"] = finished_run_id
	items[3] = finished_item
	job["items"] = items
	job["current_index"] = 3
	var source_005: Dictionary = sources[3]
	gateway.proof_by_source[active_source_005] = {
		"state": "READY", "source_sha256": str(source_005.get("source_sha256", "")),
		"pipeline": {
			"disposition": "READY", "run_id": finished_run_id, "source_id": active_source_005,
			"request": {"source_id": active_source_005, "column_count": 3},
			"primary": {"state": "WIN"}, "difficulty": {"class": "STANDARD"},
		},
	}
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	ui.call("_record_verified_batch_item_progress", job)
	_check(_activity_row_texts(ui).size() == 1 and _activity_row_texts(ui)[0].contains("005_32x32px.png"), "%d-item completed current item 005 did not produce one source-specific row" % source_count)
	job["current_index"] = 4
	var next_item: Dictionary = items[4]
	next_item["status"] = "RUNNING"
	items[4] = next_item
	job["items"] = items
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	ui.call("_record_verified_batch_item_progress", job)
	_check(str(ui.get("_activity_source_id")) == active_source_006 and _detail_text(ui).contains("006_32x32px.png"), "%d-item active job did not advance Activity and Details to 006" % source_count)
	for row_text in _activity_row_texts(ui):
		_check(not row_text.contains("005_32x32px.png"), "%d-item Activity retained completed 005 after current source advanced to 006" % source_count)
	_check(_five_card_filenames(ui).has("006"), "%d-item active job did not move the five-card window with current source 006" % source_count)
	job["state"] = "PAUSED"
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	_check(str(ui.get("_activity_state_label").text) == "PAUSED" and str(ui.get("_activity_stage")) == "PAUSED", "%d-item Activity did not follow PAUSED state for current source 006" % source_count)
	job["state"] = "INTERRUPTED"
	ui.set("_operation_running", false)
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	_check(str(ui.get("_activity_state_label").text) == "INTERRUPTED" and str(ui.get("_activity_stage")) == "INTERRUPTED", "%d-item Activity did not follow INTERRUPTED recovery state for current source 006" % source_count)
	job["state"] = "RUNNING"
	ui.set("_operation_running", true)
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	_check(str(ui.get("_activity_state_label").text) == "RUNNING" and str(ui.get("_activity_stage")) == "RUNNING", "%d-item Activity did not restore RUNNING state for current source 006" % source_count)
	var ready_006: Dictionary = items[4]
	var ready_run_id := "run-%d-006" % source_count
	ready_006["status"] = "READY"
	ready_006["run_id"] = ready_run_id
	items[4] = ready_006
	job["items"] = items
	job["state"] = "COMPLETE"
	job["counts"] = {"total": source_count, "ready": 2, "failed": 0, "rejected": 0, "skipped": 0, "remaining": source_count - 2}
	var source_006: Dictionary = sources[4]
	gateway.proof_by_source[active_source_006] = {
		"state": "READY", "source_sha256": str(source_006.get("source_sha256", "")),
		"pipeline": {
			"disposition": "READY", "run_id": ready_run_id, "source_id": active_source_006,
			"request": {"source_id": active_source_006, "column_count": 4},
			"primary": {"state": "WIN"}, "difficulty": {"class": "STANDARD"},
		},
	}
	ui.set("_operation_running", false)
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_sync_verified_batch_follow", job)
	ui.call("_record_verified_batch_item_progress", job)
	_check(str(ui.get("_activity_state_label").text) == "READY" and _activity_row_texts(ui).size() == 1 and _activity_row_texts(ui)[0].contains("006_32x32px.png"), "%d-item completed 006 did not show only its own authenticated READY activity" % source_count)
	ui.set("_operation_running", false)
	ui.set("_batch_job_id", "")


func _make_sources(count: int) -> Array[Dictionary]:
	var sources: Array[Dictionary] = []
	var fixture_a := ProjectSettings.globalize_path("%s/%s" % [FIXTURE_DIR, FIXTURE_A])
	var fixture_b := ProjectSettings.globalize_path("%s/%s" % [FIXTURE_DIR, FIXTURE_B])
	var sha_a := _file_sha256(fixture_a)
	var sha_b := _file_sha256(fixture_b)
	for index in range(count):
		var number := index + 2
		var filename := "%03d_32x32px.png" % number
		var source_sha := "%064x" % (2000 + index)
		var path := fixture_a
		if number == 5:
			source_sha = sha_a
		elif number == 6:
			source_sha = sha_b
			path = fixture_b
		sources.append({
			"source_id": "owner-upload-" + source_sha,
			"source_sha256": source_sha,
			"source_record_sha256": "%064x" % (5000 + index),
			"path": path,
			"display_filename": filename,
			"width": 32, "height": 32, "disposition": "IMPORTED",
		})
	return sources


func _make_composite_items(sources: Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for source in sources:
		result.append({
			"source_id": str(source.get("source_id", "")),
			"source_sha256": str(source.get("source_sha256", "")),
			"source_record_sha256": str(source.get("source_record_sha256", "")),
		})
	return result


func _make_job(sources: Array, count: int, state: String, current_index: int, job_id: String) -> Dictionary:
	var items: Array[Dictionary] = []
	for index in range(count):
		var source: Dictionary = sources[index]
		items.append({
			"job_id": job_id, "index": index,
			"source_id": str(source.get("source_id", "")),
			"source_sha256": str(source.get("source_sha256", "")),
			"source_record_sha256": str(source.get("source_record_sha256", "")),
			"attempt_id": "%s-attempt-%03d" % [job_id, index],
			"column_count": 3 + (index % 3),
			"status": "READY" if state == "COMPLETE" else "QUEUED",
			"original_filename": str(source.get("display_filename", "PNG")),
			"run_id": "%s-run-%03d" % [job_id, index] if state == "COMPLETE" else "",
			"reason": "",
		})
	if state == "RUNNING" and current_index >= 0 and current_index < items.size():
		items[current_index]["status"] = "RUNNING"
	return {
		"job_id": job_id, "import_batch_id": "current-140-import",
		"snapshot_source_count": count, "current_index": current_index,
		"state": state, "items": items,
		"counts": {"total": count, "ready": count if state == "COMPLETE" else 0, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 0 if state == "COMPLETE" else count},
	}


func _make_pool_entries(count: int) -> Array[Dictionary]:
	var entries: Array[Dictionary] = []
	for index in range(count):
		entries.append({"candidate_id": "ready-%03d" % index, "disposition": "READY"})
	return entries


func _source_id_for_filename(sources: Array, filename: String) -> String:
	return str(_source_for_filename(sources, filename).get("source_id", ""))


func _source_for_filename(sources: Array, filename: String) -> Dictionary:
	for source in sources:
		if str(source.get("display_filename", "")) == filename:
			return source
	return {}


func _source_for_id(sources: Array, source_id: String) -> Dictionary:
	for source in sources:
		if str(source.get("source_id", "")) == source_id:
			return source
	return {}


func _activity_row_texts(ui: Control) -> Array[String]:
	var result: Array[String] = []
	var rows := ui.get("_activity_rows") as VBoxContainer
	if rows == null:
		return result
	for child in rows.get_children():
		if child is Label:
			result.append((child as Label).text)
	return result


func _detail_text(ui: Control) -> String:
	var result := ""
	var rows: Array = ui.get("_details_rows")
	for row in rows:
		if row is Label:
			result += (row as Label).text + "\n"
	return result


func _five_card_filenames(ui: Control) -> Array[String]:
	var result: Array[String] = []
	for slot in range(1, 6):
		var button := ui.get_node_or_null("LevelVariation%d" % slot) as Button
		if button == null:
			continue
		var line := button.text.split("\n")[0].replace("● ", "")
		result.append(line.get_slice("_", 0))
	return result



func _file_sha256(path: String) -> String:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return ""
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		file.close()
		return ""
	while not file.eof_reached():
		context.update(file.get_buffer(65536))
	file.close()
	return context.finish().hex_encode()


func _forbidden_gateway_calls(gateway: ReadOnlyGateway) -> Array[String]:
	var result: Array[String] = []
	for call_record in gateway.calls:
		var operation := str(call_record.get("operation", ""))
		if operation in ["png-batch-create", "png-batch-run", "pipeline-run", "solve", "replay", "load-check", "publish-staging", "publish-production"]:
			result.append(operation)
	return result


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
