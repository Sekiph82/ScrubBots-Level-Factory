extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R06 durable resume UI PASS"

var _errors: Array[String] = []


class ReadonlyJobGateway extends RefCounted:
	var calls: Array[String] = []
	var prepared_calls := 0
	var composite: Dictionary
	var job: Dictionary
	var resolution := "MATCHED"

	func run_studio_extension(operation: String, _request: Dictionary) -> Dictionary:
		calls.append(operation)
		if operation == "loaded-png-batch-find":
			return {"state": "SUCCESS", "disposition": resolution, "batch": composite, "mutated": false}
		if operation == "png-batch-latest":
			return {"state": "SUCCESS", "disposition": "MATCHED", "job": job.duplicate(true), "mutated": false}
		return {"state": "UNAVAILABLE", "reason": "No mutating gateway operation is configured in this fixture."}

	func prepare_studio_extension_call(_operation: String, _request: Dictionary) -> Dictionary:
		prepared_calls += 1
		return {}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		push_error("resume fixture must never execute a solver worker")
		return {}


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var ids: Array[String] = []
	var composite_items: Array[Dictionary] = []
	for index in range(9):
		var sha := "%064x" % (index + 1)
		var source_id := "owner-upload-" + sha
		ids.append(source_id)
		composite_items.append({"index": index, "source_id": source_id, "source_sha256": sha,
			"source_record_sha256": "%064x" % (index + 100), "disposition": "ALREADY_IMPORTED"})
	var composite := {"batch_id": "batch-loaded-fixture", "items": composite_items, "snapshot_digest": "%064x" % 777}

	var running := _build_ui(ids, composite, _job(composite, ids, "RUNNING", []))
	var running_gateway: ReadonlyJobGateway = running["gateway"]
	var running_ui: Control = running["ui"]
	running_ui.call("_restore_loaded_png_batch_readonly")
	_check(str(running_ui.get("_batch_job_id")) == "png-batch-fixture", "startup restore did not rebind the exact persisted job")
	_check(str(running_ui.get("_batch_snapshot").get("state", "")) == "INTERRUPTED", "persisted RUNNING state did not display as interrupted")
	_check((running_ui.get_node("RunLevelPipeline") as Button).text.begins_with("Resume Batch"), "interrupted job did not expose explicit Resume Batch")
	_check(running_ui.get("_gameplay_sources").size() == 9, "ninth loaded thumbnail source was lost during job association")
	_check(running_gateway.calls == ["loaded-png-batch-find", "png-batch-latest"], "startup did not use read-only exact composite/job lookups")
	_check(running_gateway.prepared_calls == 0, "startup prepared a worker without an owner click")
	running_ui.call("_run_png_batch")
	_check(running_gateway.prepared_calls == 1, "explicit Resume Batch did not dispatch the same persisted job")
	_check(running_gateway.calls.count("loaded-png-batch-create") == 0, "resume created a new composite instead of reusing the saved job")
	_check(running_gateway.calls.count("png-batch-run") == 0, "UI fixture executed a native solver operation")

	var paused := _build_ui(ids, composite, _job(composite, ids, "PAUSED", []))
	var paused_ui: Control = paused["ui"]
	paused_ui.call("_restore_loaded_png_batch_readonly")
	_check(str(paused_ui.get("_batch_snapshot").get("state", "")) == "PAUSED", "PAUSED state was not restored truthfully")
	_check((paused_ui.get_node("RunLevelPipeline") as Button).text.begins_with("Resume Batch"), "PAUSED job did not require an explicit resume click")

	var retry_items: Array[Dictionary] = []
	for index in [1, 7]:
		var source: Dictionary = composite_items[index]
		retry_items.append({"index": retry_items.size(), "prior_item_index": index,
			"source_id": source["source_id"], "source_sha256": source["source_sha256"],
			"source_record_sha256": source["source_record_sha256"], "column_count": 3 + (index % 3), "status": "FAILED"})
	var retry := _job(composite, ids, "COMPLETE", retry_items)
	retry["parent_job_id"] = "png-batch-parent"
	retry["lineage_verified"] = true
	retry["counts"] = {"total": 2, "ready": 0, "failed": 2, "rejected": 0, "skipped": 0, "remaining": 0}
	var failed := _build_ui(ids, composite, retry)
	var failed_ui: Control = failed["ui"]
	failed_ui.call("_restore_loaded_png_batch_readonly")
	_check((failed_ui.get_node("RunLevelPipeline") as Button).text == "Retry Failed (2)", "verified two-source retry child could not expose its next Retry Failed action")
	_check(bool(failed_ui.call("_batch_job_matches_loaded_sources")), "verified subset retry was rejected only because its item count is below nine")

	var invalid_retry := retry.duplicate(true)
	invalid_retry["items"] = retry_items.duplicate(true)
	invalid_retry["lineage_verified"] = false
	var invalid := _build_ui(ids, composite, invalid_retry)
	var invalid_ui: Control = invalid["ui"]
	invalid_ui.set("_batch_snapshot", invalid_retry)
	invalid_ui.set("_batch_composite_snapshot", composite)
	invalid_ui.set("_batch_import_id", str(composite["batch_id"]))
	_check(not bool(invalid_ui.call("_batch_job_matches_loaded_sources")), "tampered retry ancestry was accepted by the UI authority guard")

	if _errors.is_empty():
		print(PASS_MARKER)
	else:
		for message in _errors:
			push_error(message)
		quit(1)
		return
	quit(0)


func _build_ui(ids: Array[String], composite: Dictionary, job: Dictionary) -> Dictionary:
	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	root.add_child(ui)
	var button := Button.new()
	button.name = "RunLevelPipeline"
	ui.add_child(button)
	var gateway := ReadonlyJobGateway.new()
	gateway.composite = composite.duplicate(true)
	gateway.job = job.duplicate(true)
	ui.set("_screen", "LEVEL FACTORY")
	ui.set("_gateway", gateway)
	var sources: Array[Dictionary] = []
	for source_id in ids:
		sources.append({"source_id": source_id, "source_sha256": source_id.trim_prefix("owner-upload-")})
	ui.set("_gameplay_sources", sources)
	ui.set("_selected_import_source_id", ids[0])
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
