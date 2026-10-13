extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const SOURCE_002 := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const SOURCE_003 := "owner-upload-e26b81cc6cc364364e3bb1b5eefbb79b88556c49aabbb5d8ca8cdc6fabda8fe1"

class SelectionGateway:
	extends RefCounted
	var operations: Array[String] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		operations.append(operation)
		if operation == "validate-source-readonly":
			return {
				"source_id": SOURCE_003, "source_sha256": SOURCE_003.trim_prefix("owner-upload-"),
				"source_authority": {"source_id": SOURCE_003, "source_sha256": SOURCE_003.trim_prefix("owner-upload-")},
				"void_capability": {"state": "OPEN"}, "exact_logical_source": true,
				"structural": {"disposition": "PASS"}
			}
		if operation == "restore-source-run-readonly":
			return {"state": "SOURCE_ONLY", "source_id": SOURCE_003, "pipeline": {}}
		if operation == "candidate-inbox":
			return {"candidates": []}
		return {"state": "READY"}


func _init() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("R09-R02-R04 source UI suite: " + message)
	quit(1)


func _load_real_002_ready_run() -> Dictionary:
	var repository_root := ProjectSettings.globalize_path("res://..").simplify_path()
	var pipeline_directory := repository_root.path_join("Release/ScrubBots Factory Studio/level_factory/output/studio-extensions/pipelines")
	var files := DirAccess.get_files_at(pipeline_directory)
	var latest: Dictionary = {}
	for filename in files:
		if not filename.begins_with("pipeline-") or not filename.ends_with(".json"):
			continue
		var raw := FileAccess.get_file_as_string(pipeline_directory.path_join(filename))
		var parsed: Variant = JSON.parse_string(raw)
		if not parsed is Dictionary:
			continue
		var request: Dictionary = parsed.get("request", {})
		if parsed.get("disposition") != "READY" or request.get("source_id") != SOURCE_002 or request.get("activity_source_sha256") != SOURCE_002.trim_prefix("owner-upload-"):
			continue
		if latest.is_empty() or str(parsed.get("created_at", "")) > str(latest.get("created_at", "")):
			latest = parsed
	if not latest.is_empty():
		latest["source_id"] = SOURCE_002
	return latest


