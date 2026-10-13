extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const SOURCE_002 := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const SOURCE_003 := "owner-upload-e26b81cc6cc364364e3bb1b5eefbb79b88556c49aabbb5d8ca8cdc6fabda8fe1"
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R02 responsive inline PASS"

var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R02ResponsiveViewport"
	viewport.size = Vector2i(1536, 864)
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.name = "FactoryStudioR02"
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

	for client in [Vector2(1536, 864), Vector2(1536, 1024), Vector2(1920, 1080), Vector2(1200, 800)]:
		ui.size = client
		viewport.size = Vector2i(client)
		ui.call("_apply_responsive_layout")
		await process_frame
		var geometry: Dictionary = ui.call("responsive_geometry", client)
		_check(geometry.get("offset", Vector2.ONE) == Vector2.ZERO, "responsive geometry retained a centered letterbox offset at %s" % client)
		_check(geometry.get("content_size", Vector2.ZERO) == client, "responsive content does not cover the actual client at %s" % client)
		var background := ui.get_node("RuntimeBackground") as Control
		var left := ui.get_node("RuntimeLeftPanel") as Control
		var center := ui.get_node("RuntimeCanvasPanel") as Control
		var details := ui.get_node("RuntimeDetailsPanel") as Control
		var bottom := ui.get_node("RuntimeBottomStrip") as Control
		var host: Rect2 = (ui.call("preview_state_snapshot") as Dictionary).get("host_rect", Rect2())
		_check(background.size == client, "background missed client bounds at %s: %s" % [client, background.size])
		_check(left.get_global_rect().end.y >= client.y - 20.0, "left region does not reach the bottom dock at %s" % client)
		_check(details.get_global_rect().end.y >= client.y - 20.0, "Details region does not reach the bottom dock at %s" % client)
		_check(bottom.get_global_rect().end.y >= client.y - 20.0, "thumbnail dock leaves a bottom band at %s" % client)
		_check(host.position.x >= center.position.x and host.end.x <= center.get_global_rect().end.x, "Visual Review canvas escapes its center region at %s: %s" % [client, host])
		_check(host.position.y >= center.position.y and host.end.y <= center.get_global_rect().end.y, "Visual Review canvas escapes its center region vertically at %s: %s" % [client, host])
		_check(details.size.x >= 299.0, "responsive Details width dropped below the 300px target at %s" % client)

	ui.size = Vector2(1536, 864)
	viewport.size = Vector2i(1536, 864)
	ui.call("_apply_responsive_layout")
	ui.call("_show_screen", "LEVEL FACTORY")
	var row_nodes: Array[Label] = []
	for index in range(1, 6):
		var row := ui.get_node("RuntimeDetailsRow%d" % index) as Label
		row_nodes.append(row)
		_check(not row.text.contains("Source:") and not row.text.contains("owner-upload-"), "compact Details exposed source identity in row %d" % index)
	_check(row_nodes.size() <= 5, "Details has more than five compact rows")
	var preview := ui.get_node("PreviewReplay") as Button
	var supply := ui.get_node("ExpandSupplyPlan") as Button
	var solve := ui.get_node("SolveAgain") as Button
	var accept := ui.get_node("AcceptLevel") as Button
	var reject := ui.get_node("RejectLevel") as Button
	_check(absf(preview.position.y - supply.position.y) < 0.1 and preview.get_rect().end.x <= supply.position.x + 0.1, "Replay and Supply are not a single non-overlapping action row")
	_check(absf(solve.position.y - accept.position.y) < 0.1 and absf(accept.position.y - reject.position.y) < 0.1, "Solve Again / Accept / Reject are not aligned in one row")
	_check(solve.get_rect().end.x <= accept.position.x + 0.1 and accept.get_rect().end.x <= reject.position.x + 0.1, "three review/run actions overlap")
	for button in [preview, supply, solve, accept, reject]:
		_check(button.size.x >= 60.0 and button.size.y >= 30.0 and button.focus_mode == Control.FOCUS_ALL, "primary Level Factory control has no accessible hit target: %s" % button.name)
	var results := ui.get_node("LevelFactoryInlineResults") as Panel
	var results_scroll := ui.get_node("LevelFactoryInlineResults/InlineResultsLayout/InlineResultsScroll") as ScrollContainer
	_check(results_scroll.vertical_scroll_mode == ScrollContainer.SCROLL_MODE_AUTO, "inline Results panel is not vertically scrollable")
	ui.call("_preview_replay")
	_check(results.visible and ui.get("_results_mode") == "ERROR", "missing trace proof was not reported in the inline Results panel")
	_check(ui.get("_replay_dialog") == null and ui.get("_supply_dialog") == null, "Replay or Supply created an external modal")

	var release_root := ProjectSettings.globalize_path("res://").path_join("..").path_join("Release/ScrubBots Factory Studio").simplify_path()
	var source_002_path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % SOURCE_002)
	var source_003_path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % SOURCE_003)
	_check(FileAccess.file_exists(source_002_path) and FileAccess.file_exists(source_003_path), "read-only 002/003 owner PNG evidence is unavailable in the existing Release")
	ui.call("_upsert_imported_source", {"path": source_002_path, "source_id": SOURCE_002, "display_filename": "002_32x32px.png", "width": 32, "height": 32})
	ui.call("_upsert_imported_source", {"path": source_003_path, "source_id": SOURCE_003, "display_filename": "003_32x32px.png", "width": 32, "height": 32})
	var pipeline_root := release_root.path_join("level_factory/output/studio-extensions/pipelines")
	var pipeline_dir := DirAccess.open(pipeline_root)
	var saved_002: Dictionary = {}
	if pipeline_dir != null:
		for filename in pipeline_dir.get_files():
			if not filename.ends_with(".json"): continue
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(pipeline_root.path_join(filename)))
			if parsed is Dictionary and parsed.get("request", {}).get("source_id") == SOURCE_002 and parsed.get("disposition") == "READY":
				var candidate_pipeline: Dictionary = parsed
				candidate_pipeline["source_id"] = SOURCE_002
				var candidate_proof: Dictionary = ui.call("_verify_saved_solver_artifacts", candidate_pipeline.get("primary", {}))
				if candidate_proof.get("ok", false):
					saved_002 = candidate_pipeline
					break
	_check(not saved_002.is_empty(), "no genuine saved READY/WIN 002 pipeline is available for read-only panel coverage")
	if not saved_002.is_empty():
		ui.set("_selected_import_source_id", SOURCE_002)
		ui.set("_last_pipeline", saved_002)
		var saved_primary: Dictionary = ui.call("_pipeline_primary_for_selected_source")
		_check(not saved_primary.is_empty(), "saved 002 run did not bind to the selected owner source")
		var artifact_proof: Dictionary = ui.call("_verify_saved_solver_artifacts", saved_primary)
		_check(bool(artifact_proof.get("ok", false)), "saved 002 artifacts failed read-only source binding: %s" % str(artifact_proof.get("reason", "unknown")))
		ui.call("_preview_replay")
		_check(str((ui.get("_results_summary") as Label).text).contains("TRACE-ONLY") and str((ui.get("_results_summary") as Label).text).contains("Step 1 / 51"), "inline replay did not show the authentic 002 trace: %s" % str((ui.get("_results_summary") as Label).text))
		_check(results_scroll.get_child(0).get_child_count() >= 5, "inline replay step details are missing")
		ui.call("_toggle_supply_plan")
		_check(str((ui.get("_results_summary") as Label).text).contains("4 columns") and str((ui.get("_results_summary") as Label).text).contains("51 batches"), "inline supply preview did not show authentic 002 four-column / 51-batch data")
		_check(results_scroll.get_child(0).get_child_count() >= 53, "inline supply content is not scrollable through all saved batches")
		_check(ui.get("_replay_dialog") == null and ui.get("_supply_dialog") == null, "authentic Replay/Supply view created a modal")
		ui.call("_select_imported_source_by_id", SOURCE_003)
		_check(not results.visible and ui.get("_results_source_id") == "", "003 selection retained 002 inline results")
		_check(str(ui.get("_last_pipeline").get("disposition", "")) != "READY", "003 inherited the 002 READY result")
		ui.call("_select_imported_source_by_id", SOURCE_002)
		_check(not results.visible, "returning to 002 leaked a stale inline results panel")
		ui.set("_last_pipeline", saved_002)
		ui.call("_preview_replay")
	ui.call("_show_screen", "PIXEL ART")
	_check(not results.visible and ui.get("_results_mode") == "", "switching to PIXEL ART leaked Level Factory results")
	ui.call("_show_screen", "RELEASE POOL")
	_check(not results.visible, "switching to RELEASE POOL leaked Level Factory results")

	if _errors.is_empty():
		print(PASS_MARKER)
	else:
		for error in _errors: push_error(error)
		quit(1)
		return
	quit(0)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
