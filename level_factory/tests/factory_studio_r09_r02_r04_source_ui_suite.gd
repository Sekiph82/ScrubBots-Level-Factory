extends SceneTree

## R09-R02-R04 source UI, rewritten 2026-11-12.
##
## The owner's saved 002 READY pipeline was deleted with the 2026-11-07 cleanup,
## so this suite writes a hash-bound READY fixture (level, supply plan, result)
## inside the isolated checkout copy. Supply and replay review moved from modal
## dialogs to the inline LevelFactoryInlineResults panel. Still checked: source
## selection is read-only, a saved proof is bound to its own source and run,
## artifact hashes are verified before anything is shown, the replay is labelled
## TRACE-ONLY, results never leak to another source or tab, and a running
## worker never shows a stale READY/replay verdict.

const MAIN_SCENE := "res://scenes/factory_studio.tscn"
const TEST_PATHS := preload("res://tests/factory_test_paths.gd")
const READY_FIXTURE := preload("res://tests/factory_test_ready_fixture.gd")
const SOURCE_002 := "owner-upload-%s" % "0000000000000000000000000000000000000000000000000000000000000a02"
const SOURCE_003 := "owner-upload-%s" % "0000000000000000000000000000000000000000000000000000000000000a03"
const RUN_ID := "pipeline-r09r02r04-fixture"


class SelectionGateway:
	extends RefCounted
	var operations: Array[String] = []
	var prepared: Array[String] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		operations.append(operation)
		if operation == "validate-source-readonly":
			var source_id := str(request.get("source_id", ""))
			var sha := source_id.trim_prefix("owner-upload-")
			return {"source_id": source_id, "source_sha256": sha, "source_authority": {"source_id": source_id, "source_sha256": sha},
				"void_capability": {"state": "OPEN"}, "exact_logical_source": true, "structural": {"disposition": "PASS"}}
		if operation == "restore-source-run-readonly":
			return {"state": "SOURCE_ONLY", "source_id": request.get("source_id", ""), "pipeline": {}}
		if operation == "candidate-inbox":
			return {"candidates": []}
		return {"state": "READY"}

	func prepare_studio_extension_call(operation: String, _request: Dictionary) -> Dictionary:
		prepared.append(operation)
		return {}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		return {"state": "UNAVAILABLE"}  # a startup read prepared before this fixture took over


func _init() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("R09-R02-R04 source UI suite: " + message)
	quit(1)


func _rows_text(studio: Node) -> String:
	var text := ""
	var rows := studio.get_node_or_null("LevelFactoryInlineResults") as Control
	if rows == null:
		return ""
	for label in rows.find_children("*", "Label", true, false):
		text += (label as Label).text + "\n" + (label as Label).tooltip_text + "\n"
	return text


func _details(studio: Node) -> String:
	var text := ""
	for row in studio.get("_details_rows"):
		text += (row as Label).text + "\n"
	return text


