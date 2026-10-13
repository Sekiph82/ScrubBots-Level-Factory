extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R03 batch UI binding PASS"

var _errors: Array[String] = []


class MockGateway extends RefCounted:
	var calls: Array[String] = []
	var requests: Array[Dictionary] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append(operation)
		requests.append(request)
		if operation == "batch-load":
			return {"batch": {"batch_id": request.get("batch_id", ""), "items": [], "counts": {"success": 0}}}
		if operation == "png-batch-latest":
			return {"disposition": "BATCH_JOB_SOURCE_MISMATCH", "mismatch_job": {"import_batch_id": "batch-A"}}
		return {"job": {"job_id": "png-batch-good", "import_batch_id": "batch-good", "state": "QUEUED"}}

	func prepare_studio_extension_call(_operation: String, _request: Dictionary) -> Dictionary:
		return {}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		push_error("test must never execute a solver worker")
		return {}


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	root.add_child(ui)
	var gateway := MockGateway.new()
	ui.set("_screen", "LEVEL FACTORY")
	ui.set("_gateway", gateway)
	ui.set("_batch_import_id", "batch-good")
	ui.set("_batch_job_id", "")
	ui.set("_batch_job_source_mismatch", false)
	ui.set("_pinned_source_preflight_ok", false)
	ui.call("_run_png_batch")
	_check(gateway.calls == ["png-batch-create"], "valid batch was blocked by the currently selected thumbnail preflight or did not create a plan")
	_check(gateway.requests.size() == 1 and gateway.requests[0].get("batch_id") == "batch-good", "explicit Run Entire Batch did not create a plan for the displayed batch")
	_check(gateway.requests[0].get("settings", {}).has("game_project"), "batch plan did not carry pinned game authority for per-source validation")
	ui.set("_source_batch_by_id", {"source-B": "batch-B"})
	ui.call("_bind_displayed_batch_to_source", "source-B")
	_check(str(ui.get("_batch_import_id")) == "batch-B", "selecting a B thumbnail did not switch the displayed import batch")
	_check(bool(ui.get("_batch_job_source_mismatch")), "latest resumable A job was not marked as mismatched for displayed batch B")
	ui.set("_batch_job_source_mismatch", true)
	ui.set("_batch_job_id", "png-batch-other")
	var calls_before_mismatch := gateway.calls.size()
	ui.call("_run_png_batch")
	_check(gateway.calls.size() == calls_before_mismatch, "mismatched restart job reached create/run pipeline dispatch")
	if _errors.is_empty():
		print(PASS_MARKER)
	else:
		for message in _errors:
			push_error(message)
		quit(1)
		return
	quit(0)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
