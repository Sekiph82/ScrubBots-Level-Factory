extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R07 five-slot release dashboard PASS"

class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []
	var release_pool: Dictionary = {"state": "READY", "entries": [], "pool_size": 0}
	var restored_run: Dictionary = {}

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "release-pool":
			return release_pool.duplicate(true)
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		if operation == "restore-source-run-readonly":
			return restored_run.duplicate(true)
		return {"state": "UNAVAILABLE", "reason": "R07 dashboard suite uses a read-only fake gateway."}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R07ReleaseDashboardViewport"
	viewport.size = Vector2i(1920, 1080)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.name = "FactoryStudioR07ReleaseDashboard"
	ui.set_script(UI_SCRIPT)
	ui.size = Vector2(1920, 1080)
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
	ui.call("_show_screen", "RELEASE POOL")
	await process_frame
	var sizes: Array[Vector2i] = [Vector2i(1536, 864), Vector2i(1536, 1024), Vector2i(1920, 1080), Vector2i(1536, 864)]
	for client in sizes:
		viewport.size = client
		ui.size = Vector2(client)
		ui.call("_apply_responsive_layout")
		await process_frame
		var left := ui.get_node("RuntimeLeftPanel") as Control
		var dock := ui.get_node("RuntimeBottomStrip") as Control
		var preview := ui.get_node("VisualReviewClip") as Control
		var scroll := ui.get_node("ReleaseCandidateScroll") as Control
		var manage := ui.get_node("ManageSelection") as Control
		var select_all := ui.get_node("SelectAllRelease") as Control
		var clear := ui.get_node("ClearRelease") as Control
		_check(_contains_with_padding(Rect2(left.position, left.size), Rect2(scroll.position, scroll.size), 4.0), "candidate list escapes left panel at %s" % client)
		_check(scroll.get_global_rect().end.y <= manage.get_global_rect().position.y + 0.5, "candidate list overlaps Manage Selection at %s" % client)
		_check(_contains_with_padding(Rect2(left.position, left.size), manage.get_global_rect(), 4.0), "Manage Selection is not pinned inside the left panel at %s" % client)
		_check(_contains_with_padding(Rect2(left.position, left.size), select_all.get_global_rect(), 4.0), "Select All is not pinned inside the left panel at %s" % client)
		_check(_contains_with_padding(Rect2(left.position, left.size), clear.get_global_rect(), 4.0), "Clear is not pinned inside the left panel at %s" % client)
		for node_name in ["SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "AddMoreLevels"]:
			var item := (ui.get_node(node_name) as Control).get_global_rect()
			_check(_contains_with_padding(dock.get_global_rect(), item, 3.0), "%s escapes selected-release bottom dock at %s" % [node_name, client])
			_check(not item.intersects(preview.get_global_rect()), "%s overlaps Visual Review at %s" % [node_name, client])
		if client == Vector2i(1920, 1080):
			var visible_rows := floori(scroll.size.y / (float(ui.get("_release_candidate_row_height")) + 3.0))
			_check(visible_rows >= 14 and visible_rows <= 15, "maximized 1920x1080 list exposes %d rows instead of 14-15" % visible_rows)

	for amount in [0, 5, 15, 25, 150]:
		var entries: Array[Dictionary] = []
		for index in range(amount):
			var candidate_id := "candidate-r07-%03d" % index
			entries.append({
				"candidate_id": candidate_id,
				"level_id": "R07 Level %03d" % index,
				"pipeline": {"primary": {"disposition": "READY", "column_count": 3 + (index % 3)}},
				"pipeline_run_id": "run-%03d" % index,
				"pipeline_sha256": "%064x" % (index + 1),
				"entry_digest": "%064x" % (index + 2),
			})
		gateway.release_pool = {"state": "READY", "entries": entries, "pool_size": amount}
		ui.set("_release_pool", gateway.release_pool.duplicate(true))
		ui.set("_selected_release_ids", [])
		ui.call("_apply_release_projection")
		await process_frame
		var rows := ui.get_node("ReleaseCandidateScroll/ReleaseCandidateRows") as VBoxContainer
		_check(rows.get_child_count() == amount, "%d candidates produced %d selectable rows" % [amount, rows.get_child_count()])
		_check((ui.get_node("ReleaseCandidateScroll") as ScrollContainer).vertical_scroll_mode == ScrollContainer.SCROLL_MODE_AUTO, "candidate gallery is not vertically scrollable")
		if amount > 0:
			ui.call("_select_all_release")
			var selected: Array = ui.get("_selected_release_ids")
			_check(selected.size() == amount, "Select All did not select all %d visible IDs" % amount)
			_check(selected == ui.get("_visible_release_ids"), "Select All selection differs from the filtered visible ID set")
			ui.call("_clear_release_selection")
			_check((ui.get("_selected_release_ids") as Array).is_empty(), "Clear did not empty the candidate selection")
		if amount == 15:
			var candidate_scroll := ui.get_node("ReleaseCandidateScroll") as ScrollContainer
			var vbar := candidate_scroll.get_v_scroll_bar()
			_check(vbar.max_value > vbar.page, "15-item gallery has no scrollable overflow")
		if amount == 150:
			var large_scroll := ui.get_node("ReleaseCandidateScroll") as ScrollContainer
			var large_vbar := large_scroll.get_v_scroll_bar()
			_check(large_vbar.max_value > large_vbar.page, "150-item gallery is not scrollable beyond the first visible candidates")
			large_scroll.scroll_vertical = large_vbar.max_value
			await process_frame
			_check(large_scroll.scroll_vertical > 0, "150-item gallery could not reach candidates below the first 15")

	var activity_events: Array = ui.get("_release_activity_events")
	var activity_count_before_tabs := activity_events.size()
	ui.call("_show_screen", "PIXEL ART")
	_check(not (ui.get_node("ReleaseCandidateScroll") as Control).visible, "Release candidates leaked into PIXEL ART")
	_check(not (ui.get_node("ReleasePoolActivityScroll") as Control).visible, "Release activity leaked into PIXEL ART")
	ui.call("_show_screen", "LEVEL FACTORY")
	_check(not (ui.get_node("ReleaseCandidateScroll") as Control).visible, "Release candidates leaked into LEVEL FACTORY")
	_check(not (ui.get_node("ReleasePoolActivityScroll") as Control).visible, "Release activity leaked into LEVEL FACTORY")
	ui.call("_show_screen", "RELEASE POOL")
	await process_frame
	_check((ui.get("_release_activity_events") as Array).size() >= activity_count_before_tabs, "Release session activity was lost while changing tabs")
	_check((ui.get_node("ReleaseCandidateScroll") as Control).visible, "Release candidate gallery did not return with Release Pool")

	ui.call("_show_screen", "LEVEL FACTORY")
	var source_id := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
	var release_root := ProjectSettings.globalize_path("res://").path_join("..").simplify_path().path_join("Release/ScrubBots Factory Studio")
	var source_path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % source_id)
	var source_sha := source_id.trim_prefix("owner-upload-")
	var record_sha := str(ui.call("_source_record_sha256_for_id", source_id))
	_check(FileAccess.file_exists(source_path), "read-only R07 source-bound batch fixture is unavailable")
	_check(record_sha.length() == 64, "canonical source-record SHA-256 could not be verified")
	ui.call("_upsert_imported_source", {"path": source_path, "source_id": source_id, "source_sha256": source_sha, "display_filename": "002_32x32px.png", "width": 32, "height": 32})
	var imported: Dictionary = (ui.get("_gameplay_sources") as Array)[0]
	_check(str(imported.get("source_record_sha256", "")) == record_sha, "verified owner source record SHA was not attached to the imported source")
	var follow_item := {
		"job_id": "r07-live-follow-fixture", "index": 0, "source_id": source_id,
		"source_sha256": source_sha, "source_record_sha256": record_sha,
		"attempt_id": "attempt-r07-live-001", "column_count": 4, "status": "RUNNING",
		"original_filename": "002_32x32px.png", "run_id": "",
	}
	var follow_snapshot := {
		"job_id": "r07-live-follow-fixture", "import_batch_id": "batch-r07-live-fixture",
		"state": "RUNNING", "current_index": 0, "items": [follow_item.duplicate(true)],
	}
	var composite := {"items": [{"source_id": source_id, "source_sha256": source_sha, "source_record_sha256": record_sha}]}
	ui.set("_batch_job_id", "r07-live-follow-fixture")
	ui.set("_batch_import_id", "batch-r07-live-fixture")
	ui.set("_batch_snapshot", follow_snapshot.duplicate(true))
	ui.set("_batch_composite_snapshot", composite)
	ui.set("_operation_running", true)
	ui.call("_sync_verified_batch_follow", follow_snapshot)
	_check(str(ui.get("_selected_import_source_id")) == source_id, "authenticated live batch item did not bind the selected source")
	_check(str(ui.get("_selected_art_path")) == source_path, "authenticated live batch item did not bind the preview art path")
	_check(str(ui.get("_activity_source_id")) == source_id, "authenticated live batch item did not bind Pipeline Activity")
	_check(int(ui.get("_imported_window_start")) == 0, "single-item batch follow moved the five-slot gallery incorrectly")
	var details: Array = ui.get("_details_rows")
	_check(details.size() >= 1 and (details[0] as Label).text.contains("Columns 4"), "Level Factory details did not follow the authenticated four-column item")
	var terminal_item := follow_item.duplicate(true)
	terminal_item["status"] = "FAILED"
	terminal_item["reason"] = "fixture terminal transition"
	var terminal_snapshot := follow_snapshot.duplicate(true)
	terminal_snapshot["state"] = "COMPLETE"
	terminal_snapshot["items"] = [terminal_item]
	ui.set("_batch_snapshot", terminal_snapshot.duplicate(true))
	ui.set("_operation_running", false)
	ui.call("_sync_verified_batch_follow", terminal_snapshot)
	_check(str(ui.get("_batch_follow_item").get("status", "")) == "FAILED", "terminal authenticated status transition was not followed")
	_check(str(ui.get("_activity_stage")) == "FAILED", "Pipeline Activity did not follow the terminal batch item state")

	var real_job_path := release_root.path_join("level_factory/output/studio-extensions/png-batches/jobs/png-batch-c898cfef80663a61e8246ea1e4da8e13.json")
	var real_job_variant: Variant = JSON.parse_string(FileAccess.get_file_as_string(real_job_path)) if FileAccess.file_exists(real_job_path) else null
	_check(real_job_variant is Dictionary and (real_job_variant as Dictionary).get("items", []).size() == 9, "read-only nine-source batch fixture is unavailable")
	if real_job_variant is Dictionary and (real_job_variant as Dictionary).get("items", []).size() == 9:
		var real_items: Array = (real_job_variant as Dictionary).get("items", [])
		var composite_items: Array[Dictionary] = []
		var fake_items: Array[Dictionary] = []
		for index in range(real_items.size()):
			var saved: Dictionary = real_items[index]
			var identity := str(saved.get("source_id", ""))
			var sha := str(saved.get("source_sha256", ""))
			var record_hash := str(saved.get("source_record_sha256", ""))
			var path := release_root.path_join("level_factory/output/owner-uploads/%s/source.png" % identity)
			_check(FileAccess.file_exists(path) and sha == identity.trim_prefix("owner-upload-"), "saved nine-source item %d has no matching read-only owner PNG" % index)
			_check(str(ui.call("_source_record_sha256_for_id", identity)) == record_hash, "saved nine-source item %d source-record hash is not current" % index)
			ui.call("_upsert_imported_source", {"path": path, "source_id": identity, "source_sha256": sha, "source_record_sha256": record_hash, "display_filename": str(saved.get("original_filename", "PNG")), "width": 32, "height": 32})
			composite_items.append({"source_id": identity, "source_sha256": sha, "source_record_sha256": record_hash})
			var fake := saved.duplicate(true)
			fake["job_id"] = "r07-nine-source-transition-fixture"
			fake["index"] = index
			fake["attempt_id"] = "r07-attempt-%03d" % index
			fake["status"] = "QUEUED"
			fake["run_id"] = ""
			fake_items.append(fake)
		var source_order := (ui.get("_gameplay_sources") as Array).duplicate(true)
		_check(source_order.size() == 9, "nine immutable PNG sources did not populate the five-slot gallery fixture")
		ui.set("_batch_job_id", "r07-nine-source-transition-fixture")
		ui.set("_batch_import_id", "batch-r07-nine-source-fixture")
		ui.set("_batch_composite_snapshot", {"items": composite_items})
		ui.set("_operation_running", true)
		for active_index in range(9):
			for item_index in range(fake_items.size()):
				fake_items[item_index]["status"] = "QUEUED"
				fake_items[item_index]["run_id"] = ""
			if active_index > 0:
				fake_items[active_index - 1]["status"] = "FAILED"
			fake_items[active_index]["status"] = "RUNNING"
			var live_snapshot := {"job_id": "r07-nine-source-transition-fixture", "import_batch_id": "batch-r07-nine-source-fixture", "state": "RUNNING", "current_index": active_index, "items": fake_items.duplicate(true)}
			ui.set("_batch_snapshot", live_snapshot.duplicate(true))
			ui.call("_sync_verified_batch_follow", live_snapshot)
			var active_id := str(fake_items[active_index].get("source_id", ""))
			var expected_start := clampi(active_index - 2, 0, 4)
			_check(str(ui.get("_selected_import_source_id")) == active_id, "nine-source transition %d did not select its active source" % active_index)
			_check(str(ui.get("_activity_source_id")) == active_id, "nine-source transition %d left Activity on another source" % active_index)
			_check(int(ui.get("_imported_window_start")) == expected_start, "nine-source transition %d did not center/clamp the five-card window" % active_index)
			var active_slot := active_index - expected_start
			var active_button := ui.get_node("LevelVariation%d" % (active_slot + 1)) as Button
			_check(active_button.text.contains("●"), "nine-source transition %d did not highlight the active thumbnail" % active_index)
			var tooltip_identity := active_button.tooltip_text.replace("\n", "").replace("\r", "")
			_check(tooltip_identity.contains(active_id), "nine-source transition %d thumbnail is bound to another source ID" % active_index)
			_check(str((ui.get("_preview_paths_by_screen") as Dictionary).get("LEVEL FACTORY", "")) == str((ui.get("_gameplay_sources") as Array)[active_index].get("path", "")), "nine-source transition %d preview is bound to another source" % active_index)
			_check(str((ui.get("_details_rows") as Array)[0].text).contains("Columns %d" % int(fake_items[active_index].get("column_count", 0))), "nine-source transition %d Details do not show the assigned columns" % active_index)
			_check(str(ui.get("_activity_stage")) == "RUNNING", "nine-source transition %d Activity does not show its live status" % active_index)
			if active_index == 4:
				var ready_item: Dictionary = fake_items[active_index].duplicate(true)
				ready_item["status"] = "READY"
				ready_item["run_id"] = "r07-authenticated-ready-run"
				ready_item["release_pool"] = {"disposition": "INCLUDED"}
				var ready_snapshot := live_snapshot.duplicate(true)
				ready_snapshot["items"] = fake_items.duplicate(true)
				ready_snapshot["items"][active_index] = ready_item
				ready_snapshot["current_index"] = active_index
				var ready_column_count := int(ready_item.get("column_count", 0))
				gateway.restored_run = {
					"state": "READY", "source_sha256": str(ready_item.get("source_sha256", "")),
					"run_id": "r07-authenticated-ready-run", "owner_review_status": {"pool_state": "INCLUDED"},
					"pipeline": {"run_id": "r07-authenticated-ready-run", "request": {"source_id": active_id, "column_count": ready_column_count},
						"primary": {"state": "SOLVED", "column_count": ready_column_count, "acceptance": {"replay": "WIN"}, "difficulty": {"class": "V1"}}},
				}
				ui.set("_batch_snapshot", ready_snapshot.duplicate(true))
				ui.call("_sync_verified_batch_follow", ready_snapshot)
				var ready_details: Array = ui.get("_details_rows")
				_check(str(ready_details[2].text).contains("SOLVED") and str(ready_details[2].text).contains("WIN"), "authenticated READY item did not bind solver and replay facts to its source")
				_check(str(ready_details[3].text).contains("V1") and str(ready_details[3].text).contains("INCLUDED"), "authenticated READY item did not bind Difficulty and Pool facts to its source")
			await process_frame
		ui.set("_operation_running", true)
		for item_index in range(fake_items.size()):
			fake_items[item_index]["status"] = "FAILED"
			fake_items[item_index]["reason"] = "fixture terminal status"
		var completed_snapshot := {"job_id": "r07-nine-source-transition-fixture", "import_batch_id": "batch-r07-nine-source-fixture", "state": "COMPLETE", "current_index": null, "items": fake_items.duplicate(true)}
		ui.set("_batch_snapshot", completed_snapshot.duplicate(true))
		ui.set("_operation_running", false)
		ui.call("_sync_verified_batch_follow", completed_snapshot)
		_check(str(ui.get("_selected_import_source_id")) == str(fake_items[8].get("source_id", "")), "completed nine-source job did not follow the most recently completed item")
		_check(int(ui.get("_imported_window_start")) == 4, "completed nine-source job did not clamp to the final five thumbnails")
		_check(str(ui.get("_activity_stage")) == "FAILED", "completed nine-source job displayed a fabricated READY state")

	ui.call("_show_screen", "RELEASE POOL")
	var help_buttons := ["ReleaseStagingHelp", "ReleaseProductionHelp", "PreflightReleaseHelp", "ValidateReleaseAssetsHelp", "BuildReleasePackHelp", "UploadR2StatusHelp", "UploadSelectedHelp", "PreviewReleaseManifestHelp"]
	for help_name in help_buttons:
		var help_button := ui.get_node(help_name) as Button
		_check(help_button.visible and help_button.text == "ⓘ", "%s help affordance is not visible beside its action" % help_name)
		help_button.emit_signal("pressed")
	ui.call("_set_release_target", "STAGING")
	ui.call("_show_publish_stage", "VALIDATE_ASSETS")
	ui.call("_show_publish_stage", "BUILD_SCRUBPACK")
	ui.call("_show_publish_stage", "UPLOAD_R2")
	ui.set("_release_pool", {"entries": [], "publish_preflight": {}})
	ui.call("_preview_release_manifest")
	_check(gateway.calls.all(func(call: Dictionary) -> bool: return str(call.get("operation", "")) != "scrubbots-publish"), "help, target, status or manifest-preview action called the publisher")
	_check(gateway.calls.all(func(call: Dictionary) -> bool: return str(call.get("operation", "")) not in ["pipeline", "png-batch-run", "png-batch-create", "solve", "replay", "load-check"]), "dashboard test dispatched solver, batch, replay or load-check work")
	_check((ui.get("_release_activity_events") as Array).any(func(event: Dictionary) -> bool: return str(event.get("state", "")).contains("STATUS ONLY")), "status-only action was not recorded in session activity")
	_check((ui.get("_release_activity_events") as Array).any(func(event: Dictionary) -> bool: return str(event.get("action", "")).contains("PREVIEW MANIFEST") and str(event.get("state", "")) == "BLOCKED"), "missing-preflight manifest preview was not blocked and logged")

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


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
