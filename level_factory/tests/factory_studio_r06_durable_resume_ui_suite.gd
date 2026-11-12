extends SceneTree

## R06 durable resume, rewritten 2026-11-12 for the current startup flow.
##
## After the Release Pool statuses and the PixelLab Final inventory load, the
## Studio looks up the saved batch for the current Pending sources through the
## background reader ("loaded-png-batch-find" then "png-batch-latest"). It must
## only read: a persisted RUNNING job is shown as INTERRUPTED, PAUSED stays
## PAUSED, and nothing runs until the owner presses Resume Batch, which resumes
## the same durable job. A retry child is accepted only with verified lineage.

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R06 durable resume UI PASS"

var _errors: Array[String] = []


class ReadonlyJobGateway extends RefCounted:
	var reads: Array[String] = []
	var workers: Array[String] = []
	var sync_calls: Array[String] = []
	var composite: Dictionary
	var job: Dictionary
	var resolution := "MATCHED"

	func run_studio_extension(operation: String, _request: Dictionary) -> Dictionary:
		sync_calls.append(operation)
		return {"state": "UNAVAILABLE", "reason": "No synchronous gateway operation is configured in this fixture."}

	func prepare_studio_extension_call(operation: String, _request: Dictionary) -> Dictionary:
		if operation in ["loaded-png-batch-find", "png-batch-latest"]:
			reads.append(operation)
			return {"operation": operation}
		workers.append(operation)
		return {}  # a worker request is recorded but never started

	func execute_prepared_studio_extension_call(prepared: Dictionary) -> Dictionary:
		var operation := str(prepared.get("operation", ""))
		if operation == "loaded-png-batch-find":
			return {"state": "SUCCESS", "disposition": resolution, "batch": composite.duplicate(true), "mutated": false}
		if operation == "png-batch-latest":
			return {"state": "SUCCESS", "disposition": "MATCHED", "job": job.duplicate(true), "mutated": false}
		push_error("resume fixture must never execute a solver worker")
		return {}


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var ids: Array[String] = []
	var composite_items: Array[Dictionary] = []
	for index in range(9):
		var sha := "%064x" % (index + 1)
		ids.append("owner-upload-" + sha)
		composite_items.append({"index": index, "source_id": "owner-upload-" + sha, "source_sha256": sha,
			"source_record_sha256": "%064x" % (index + 100), "disposition": "ALREADY_IMPORTED"})
	var composite := {"batch_id": "batch-pending-fixture", "items": composite_items, "snapshot_digest": "%064x" % 777}

	# 1. A persisted RUNNING job is shown as INTERRUPTED and needs an explicit resume.
	var running := await _restore(ids, composite, _job(composite, ids, "RUNNING", []))
	var running_ui: Control = running["ui"]
	var running_gateway: ReadonlyJobGateway = running["gateway"]
	_check(str(running_ui.get("_batch_job_id")) == "png-batch-fixture", "startup restore did not rebind the exact persisted job")
	_check(str(running_ui.get("_batch_snapshot").get("state", "")) == "INTERRUPTED", "persisted RUNNING state did not display as interrupted")
	_check((running_ui.get_node("RunLevelPipeline") as Button).text.begins_with("Resume Batch"),
		"interrupted job did not expose explicit Resume Batch: %s" % (running_ui.get_node("RunLevelPipeline") as Button).text)
	_check(running_ui.get("_gameplay_sources").size() == 9, "a loaded thumbnail source was lost during job association")
	_check(running_gateway.reads == ["loaded-png-batch-find", "png-batch-latest"],
		"startup did not use exactly the read-only composite/job lookups: %s" % [running_gateway.reads])
	_check(running_gateway.workers.is_empty() and running_gateway.sync_calls.is_empty(),
		"startup prepared a worker or a synchronous call without an owner click: %s %s" % [running_gateway.workers, running_gateway.sync_calls])
	running_ui.call("_run_png_batch")
	_check(running_gateway.workers == ["png-batch-run"], "explicit Resume Batch did not dispatch the same persisted job: %s" % [running_gateway.workers])
	_check(not running_gateway.sync_calls.has("pending-png-batch-create") and not running_gateway.sync_calls.has("png-batch-create"),
		"resume created a new snapshot or plan instead of reusing the saved job")
	running_ui.free()

	# 2. PAUSED is restored truthfully and still needs an explicit click.
	var paused := await _restore(ids, composite, _job(composite, ids, "PAUSED", []))
	var paused_ui: Control = paused["ui"]
	_check(str(paused_ui.get("_batch_snapshot").get("state", "")) == "PAUSED", "PAUSED state was not restored truthfully")
	_check((paused_ui.get_node("RunLevelPipeline") as Button).text.begins_with("Resume Batch"), "PAUSED job did not require an explicit resume click")
	_check((paused["gateway"] as ReadonlyJobGateway).workers.is_empty(), "PAUSED restore started a worker")
	paused_ui.free()

	# 3. A verified retry child over a subset is accepted; tampered lineage is not.
	var retry_items: Array[Dictionary] = []
	for index in [1, 7]:
		var source: Dictionary = composite_items[index]
		retry_items.append({"index": retry_items.size(), "prior_item_index": index, "source_id": source["source_id"],
			"source_sha256": source["source_sha256"], "source_record_sha256": source["source_record_sha256"],
			"column_count": 3 + (index % 3), "status": "FAILED"})
	var retry := _job(composite, ids, "COMPLETE", retry_items)
	retry["parent_job_id"] = "png-batch-parent"
	retry["lineage_verified"] = true
	retry["counts"] = {"total": 2, "ready": 0, "failed": 2, "rejected": 0, "skipped": 0, "remaining": 0}
	var verified := await _restore(ids, composite, retry)
	var verified_ui: Control = verified["ui"]
	_check(bool(verified_ui.call("_batch_job_matches_loaded_sources")), "verified subset retry was rejected only because its item count is below nine")
	verified_ui.set("_batch_snapshot", _with_lineage(retry, false))
	_check(not bool(verified_ui.call("_batch_job_matches_loaded_sources")), "tampered retry ancestry was accepted by the UI authority guard")
	verified_ui.free()

	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for message in _errors:
		push_error(message)
	quit(1)


