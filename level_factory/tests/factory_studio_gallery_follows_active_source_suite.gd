extends SceneTree

## Owner report 2026-11-12: while a Pending batch runs, the bottom gallery did
## not show the active PNG. The gallery renders every Final PNG (1424) in
## filename order, but the five-slot window was positioned with the active
## item's index inside the Pending batch snapshot (1299 sources), so it stayed
## on LF-000001..005 while LF-000099 was being solved.

const PASS_MARKER := "Gallery follows active source PASS"

var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _png_source(number: int) -> Dictionary:
	var image := Image.create(32, 32, false, Image.FORMAT_RGBA8)
	image.fill(Color8(10 + number * 9, 200 - number * 7, 60 + number * 5))
	var png := image.save_png_to_buffer()
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(png)
	var sha := context.finish().hex_encode()
	var path := OS.get_temp_dir().path_join("sb-gallery-follow-%02d.png" % number)
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_buffer(png)
	file.close()
	return {"source_id": "owner-upload-" + sha, "source_sha256": sha, "source_record_sha256": "%064x" % (900 + number),
		"path": path, "display_filename": "LF-%06d.png" % number, "width": 32, "height": 32, "disposition": "IMPORTED"}


func _run_suite() -> void:
	var instance := (load("res://scenes/factory_studio.tscn") as PackedScene).instantiate()
	root.add_child(instance)
	await process_frame
	var ui := instance.get_node("MasterUI") as Control
	ui.set("_studio_read_queue", [])
	ui.set("_screen", "LEVEL FACTORY")
	var sources: Array[Dictionary] = []
	for number in range(1, 13):
		sources.append(_png_source(number))
	ui.set("_imported_sources", sources.duplicate(true))
	ui.call("_refresh_gameplay_sources")
	# LF-000001..000004 are already READY; the Pending batch holds LF-000005..000012.
	var pending: Array = sources.slice(4)
	var composite_items: Array = []
	var job_items: Array = []
	for index in range(pending.size()):
		var source: Dictionary = pending[index]
		composite_items.append({"source_id": source["source_id"], "source_sha256": source["source_sha256"], "source_record_sha256": source["source_record_sha256"]})
		job_items.append({"job_id": "job-gallery", "index": index, "source_id": source["source_id"], "source_sha256": source["source_sha256"],
			"source_record_sha256": source["source_record_sha256"], "attempt_id": "attempt-%02d" % index, "column_count": 3,
			"status": "READY" if index < 3 else "RUNNING" if index == 3 else "QUEUED", "run_id": "run-%02d" % index if index < 3 else "",
			"original_filename": source["display_filename"]})
	var job := {"job_id": "job-gallery", "import_batch_id": "batch-gallery", "state": "RUNNING", "current_index": 3, "items": job_items}
	ui.set("_batch_import_id", "batch-gallery")
	ui.set("_batch_composite_snapshot", {"batch_id": "batch-gallery", "items": composite_items})
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.set("_batch_job_id", "job-gallery")
	ui.set("_operation_running", true)

	# Active item: Pending index 3 = LF-000008 = gallery index 7.
	ui.call("_sync_verified_batch_follow", job)
	_check(str(ui.get("_selected_import_source_id")) == str(pending[3]["source_id"]), "batch follow did not select the active Pending source")
	var shown := _slot_texts(ui)
	_check(shown.any(func(text: String) -> bool: return text.contains("LF-000008") and text.contains("●")),
		"active LF-000008 is not visible and marked in the five-slot gallery: %s" % [shown])

	# Parallel workers (2026-11-12): two items RUNNING -> caption counts both.
	job_items[4]["status"] = "RUNNING"
	job["counts"] = {"total": 8, "ready": 3, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 5}
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.call("_refresh_run_button_caption")
	var caption := (ui.get_node("RunLevelPipeline") as Button).text
	_check(caption == "Running · 3/8 done · 2 parallel", "parallel run caption is wrong: %s" % caption)

	# Owner screen 2026-11-13: with parallel workers the job has no current_index.
	# The button said 61/1256, Details 56/1256, and the activity header stayed on
	# "Starting next verified PNG". One progress number everywhere, and the header
	# names the followed PNG.
	job["current_index"] = null
	ui.set("_batch_snapshot", job.duplicate(true))
	ui.set("_owner_release_archive_loaded", true)
	ui.call("_sync_verified_batch_follow", job)
	ui.call("_refresh_run_button_caption")
	ui.call("_refresh_activity_header")
	ui.call("_refresh_live_data")
	var activity_source := (ui.get("_activity_source_label") as Label).text
	var activity_phase := (ui.get("_activity_phase_label") as Label).text
	_check(not activity_source.contains("Starting next"), "activity header is stuck on 'Starting next' while PNGs run: %s" % activity_source)
	_check(activity_source.contains("LF-000008"), "activity header does not name the followed PNG: %s" % activity_source)
	_check(activity_phase.contains("3/8 done") and not activity_phase.contains(" P"), "activity progress is not the shared done count or repeats P/R/F/X: %s" % activity_phase)
	var details_texts: Array[String] = []
	for row in ui.get("_details_rows"):
		details_texts.append((row as Label).text)
	# A RUNNING PNG has no result yet: Preview Replay / Supply Plan must not open
	# a "Results unavailable" error panel.
	_check((ui.get_node("PreviewReplay") as Button).disabled and (ui.get_node("ExpandSupplyPlan") as Button).disabled,
		"Preview Replay / Supply Plan are clickable for a PNG without a READY result")
	_check(details_texts.any(func(text: String) -> bool: return text.contains("Batch 3/8 done")), "Details batch progress differs from the button: %s" % [details_texts])

	# Owner request 2026-11-13: Batch Issues lists the PNGs being solved first, in
	# filename order (LF-000008, LF-000009), without repeating their Pending row.
	var archive_records: Array = []
	for source in sources:
		archive_records.append({"source_id": source["source_id"], "source_sha256": source["source_sha256"], "provider": "PIXELLAB",
			"status": "PENDING", "original_source_path": "C:/final/" + str(source["display_filename"])})
	ui.set("_owner_release_archive", {"records": archive_records})
	ui.set("_batch_issue_filter", "ALL")
	ui.call("_refresh_batch_issue_panel")
	var issue_texts: Array[String] = []
	for child in (ui.get("_batch_issue_rows") as Node).get_children():
		if child is Button and not child.is_queued_for_deletion():
			issue_texts.append((child as Button).text)
	_check(issue_texts.size() >= 2 and issue_texts[0].begins_with("RUNNING · LF-000008") and issue_texts[1].begins_with("RUNNING · LF-000009"),
		"running PNGs are not listed first in filename order: %s" % [issue_texts.slice(0, 3)])
	_check(issue_texts.filter(func(text: String) -> bool: return text.contains("LF-000008")).size() == 1, "running PNG is listed twice")
	# A PNG that just finished must not show its stale Pending archive row while the
	# Release Pool re-read is still on its way.
	var finished_names: Array[String] = []
	for batch_item in (ui.get("_batch_snapshot") as Dictionary).get("items", []):
		if str(batch_item.get("status", "")) == "READY":
			finished_names.append(str(batch_item.get("original_filename", "")).get_basename())
	_check(not finished_names.is_empty(), "fixture has no READY batch item")
	for finished_name in finished_names:
		_check(issue_texts.any(func(text: String) -> bool: return text.begins_with("READY · " + finished_name)),
			"%s finished READY but Batch Issues still shows: %s" % [finished_name, issue_texts.filter(func(text: String) -> bool: return text.contains(finished_name))])

	# Selecting a thumbnail by hand must also centre the window on that PNG.
	ui.set("_operation_running", false)
	ui.call("_select_imported_source_by_id", str(sources[10]["source_id"]))
	shown = _slot_texts(ui)
	_check(shown.any(func(text: String) -> bool: return text.contains("LF-000011") and text.contains("●")),
		"selected LF-000011 is not visible and marked in the five-slot gallery: %s" % [shown])

	# 2026-11-13: a Release Pool retry job the gallery cannot re-derive stayed
	# "Running 2/6 · QUEUED" because progress results were rejected. A job this
	# session dispatched and is running must be followed.
	var retry_items: Array = []
	for index in range(3):
		retry_items.append({"index": index, "source_id": "owner-upload-%064x" % (700 + index), "source_sha256": "%064x" % (700 + index),
			"source_record_sha256": "%064x" % (800 + index), "status": "QUEUED", "column_count": 3})
	var retry_job := {"job_id": "job-retry", "import_batch_id": "batch-retry", "state": "RUNNING", "current_index": null, "items": retry_items,
		"counts": {"total": 3, "ready": 0, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 3}}
	ui.set("_batch_job_id", "job-retry")
	ui.set("_batch_import_id", "batch-retry")
	ui.set("_batch_composite_snapshot", {"batch_id": "batch-retry", "items": retry_items})
	ui.set("_batch_snapshot", retry_job.duplicate(true))
	ui.set("_batch_job_source_mismatch", false)
	ui.set("_operation_running", true)
	ui.set("_batch_worker_active", true)
	var progressed := retry_job.duplicate(true)
	for item in progressed["items"]:
		item["status"] = "RUNNING"
	progressed["current_index"] = 0
	ui.call("_apply_batch_progress_result", {"disposition": "MATCHED", "job": progressed}, "job-retry")
	ui.call("_refresh_run_button_caption")
	var retry_caption := (ui.get_node("RunLevelPipeline") as Button).text
	_check(retry_caption == "Running · 0/3 done · 3 parallel", "dispatched retry progress was not followed: %s" % retry_caption)
	_check(not bool(ui.get("_batch_job_source_mismatch")), "dispatched retry progress was treated as a lineage mismatch")

	# 2026-11-13: the status counter showed 180 R / 2 F while the Release Pool held
	# 208 READY / 6 FAILED, and Batch Issues kept READY PNGs as "PENDING", because
	# the Release Pool was re-read only when the whole batch ended. A PNG that
	# finishes during the batch must trigger a re-read.
	ui.set("_owner_release_archive", {"records": []})
	ui.set("_owner_release_archive_loaded", true)
	ui.get("_studio_read_queue").clear()
	ui.set("_studio_read_context", {})
	var finished := progressed.duplicate(true)
	finished["items"][0]["status"] = "READY"
	finished["counts"] = {"total": 3, "ready": 1, "failed": 0, "rejected": 0, "skipped": 0, "remaining": 2}
	ui.call("_apply_batch_progress_result", {"disposition": "MATCHED", "job": finished}, "job-retry")
	_check(_release_archive_read_requested(ui), "a PNG finished during the batch but the Release Pool was not re-read")
	ui.get("_studio_read_queue").clear()
	ui.set("_studio_read_context", {})
	ui.call("_apply_batch_progress_result", {"disposition": "MATCHED", "job": finished.duplicate(true)}, "job-retry")
	_check(not _release_archive_read_requested(ui), "Release Pool was re-read although no PNG finished")
	ui.get("_studio_read_queue").clear()
	ui.set("_studio_read_context", {})
	ui.set("_operation_running", false)
	ui.set("_batch_worker_active", false)

	# Owner layout 2026-11-13: live Release status counter under Run Pipeline,
	# only on LEVEL FACTORY; the P/R/F/X totals left the Details batch row.
	ui.set("_owner_release_archive", {"records": [
		{"source_id": str(sources[0]["source_id"]), "source_sha256": str(sources[0]["source_sha256"]), "status": "READY"},
		{"source_id": str(sources[1]["source_id"]), "source_sha256": str(sources[1]["source_sha256"]), "status": "FAILED"},
		{"source_id": str(sources[2]["source_id"]), "source_sha256": str(sources[2]["source_sha256"]), "status": "PENDING"}]})
	ui.set("_owner_release_archive_loaded", true)
	ui.call("_show_screen", "LEVEL FACTORY")
	ui.call("_refresh_run_button_caption")
	var counter := ui.get_node("ReleaseStatusCounter") as Label
	var run_button := ui.get_node("RunLevelPipeline") as Control
	_check(counter.visible and RegEx.create_from_string("^\\d+ P / \\d+ R / \\d+ F / \\d+ X$").search(counter.text) != null,
		"status counter is missing or malformed: visible=%s text=%s" % [counter.visible, counter.text])
	_check(counter.position.y > run_button.position.y + run_button.size.y, "status counter is not under Run Pipeline")
	# Owner screen 2026-11-13: the Studio opens on PIXEL ART, where these buttons
	# are hidden, so Batch Issues kept its unscaled default top. Opening LEVEL
	# FACTORY on a large window put Retry/Accept/Reject over its heading and tabs.
	ui.call("_show_screen", "PIXEL ART")
	ui.size = Vector2(1920, 1130)
	ui.call("_apply_responsive_layout")
	ui.call("_show_screen", "LEVEL FACTORY")
	var issues_top := (ui.get_node("RuntimeDetailsPanel/BatchIssuesPanel") as Control).get_global_rect().position.y
	for name in ["SolveAgain", "AcceptLevel", "RejectLevel"]:
		var rect := (ui.get_node(name) as Control).get_global_rect()
		_check(issues_top >= rect.end.y, "%s overlaps Batch Issues: button bottom %.0f, panel top %.0f" % [name, rect.end.y, issues_top])
	ui.call("_show_screen", "PIXEL ART")
	_check(not counter.visible, "status counter leaked onto PIXEL ART")

	instance.free()
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for message in _errors:
		push_error(message)
	quit(1)


func _slot_texts(ui: Control) -> Array[String]:
	var texts: Array[String] = []
	for index in range(5):
		texts.append((ui.get_node("LevelVariation%d" % (index + 1)) as Button).text)
	return texts


func _release_archive_read_requested(ui: Control) -> bool:
	var contexts: Array = [ui.get("_studio_read_context")]
	for queued in ui.get("_studio_read_queue"):
		contexts.append(queued.get("context", {}))
	return contexts.any(func(context: Variant) -> bool: return context is Dictionary and str(context.get("kind", "")) == "owner-release-library")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
