extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R08 tall dock and batch status PASS"
const FIXTURE_DIR := "res://tests/fixtures/factory_studio_r04_r01"
const FIXTURE_NAMES := [
	"import_01_20x20.png", "import_02_20x59.png", "import_03_32x32.png",
	"import_04_59x20.png", "import_05_20x20.png", "import_06_20x20.png",
	"import_07_20x20.png", "import_08_20x20.png", "import_09_20x20.png",
]

class ReadOnlyGateway extends RefCounted:
	var calls: Array[Dictionary] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append({"operation": operation, "request": request.duplicate(true)})
		if operation == "candidate-inbox":
			return {"state": "READY", "candidates": []}
		if operation == "release-pool":
			return {"state": "READY", "entries": [], "pool_size": 0}
		if operation == "restore-source-run-readonly":
			return {}
		return {"state": "UNAVAILABLE", "reason": "R08 status suite uses a read-only fake gateway."}


var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var viewport := SubViewport.new()
	viewport.name = "R08TallDockStatusViewport"
	viewport.size = Vector2i(1536, 960)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ui := Control.new()
	ui.name = "FactoryStudioR08TallDockStatus"
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
	ui.call("configure_gateway", gateway)
	ui.call("_show_screen", "LEVEL FACTORY")
	var imported: Array[Dictionary] = []
	var composite_items: Array[Dictionary] = []
	var items: Array[Dictionary] = []
	for index in range(9):
		var fixture_name: String = FIXTURE_NAMES[index]
		var fixture_path := ProjectSettings.globalize_path("%s/%s" % [FIXTURE_DIR, fixture_name])
		var source_sha := str(ui.call("_source_png_sha256", fixture_path))
		var source_id := "owner-upload-" + source_sha
		var record_sha := "%064x" % (index + 800)
		var display_name := "%03d_32x32px.png" % (index + 2)
		imported.append({
			"source_id": source_id, "source_sha256": source_sha,
			"source_record_sha256": record_sha, "path": fixture_path,
			"display_filename": display_name, "width": 32, "height": 32,
			"disposition": "IMPORTED",
		})
		composite_items.append({
			"source_id": source_id, "source_sha256": source_sha,
			"source_record_sha256": record_sha,
		})
		items.append({
			"job_id": "r08-nine-source-mock", "index": index,
			"source_id": source_id, "source_sha256": source_sha,
			"source_record_sha256": record_sha,
			"attempt_id": "r08-attempt-%03d" % index,
			"column_count": 3 + (index % 3), "status": "QUEUED",
			"original_filename": display_name, "run_id": "", "reason": "",
		})
	ui.set("_imported_sources", imported)
	ui.set("_batch_job_id", "r08-nine-source-mock")
	ui.set("_batch_import_id", "r08-nine-import-mock")
	ui.set("_batch_composite_snapshot", {"items": composite_items})
	ui.set("_batch_job_source_mismatch", false)
	ui.set("_operation_running", true)
	ui.call("_refresh_gameplay_sources")

	var active_items := items.duplicate(true)
	active_items[4]["status"] = "RUNNING"
	var running_snapshot := {
		"job_id": "r08-nine-source-mock", "import_batch_id": "r08-nine-import-mock",
		"state": "RUNNING", "current_index": 4, "items": active_items,
	}
	ui.set("_batch_snapshot", running_snapshot.duplicate(true))
	ui.call("_sync_verified_batch_follow", running_snapshot)
	ui.call("_refresh_runtime_cards")
	var active_card := ui.get_node("LevelVariation3") as Button
	_check(str(ui.get("_selected_import_source_id")) == str(active_items[4].get("source_id", "")), "active item 006 did not bind selected source")
	_check(str(ui.get("_activity_source_id")) == str(active_items[4].get("source_id", "")), "active item 006 did not bind Pipeline Activity")
	_check(active_card.text.contains("006") and active_card.text.contains("RUNNING") and active_card.text.contains("4 COL"), "active 006 card does not show its current RUNNING status and assigned columns")
	_check(active_card.text.contains("●"), "active 006 card is not visibly selected")
	var expected_ids := [str(active_items[2].get("source_id", "")), str(active_items[3].get("source_id", "")), str(active_items[4].get("source_id", "")), str(active_items[5].get("source_id", "")), str(active_items[6].get("source_id", ""))]
	for slot in range(5):
		var card := ui.get_node("LevelVariation%d" % (slot + 1)) as Button
		var tooltip_identity := card.tooltip_text.replace("\n", "").replace("\r", "")
		_check(tooltip_identity.contains(expected_ids[slot]), "active 006 five-slot window has the wrong source in slot %d" % (slot + 1))
	var details: Array = ui.get("_details_rows")
	_check(str(details[0].text).contains("Columns 4") and str(details[4].text).contains("006_32x32px.png"), "active 006 Details do not match its preview/card source")

	# Old READY evidence for 002 must not override this authenticated job's QUEUED item.
	ui.set("_last_pipeline", {"source_id": str(active_items[0].get("source_id", "")), "disposition": "READY", "primary": {"column_count": 3}})
	ui.call("_refresh_runtime_cards")
	var first_card := ui.get_node("LevelVariation1") as Button
	_check(first_card.text.contains("QUEUED") and first_card.text.contains("5 COL"), "old READY history overrode the current queued item and assigned columns")

	var failed_items := active_items.duplicate(true)
	failed_items[2]["status"] = "FAILED"
	failed_items[2]["reason"] = "fixture failure reason"
	var failed_snapshot := running_snapshot.duplicate(true)
	failed_snapshot["items"] = failed_items
	ui.set("_batch_snapshot", failed_snapshot.duplicate(true))
	ui.call("_refresh_runtime_cards")
	var failed_card := ui.get_node("LevelVariation1") as Button
	# The active window starts at item 2; source 004 occupies its first card.
	_check((ui.get_node("LevelVariation1") as Button).text.contains("FAILED"), "failed source card did not show FAILED")
	_check(failed_card.tooltip_text.contains("fixture failure reason"), "failed source reason is not available from its thumbnail tooltip")

	var reused_items := active_items.duplicate(true)
	reused_items[1]["status"] = "READY"
	reused_items[1].erase("attempt_id")
	reused_items[1]["run_id"] = "r08-existing-ready-run"
	reused_items[1]["reused_existing_ready"] = true
	var reused_snapshot := running_snapshot.duplicate(true)
	reused_snapshot["items"] = reused_items
	reused_snapshot["current_index"] = 1
	ui.set("_batch_snapshot", reused_snapshot.duplicate(true))
	ui.call("_sync_verified_batch_follow", reused_snapshot)
	ui.call("_refresh_runtime_cards")
	var reused_card := ui.get_node("LevelVariation2") as Button
	_check(reused_card.text.contains("READY · REUSED PROOF") and reused_card.text.contains("4 COL"), "authenticated reused READY item was not explicitly distinguished")
	_check(str(ui.get("_selected_import_source_id")) == str(reused_items[1].get("source_id", "")), "reused READY item with no new attempt was not followed")

	var retry_items: Array[Dictionary] = []
	for retry_index in range(2):
		var source_index := 8 if retry_index == 0 else 2
		var retry_item: Dictionary = items[source_index].duplicate(true)
		retry_item["job_id"] = "r08-subset-retry"
		retry_item["index"] = retry_index
		retry_item["status"] = "RUNNING" if retry_index == 0 else "QUEUED"
		retry_item["attempt_id"] = "r08-retry-attempt-%d" % retry_index
		retry_items.append(retry_item)
	var retry_snapshot := {
		"job_id": "r08-subset-retry", "parent_job_id": "r08-nine-source-mock",
		"lineage_verified": true, "import_batch_id": "r08-nine-import-mock",
		"state": "RUNNING", "current_index": 0, "items": retry_items,
	}
	ui.set("_batch_job_id", "r08-subset-retry")
	ui.set("_batch_snapshot", retry_snapshot.duplicate(true))
	ui.call("_sync_verified_batch_follow", retry_snapshot)
	ui.call("_refresh_runtime_cards")
	_check(int(ui.get("_imported_window_start")) == 4, "subset retry used its job index instead of the active gallery source index")
	_check((ui.get_node("LevelVariation5") as Button).text.contains("RUNNING"), "subset retry active source did not occupy the correctly clamped fifth slot")

	var invalid_items := retry_items.duplicate(true)
	invalid_items[0]["source_record_sha256"] = "%064x" % 999999
	var invalid_snapshot := retry_snapshot.duplicate(true)
	invalid_snapshot["items"] = invalid_items
	ui.set("_batch_snapshot", invalid_snapshot.duplicate(true))
	ui.call("_refresh_runtime_cards")
	_check((ui.get_node("LevelVariation5") as Button).text.contains("UNVERIFIED"), "record-hash mismatch still appears as a verified live status")

	var interrupted_items := retry_items.duplicate(true)
	var interrupted_snapshot := retry_snapshot.duplicate(true)
	interrupted_snapshot["state"] = "INTERRUPTED"
	interrupted_snapshot["items"] = interrupted_items
	ui.set("_batch_snapshot", interrupted_snapshot.duplicate(true))
	ui.set("_operation_running", false)
	ui.call("_refresh_runtime_cards")
	_check((ui.get_node("LevelVariation5") as Button).text.contains("INTERRUPTED"), "restored interrupted RUNNING item is still shown as active")
	interrupted_snapshot["state"] = "PAUSED"
	ui.set("_batch_snapshot", interrupted_snapshot.duplicate(true))
	ui.call("_refresh_runtime_cards")
	_check((ui.get_node("LevelVariation5") as Button).text.contains("PAUSED"), "paused active item card does not show PAUSED")
	_check(gateway.calls.all(func(call: Dictionary) -> bool: return str(call.get("operation", "")) not in ["pipeline", "png-batch-run", "png-batch-create", "solve", "replay", "load-check"]), "batch status preview dispatched a solver, replay, load-check or batch run")

	# Tall dock geometry and aspect-preserving image fit at requested client sizes.
	ui.call("_show_screen", "LEVEL FACTORY")
	var portrait_path := ProjectSettings.globalize_path("%s/import_02_20x59.png" % FIXTURE_DIR)
	ui.call("_load_selected_art_preview", portrait_path, "LEVEL FACTORY")
	var sizes: Array[Vector2i] = [Vector2i(1536, 864), Vector2i(1536, 960), Vector2i(1536, 1024), Vector2i(1920, 1080), Vector2i(1100, 720), Vector2i(1536, 864)]
	for client in sizes:
		viewport.size = client
		ui.size = Vector2(client)
		ui.call("_apply_responsive_layout")
		await process_frame
		var dock := ui.get_node("RuntimeBottomStrip") as Control
		var host := ui.get_node("VisualReviewClip") as Control
		var original_scale_y := float(ui.call("responsive_geometry", Vector2(client)).get("scale_y", 1.0))
		_check(dock.size.y > 106.0 * original_scale_y + 20.0, "Level Factory dock did not grow at %s" % client)
		_check(host.size.y < float(client.y) - 184.0 * original_scale_y, "Level Factory preview host did not shrink with its taller dock at %s" % client)
		_check(host.get_global_rect().end.y <= dock.get_global_rect().position.y + 0.5, "preview host overlaps the taller dock at %s" % client)
		var image_rect := ui.get_node("VisualReviewClip/VisualReviewContent/SelectedArtworkPreview") as TextureRect
		_check(image_rect.texture != null and image_rect.visible, "portrait preview texture is absent after resize at %s" % client)
		_check(image_rect.get_global_rect().position.x >= host.get_global_rect().position.x - 0.5 and image_rect.get_global_rect().position.y >= host.get_global_rect().position.y - 0.5 and image_rect.get_global_rect().end.x <= host.get_global_rect().end.x + 0.5 and image_rect.get_global_rect().end.y <= host.get_global_rect().end.y + 0.5, "displayed portrait image escapes the preview host at %s" % client)
		_check(absf(image_rect.size.x / image_rect.size.y - 20.0 / 59.0) < 0.01, "portrait preview was distorted at %s" % client)
		_check(image_rect.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "preview lost nearest-neighbor filtering")
		for card_index in range(5):
			var card := (ui.get_node("LevelVariation%d" % (card_index + 1)) as Control).get_global_rect()
			_check(card.position.x >= dock.get_global_rect().position.x and card.position.y >= dock.get_global_rect().position.y and card.end.x <= dock.get_global_rect().end.x and card.end.y <= dock.get_global_rect().end.y, "Level Factory card %d escapes its tall dock at %s" % [card_index + 1, client])
			if card_index < 4:
				var next_card := (ui.get_node("LevelVariation%d" % (card_index + 2)) as Control).get_global_rect()
				_check(card.end.x + 1.0 <= next_card.position.x, "Level Factory cards lack separate click targets at %s" % client)

	ui.call("_show_screen", "RELEASE POOL")
	viewport.size = Vector2i(1536, 960)
	ui.size = Vector2(1536, 960)
	ui.call("_apply_responsive_layout")
	await process_frame
	var release_scale_y := float(ui.call("responsive_geometry", Vector2(1536, 960)).get("scale_y", 1.0))
	_check(is_equal_approx((ui.get_node("RuntimeBottomStrip") as Control).size.y, 106.0 * release_scale_y), "Release Pool dock changed with the Level Factory-only geometry")
	var release_entries: Array[Dictionary] = []
	for index in range(15):
		release_entries.append({
			"candidate_id": "r08-candidate-%03d" % index,
			"level_id": "R08 candidate %03d" % index,
			"pipeline": {"primary": {"disposition": "READY", "column_count": 3 + (index % 3)}},
			"pipeline_run_id": "r08-mock-run-%03d" % index,
			"pipeline_sha256": "%064x" % (index + 101),
			"entry_digest": "%064x" % (index + 201),
		})
	ui.set("_release_pool", {"state": "READY", "entries": release_entries, "pool_size": release_entries.size()})
	ui.call("_apply_release_projection")
	var release_scroll := ui.get_node("ReleaseCandidateScroll") as ScrollContainer
	var release_rows := ui.get_node("ReleaseCandidateScroll/ReleaseCandidateRows") as VBoxContainer
	_check(release_rows.get_child_count() == 15, "Release Pool no longer renders all fifteen candidate rows")
	viewport.size = Vector2i(1920, 1080)
	ui.size = Vector2(1920, 1080)
	ui.call("_apply_responsive_layout")
	await process_frame
	var visible_rows := floori(release_scroll.size.y / (float(ui.get("_release_candidate_row_height")) + 3.0))
	_check(visible_rows >= 14 and visible_rows <= 15, "Release Pool visible candidate row count is %d at 1920x1080" % visible_rows)
	for help_name in ["ReleaseStagingHelp", "ReleaseProductionHelp", "PreflightReleaseHelp", "ValidateReleaseAssetsHelp", "BuildReleasePackHelp", "UploadR2StatusHelp", "UploadSelectedHelp", "PreviewReleaseManifestHelp"]:
		var help_button := ui.get_node(help_name) as Button
		_check(help_button.visible and help_button.text == "ⓘ", "%s regressed while Level Factory geometry changed" % help_name)
	for dock_name in ["SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "AddMoreLevels"]:
		var release_item := (ui.get_node(dock_name) as Control).get_global_rect()
		_check(release_item.position.y >= (ui.get_node("RuntimeBottomStrip") as Control).get_global_rect().position.y and release_item.end.y <= (ui.get_node("RuntimeBottomStrip") as Control).get_global_rect().end.y, "%s moved outside the Release Pool bottom dock" % dock_name)
	ui.call("_append_release_pool_activity", "R08 test", "STATUS ONLY", "Mock activity retention check")
	var activity_count := (ui.get("_release_activity_events") as Array).size()
	ui.call("_show_screen", "LEVEL FACTORY")
	ui.call("_show_screen", "RELEASE POOL")
	_check((ui.get("_release_activity_events") as Array).size() == activity_count, "Release Pool session activity changed during tab navigation")
	ui.call("_show_screen", "PIXEL ART")
	viewport.size = Vector2i(1536, 960)
	ui.size = Vector2(1536, 960)
	ui.call("_apply_responsive_layout")
	await process_frame
	_check(is_equal_approx((ui.get_node("RuntimeBottomStrip") as Control).size.y, 106.0 * release_scale_y), "Pixel Art dock changed with the Level Factory-only geometry")

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
