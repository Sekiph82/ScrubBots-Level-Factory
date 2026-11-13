extends SceneTree

## R09-R02-R04-R03 batch UI binding, rewritten 2026-11-12 for the Pending flow.
##
## Since 2026-11-08 an explicit Run snapshots only the PixelLab Final sources
## whose Release Pool status is PENDING (SHA-matched), in gallery order, and
## plans one durable job bound to the pinned game Runtime. Thumbnail selection
## stays read-only and a job whose sources do not match is never resumed.

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const TEST_PATHS := preload("res://tests/factory_test_paths.gd")
const PASS_MARKER := "SB-LFX-018-C001-R02-R05-R09-R02-R04-R03 batch UI binding PASS"
const PINNED_GAME_COMMIT := "6534537ceb4c71c63286614b74e4801145d5fb4d"  # owner re-pin 2026-11-13

var _errors: Array[String] = []


class MockGateway extends RefCounted:
	var calls: Array[String] = []
	var requests: Array[Dictionary] = []
	var prepared: Array[String] = []

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		calls.append(operation)
		requests.append(request.duplicate(true))
		if operation == "pending-png-batch-create":
			var items: Array = []
			for source_id in request.get("source_ids", []):
				items.append({"index": items.size(), "source_id": source_id})
			return {"batch_id": "batch-pending-fixture", "items": items}
		if operation == "png-batch-create":
			return {"job": {"job_id": "png-batch-fixture", "import_batch_id": "batch-pending-fixture", "state": "QUEUED",
				"counts": {"total": 2, "remaining": 2}}}
		return {"state": "UNAVAILABLE"}

	func prepare_studio_extension_call(operation: String, _request: Dictionary) -> Dictionary:
		prepared.append(operation)
		return {}  # never start a real worker

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		push_error("test must never execute a solver worker")
		return {}


func _init() -> void:
	call_deferred("_run_suite")


func _source(index: int) -> Dictionary:
	var sha := "%064x" % (index + 1)
	return {"source_id": "owner-upload-" + sha, "source_sha256": sha, "display_filename": "LF-%06d.png" % (index + 1),
		"disposition": "SOURCE_ONLY", "width": 56, "height": 56, "path": ""}


func _run_suite() -> void:
	# The pinned Runtime must exist for a plan; create it inside the isolated copy only.
	var runtime := TEST_PATHS.data("Level Factory/Runtime/%s" % PINNED_GAME_COMMIT)
	DirAccess.make_dir_recursive_absolute(runtime)
	var project := FileAccess.open(runtime.path_join("project.godot"), FileAccess.WRITE)
	if project != null:
		project.store_string("; isolated test stand-in for the pinned ScrubBots runtime\n")
		project.close()

	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	root.add_child(ui)
	var gateway := MockGateway.new()
	ui.set("_screen", "LEVEL FACTORY")
	ui.set("_gateway", gateway)
	ui.set("_operation_running", false)
	var sources: Array[Dictionary] = [_source(0), _source(1), _source(2)]
	for source in sources:
		ui.call("_upsert_imported_source", source.duplicate(true), false)
	ui.call("_refresh_gameplay_sources")
	# Sources 0 and 1 are Pending; source 2 is already READY and must be excluded.
	var records: Array = []
	for index in range(3):
		records.append({"source_id": sources[index]["source_id"], "source_sha256": sources[index]["source_sha256"],
			"status": "READY" if index == 2 else "PENDING"})

	# 1. Before the Release Pool statuses load, Run must not plan anything.
	ui.set("_owner_release_archive_loaded", false)
	ui.call("_run_png_batch")
	_check(not gateway.calls.has("pending-png-batch-create") and not gateway.calls.has("png-batch-create"),
		"Run planned a batch before Release Pool statuses were loaded: %s" % [gateway.calls])

	# 2. Explicit Run snapshots exactly the Pending sources in gallery order.
	ui.set("_owner_release_archive", {"schema": "scrubbots-owner-release-library-view/v1", "records": records})
	ui.set("_owner_release_archive_loaded", true)
	gateway.calls.clear()
	gateway.requests.clear()
	ui.call("_run_png_batch")
	_check(gateway.calls == ["pending-png-batch-create", "png-batch-create"],
		"explicit Run did not plan one Pending snapshot and one job: %s" % [gateway.calls])
	if gateway.requests.size() >= 2:
		_check(gateway.requests[0].get("source_ids", []) == [sources[0]["source_id"], sources[1]["source_id"]],
			"Pending snapshot did not contain exactly the Pending sources in gallery order: %s" % [gateway.requests[0]])
		var settings: Dictionary = gateway.requests[1].get("settings", {})
		_check(gateway.requests[1].get("batch_id", "") == "batch-pending-fixture", "job was not planned for the displayed Pending snapshot")
		_check(str(settings.get("game_project", "")).simplify_path() == runtime.simplify_path(),
			"batch plan did not carry the pinned game Runtime: %s" % [settings])
		_check(int(settings.get("solver_timeout_seconds", 0)) == 900, "batch plan did not use the single 900 s solver budget")
	_check(str(ui.get("_batch_job_id")) == "png-batch-fixture", "planned job identity was not retained")
	# Step 1 legitimately queued a read-only Release Pool status refresh.
	_check(gateway.prepared.count("png-batch-run") == 1 and gateway.prepared.filter(func(operation: String) -> bool:
			return operation != "png-batch-run" and operation != "owner-release-library").is_empty(),
		"explicit Run did not request exactly one batch worker: %s" % [gateway.prepared])

	# 3. Selecting another thumbnail is read-only.
	var calls_before_select := gateway.calls.size()
	var prepared_before_select := gateway.prepared.size()
	ui.call("_bind_displayed_batch_to_source", sources[1]["source_id"])
	_check(gateway.calls.size() == calls_before_select and gateway.prepared.size() == prepared_before_select,
		"thumbnail selection called the gateway")
	_check(str(ui.get("_batch_import_id")) == "batch-pending-fixture", "thumbnail selection rebound the displayed batch")

	# 4. A job whose sources do not match is never planned or resumed.
	ui.set("_batch_job_source_mismatch", true)
	ui.set("_batch_job_id", "png-batch-other")
	var calls_before_mismatch := gateway.calls.size()
	var prepared_before_mismatch := gateway.prepared.size()
	ui.call("_run_png_batch")
	_check(gateway.calls.size() == calls_before_mismatch and gateway.prepared.size() == prepared_before_mismatch,
		"mismatched job reached create/run dispatch")

	ui.free()
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for message in _errors:
		push_error(message)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
