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
	_check(caption == "Running 5/8 · 2 parallel", "parallel run caption is wrong: %s" % caption)

	# Selecting a thumbnail by hand must also centre the window on that PNG.
	ui.set("_operation_running", false)
	ui.call("_select_imported_source_by_id", str(sources[10]["source_id"]))
	shown = _slot_texts(ui)
	_check(shown.any(func(text: String) -> bool: return text.contains("LF-000011") and text.contains("●")),
		"selected LF-000011 is not visible and marked in the five-slot gallery: %s" % [shown])

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


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