func _run() -> void:
	var packed := load(MAIN_SCENE) as PackedScene
	var instance := packed.instantiate()
	root.add_child(instance)
	await process_frame
	var studio := instance.get_node("MasterUI") as Control
	var gateway := SelectionGateway.new()
	studio.call("configure_gateway", gateway)
	studio.set("_studio_read_queue", [])
	studio.call("_apply_restored_imported_sources", {"schema": "scrubbots-source-library-view", "sources": []})
	studio.set("_owner_release_archive", {"schema": "scrubbots-owner-release-library-view/v1", "records": []})
	studio.set("_owner_release_archive_loaded", true)
	studio.set("_startup_release_archive_settled", true)
	studio.set("_startup_pending_batch_restore_started", true)
	studio.set("_batch_restore_pending", false)
	studio.set("_release_pool_loaded", true)
	studio.call("_apply_startup_gate")
	var fixture_png := ProjectSettings.globalize_path("res://tests/fixtures/factory_studio_r04_r01/import_03_32x32.png")
	for source_id in [SOURCE_002, SOURCE_003]:
		studio.call("_upsert_imported_source", {"source_id": source_id, "path": fixture_png,
			"display_filename": "%s_32x32px.png" % ("002" if source_id == SOURCE_002 else "003"), "width": 32, "height": 32, "disposition": "IMPORTED"})
	studio.call("_refresh_gameplay_sources")
	studio.call("_show_screen", "LEVEL FACTORY")
	gateway.operations.clear()

	# 1. Selecting a PNG is read-only (preflight + saved-run restore, never a pipeline).
	studio.call("_select_imported_source_by_id", SOURCE_003)
	await process_frame
	if gateway.operations.has("pipeline") or gateway.prepared.any(func(operation: String) -> bool: return operation.contains("pipeline") or operation.contains("batch-run")):
		_fail("PNG selection launched a pipeline; calls=%s prepared=%s" % [gateway.operations, gateway.prepared])
		return
	studio.call("_refresh_pinned_source_preflight")
	var request: Dictionary = studio.call("_build_selected_source_pipeline_request")
	if str(request.get("state", "")) != "AUTHORIZED_SOURCE_SCOPE" or str(request.get("source_id", "")) != SOURCE_003:
		_fail("independently preflighted source 003 was not authorized for an explicit run: %s" % [request])
		return

	# 2. The saved READY proof is bound to its own source and its bytes verify.
	var pipeline := READY_FIXTURE.build(SOURCE_002, RUN_ID)
	studio.set("_selected_import_source_id", SOURCE_002)
	studio.set("_last_pipeline", pipeline)
	var primary: Dictionary = studio.call("_pipeline_primary_for_selected_source")
	if primary.get("state") != "READY":
		_fail("source-bound 002 saved READY run was not selected")
		return
	var verified: Dictionary = studio.call("_verify_saved_solver_artifacts", primary)
	if not verified.get("ok", false):
		_fail("saved level/supply/result bytes did not verify: %s" % verified.get("reason", "unknown"))
		return

	# 3. Supply plan review (inline): four columns with aggregate totals.
	studio.call("_toggle_supply_plan")
	var panel := studio.get_node("LevelFactoryInlineResults") as Control
	var supply_summary := (studio.get("_results_summary") as Label).text
	var supply_rows := _rows_text(studio)
	if not panel.visible or not supply_summary.contains("4 columns") or not supply_rows.contains("Total robots") or not supply_rows.contains("total pixels") or not supply_rows.contains("Column 4") or not supply_rows.contains("Conservation: PASS"):
		_fail("inline supply review omitted columns or aggregate totals: %s | %s" % [supply_summary, supply_rows])
		return

	# 4. Replay review is TRACE-ONLY, bound to source and run, and steps through the recorded moves.
	studio.call("_preview_replay")
	var summary := studio.get("_results_summary") as Label
	if not summary.text.contains("TRACE-ONLY") or not summary.tooltip_text.contains(SOURCE_002) or not summary.tooltip_text.contains(RUN_ID):
		_fail("replay omitted its trace-only limitation, source or run: %s / %s" % [summary.text, summary.tooltip_text])
		return
	studio.call("_set_replay_step", 1)
	var expected: Dictionary = primary["result"]["solution_trace"][1]
	var step_rows := _rows_text(studio)
	if not step_rows.contains("Column: %s" % str(expected["column"])) or not step_rows.contains("%s × %s" % [str(expected["batch"]["color"]), str(expected["batch"]["amount"])]):
		_fail("step viewer did not display the recorded move: %s" % step_rows)
		return

	# 5. Tampered saved bytes fail closed.
	var level_path: String = primary["files"]["level"]
	var original := FileAccess.get_file_as_string(level_path)
	READY_FIXTURE.write_text(level_path, original + " ")
	if (studio.call("_verify_saved_solver_artifacts", primary) as Dictionary).get("ok", false):
		_fail("a modified saved level file still verified")
		return
	READY_FIXTURE.write_text(level_path, original)

	# 6. Results never leak to another tab, another source or a running worker.
	studio.call("_show_screen", "PIXEL ART")
	if panel.visible:
		_fail("inline results remained visible when leaving LEVEL FACTORY")
		return
	studio.call("_show_screen", "LEVEL FACTORY")
	studio.set("_activity_source_id", SOURCE_002)
	studio.set("_operation_running", true)
	studio.call("_refresh_live_data")
	var running_details := _details(studio)
	if not running_details.contains("RUNNING") or running_details.contains("Replay WIN") or running_details.contains("Difficulty MEDIUM"):
		_fail("active run details showed stale READY/replay/difficulty evidence: %s" % running_details)
		return
	studio.set("_operation_running", false)
	studio.set("_selected_import_source_id", SOURCE_003)
	if not (studio.call("_pipeline_primary_for_selected_source") as Dictionary).is_empty():
		_fail("source-bound 002 result leaked into selected source 003")
		return
	studio.set("_selected_import_source_id", SOURCE_002)
	if (studio.call("_pipeline_primary_for_selected_source") as Dictionary).get("state") != "READY":
		_fail("return navigation did not restore the exact 002 READY record")
		return
	instance.free()
	print("R09-R02-R04 source UI suite: PASS (hash-bound saved proof, explicit 003 request, inline plan/replay review, source/tab/running-state isolation)")
	quit(0)