func _with_lineage(job: Dictionary, verified: bool) -> Dictionary:
	var copy := job.duplicate(true)
	copy["lineage_verified"] = verified
	return copy


## Builds a Studio whose startup reads have loaded (Pending records for every
## source), then lets the real background reader resolve the saved batch.
func _restore(ids: Array[String], composite: Dictionary, job: Dictionary) -> Dictionary:
	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	root.add_child(ui)
	var button := Button.new()  # the bare controller does not build the master controls
	button.name = "RunLevelPipeline"
	ui.add_child(button)
	var gateway := ReadonlyJobGateway.new()
	gateway.composite = composite.duplicate(true)
	gateway.job = job.duplicate(true)
	ui.set("_studio_read_queue", [])
	ui.set("_gateway", gateway)
	ui.set("_screen", "LEVEL FACTORY")
	var sources: Array[Dictionary] = []
	var records: Array = []
	for index in range(ids.size()):
		var sha := ids[index].trim_prefix("owner-upload-")
		sources.append({"source_id": ids[index], "source_sha256": sha, "source_record_sha256": "%064x" % (index + 100),
			"display_filename": "LF-%06d.png" % (index + 1), "width": 56, "height": 56})
		records.append({"source_id": ids[index], "source_sha256": sha, "status": "PENDING"})
	ui.set("_gameplay_sources", sources)
	ui.set("_selected_import_source_id", ids[0])
	ui.set("_owner_release_archive", {"schema": "scrubbots-owner-release-library-view/v1", "records": records})
	ui.set("_owner_release_archive_loaded", true)
	ui.set("_startup_source_inventory_loaded", true)
	ui.set("_startup_pending_batch_restore_started", false)
	ui.set("_operation_running", false)
	ui.call("_restore_loaded_png_batch_readonly")
	for _frame in range(600):
		if not bool(ui.get("_batch_restore_pending")):
			break
		await process_frame
	_check(not bool(ui.get("_batch_restore_pending")), "saved batch lookup did not finish")
	return {"ui": ui, "gateway": gateway}


func _job(composite: Dictionary, ids: Array[String], state: String, items: Array[Dictionary]) -> Dictionary:
	var rows := items
	if rows.is_empty():
		var source_rows: Array = composite["items"]
		for index in range(ids.size()):
			var source: Dictionary = source_rows[index]
			rows.append({"index": index, "source_id": ids[index], "source_sha256": source["source_sha256"],
				"source_record_sha256": source["source_record_sha256"], "column_count": [3, 4, 3, 4, 3, 4, 3, 4, 5][index], "status": "QUEUED"})
	return {"job_id": "png-batch-fixture", "import_batch_id": composite["batch_id"],
		"batch_digest": "%064x" % 888, "lineage_verified": true, "snapshot_source_count": 9,
		"state": state, "counts": {"total": rows.size(), "ready": 0, "failed": 0, "rejected": 0, "skipped": 0, "remaining": rows.size()},
		"items": rows}


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