func _run() -> void:
	var pipeline := _load_real_002_ready_run()
	if pipeline.is_empty():
		_fail("read-only Release fixture has no exact saved 002 READY pipeline")
		return
	var studio := UI_SCRIPT.new()
	root.add_child(studio)
	var canvas := TextureRect.new()
	canvas.name = "MasterCanvas"
	studio.add_child(canvas)
	studio.set("_canvas", canvas)
	var live := Label.new()
	live.name = "RuntimeLiveData"
	studio.add_child(live)
	var activity_rows := VBoxContainer.new()
	studio.add_child(activity_rows)
	studio.set("_activity_rows", activity_rows)
	studio.set("_screen", "PIXEL ART")
	var gateway := SelectionGateway.new()
	studio.call("configure_gateway", gateway)
	var repository_root := ProjectSettings.globalize_path("res://..").simplify_path()
	var source_png := repository_root.path_join("Release/ScrubBots Factory Studio/level_factory/output/owner-uploads/%s/source.png" % SOURCE_003)
	studio.call("_upsert_imported_source", {
		"source_id": SOURCE_003, "source_sha256": SOURCE_003.trim_prefix("owner-upload-"),
		"path": source_png, "display_filename": "003_32x32px.png", "width": 32, "height": 32, "disposition": "IMPORTED"
	})
	studio.call("_refresh_gameplay_sources")
	if (studio.get("_gameplay_sources") as Array).is_empty():
		_fail("selection fixture was rejected by the 20..59 logical-size filter; imported=" + str(studio.get("_imported_sources")) + " gameplay=" + str(studio.get("_gameplay_sources")))
		return
	studio.set("_selected_import_source_id", SOURCE_003)
	studio.call("_select_imported_source_by_id", SOURCE_003)
	if gateway.operations.has("pipeline") or not gateway.operations.has("validate-source-readonly") or not gateway.operations.has("restore-source-run-readonly"):
		_fail("PNG selection launched a pipeline or skipped read-only preflight/session restore; calls=" + str(gateway.operations))
		return
	studio.set("_screen", "LEVEL FACTORY")
	studio.set("_pinned_source_preflight_ok", true)
	var request: Dictionary = studio.call("_build_selected_source_pipeline_request")
	if str(request.get("state", "")) != "AUTHORIZED_SOURCE_SCOPE" or str(request.get("source_id", "")) != SOURCE_003:
		_fail("independently preflighted source 003 was not authorized for explicit Run Pipeline")
		return

	studio.set("_selected_import_source_id", SOURCE_002)
	studio.set("_last_pipeline", pipeline)
	var primary: Dictionary = studio.call("_pipeline_primary_for_selected_source")
	if primary.get("state") != "READY":
		_fail("source-bound 002 saved READY run was not selected")
		return
	var verified: Dictionary = studio.call("_verify_saved_solver_artifacts", primary)
	if not verified.get("ok", false):
		_fail("actual 002 saved level/supply/result bytes did not verify: " + str(verified.get("reason", "unknown")))
		return

	studio.call("_toggle_supply_plan")
	var supply_dialog: AcceptDialog = studio.get("_supply_dialog")
	if supply_dialog == null or not supply_dialog.visible:
		_fail("supply modal did not open from the actual canonical 002 supply plan")
		return
	var supply_text := ""
	for child in supply_dialog.get_children():
		if child is RichTextLabel:
			supply_text = child.text
	if not supply_text.contains("4 columns") or not supply_text.to_lower().contains("total pixels") or not supply_text.contains("Column 4"):
		_fail("supply modal omitted actual four-column lists or aggregate totals")
		return
	studio.call("_toggle_supply_plan")
	if supply_dialog.visible:
		_fail("second supply click did not close the modal")
		return
	studio.call("_toggle_supply_plan")
	if not supply_dialog.visible:
		_fail("supply modal did not reopen on repeated click")
		return
	studio.call("_toggle_supply_plan")
	if supply_dialog.visible:
		_fail("supply modal did not close on the fourth click")
		return

	studio.call("_preview_replay")
	var replay_dialog: AcceptDialog = studio.get("_replay_dialog")
	if replay_dialog == null or not replay_dialog.visible:
		_fail("actual solution trace viewer did not open")
		return
	var replay_summary := replay_dialog.get_node("ReplaySummary") as Label
	if replay_summary == null or not replay_summary.text.contains("TRACE-ONLY") or not replay_summary.text.contains("WIN") or not replay_summary.text.contains("run pipeline-") or not replay_summary.text.contains(SOURCE_002):
		_fail("replay omitted authentic source, run, outcome or trace-only limitation")
		return
	studio.call("_set_replay_step", 1)
	var trace: Array = primary.get("result", {}).get("solution_trace", [])
	var expected: Dictionary = trace[1]
	var batch: Dictionary = expected.get("batch", {})
	var step_label: RichTextLabel = studio.get("_replay_step_label")
	if step_label == null or not step_label.text.contains("Column: %s" % str(expected.get("column", "?"))) or not step_label.text.contains("%s × %s" % [str(batch.get("color", "?")), str(batch.get("amount", "?"))]):
		_fail("step viewer did not display the corresponding authentic recorded move")
		return
	studio.call("_show_screen", "PIXEL ART")
	if supply_dialog.visible or replay_dialog.visible:
		_fail("review modals remained visible when leaving LEVEL FACTORY")
		return

	studio.set("_activity_source_id", SOURCE_002)
	studio.set("_operation_running", true)
	studio.set("_screen", "LEVEL FACTORY")
	studio.call("_refresh_live_data")
	if not live.text.contains("RUNNING") or live.text.contains("Replay: WIN") or live.text.contains("Difficulty V1: MEDIUM"):
		_fail("active run details showed stale READY/replay/difficulty evidence")
		return
	studio.set("_selected_import_source_id", SOURCE_003)
	studio.set("_last_pipeline", pipeline)
	if not studio.call("_pipeline_primary_for_selected_source").is_empty():
		_fail("source-bound 002 result leaked into selected source 003")
		return
	studio.set("_selected_import_source_id", SOURCE_002)
	studio.set("_operation_running", false)
	if studio.call("_pipeline_primary_for_selected_source").get("state") != "READY":
		_fail("return navigation did not restore the exact 002 READY record")
		return
	studio.free()
	print("R09-R02-R04 source UI suite: PASS (real 002 saved proof, explicit 003 request, hash-bound plan/replay viewer, modal lifecycle, source/tab/running-state isolation)")
	quit(0)
