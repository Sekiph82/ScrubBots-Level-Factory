extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const OUTPUT_RELATIVE_ROOT := ".lfx-001-dashboard-test"
const OUTPUT_RELATIVE_MANIFEST := OUTPUT_RELATIVE_ROOT + "/batch-manifest.json"
const CORRUPT_RELATIVE_MANIFEST := OUTPUT_RELATIVE_ROOT + "-corrupt/batch-manifest.json"
const QUALITY_POLICY_RELATIVE_PATH := OUTPUT_RELATIVE_ROOT + "/quality-policy.json"
const PASS_MARKER := "SB-LFX-001-C001 Factory Operations Dashboard derived-view integration PASS"

var _errors: Array[String] = []
var _root: Node
var _gateway: RefCounted
var _dashboard: Node


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var scene := ResourceLoader.call("load", MAIN_SCENE_PATH) as PackedScene
	_require(scene != null, "factory_studio.tscn could not be loaded")
	if not _errors.is_empty():
		_finish()
		return
	_root = scene.instantiate()
	root.add_child(_root)
	await process_frame
	_gateway = _root.get("core_gateway") as RefCounted
	_dashboard = _root.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/OperationsDashboard")
	_require(_gateway != null, "real Factory Studio shell did not expose the canonical gateway")
	_require(_dashboard != null, "real Factory Studio workspace did not instantiate OperationsDashboard")
	if not _errors.is_empty():
		_finish()
		return

	var output_root := ProjectSettings.globalize_path("res://output/" + OUTPUT_RELATIVE_ROOT)
	var policy_path := ProjectSettings.globalize_path("res://output/" + QUALITY_POLICY_RELATIVE_PATH)
	_remove_tree(output_root)
	_remove_tree(ProjectSettings.globalize_path("res://output/" + OUTPUT_RELATIVE_ROOT + "-corrupt"))
	_write_quality_policy(policy_path)
	var captured: Array[String] = []
	var python_executable := str(_gateway.get("python_executable"))
	var launcher := ProjectSettings.globalize_path("res://scripts/factory_core_launcher.py")
	var batch_exit := OS.execute(python_executable, PackedStringArray([
		launcher,
		"batch",
		"--difficulty", "EASY",
		"--count", "1",
		"--max-attempts", "1",
		"--mode", "MASK",
		"--seed", "905",
		"--width", "20",
		"--height", "20",
		"--quality-policy-json", policy_path,
		"--output", output_root,
	]), captured, true, false)
	_require(batch_exit == 7, "canonical rejected batch must exit 7, got %s (%s)" % [batch_exit, " ".join(captured)])
	var manifest_path := ProjectSettings.globalize_path("res://output/" + OUTPUT_RELATIVE_MANIFEST)
	_require(FileAccess.file_exists(manifest_path), "canonical rejected batch did not create batch-manifest.json")
	if not _errors.is_empty():
		_cleanup_and_finish()
		return
	var original_bytes := FileAccess.get_file_as_bytes(manifest_path)

	_dashboard.call("set_manifest_relative_path", OUTPUT_RELATIVE_MANIFEST)
	_dashboard.call("refresh_manifest")
	await process_frame
	var projection: Dictionary = _dashboard.call("snapshot")
	var manifest: Dictionary = JSON.parse_string(original_bytes.get_string_from_utf8())
	_require(str(projection.get("state", "")) == "READY", "valid canonical manifest was not READY: %s" % projection)
	_require(projection.get("batch_id") == manifest.get("batch_id"), "dashboard batch identity differs from canonical manifest")
	_require(projection.get("terminal_state") == manifest.get("terminal_state"), "dashboard terminal state differs from canonical manifest")
	_require(projection.get("requested_count") == manifest.get("requested_count"), "dashboard requested count differs from canonical manifest")
	_require(projection.get("max_attempts") == manifest.get("max_attempts"), "dashboard max attempts differs from canonical manifest")
	_require(projection.get("attempt_count") == manifest.get("attempts", []).size(), "dashboard attempt count is not derived from canonical attempts")
	_require(projection.get("next_attempt_index") == manifest.get("next_attempt_index"), "dashboard next attempt index differs from canonical manifest")
	_require(projection.get("accepted_count") == manifest.get("accepted_count"), "dashboard accepted count differs from canonical manifest")
	_require(str(projection.get("source_classification", "")) == "CANONICAL_BATCH / PROCEDURAL", "dashboard source classification is not truthful: %s" % projection)
	var request_template: Dictionary = manifest.get("request_template", {})
	var request_context: Dictionary = projection.get("request_context", {})
	for key in ["difficulty", "width", "height", "generator_mode"]:
		_require(request_context.get(key) == request_template.get(key), "dashboard request context mismatch for %s" % key)
	var expected_dispositions := {"ACCEPTED": 0.0, "QUALITY_REJECTED": 0.0, "GENERATOR_FAILURE": 0.0, "DUPLICATE": 0.0}
	var expected_rejections := {}
	for attempt in manifest.get("attempts", []):
		expected_dispositions[attempt.get("status")] = float(expected_dispositions.get(attempt.get("status"), 0.0)) + 1.0
		for code in attempt.get("rejection_codes", []):
			expected_rejections[code] = float(expected_rejections.get(code, 0.0)) + 1.0
	_require(projection.get("disposition_counts") == expected_dispositions, "dashboard disposition counts are not canonical: %s != %s" % [projection.get("disposition_counts"), expected_dispositions])
	_require(projection.get("rejection_code_counts") == expected_rejections, "dashboard rejection-code counts are not canonical")
	_require(projection.get("latest_attempt") == manifest.get("attempts", [])[manifest.get("attempts", []).size() - 1], "dashboard latest attempt is not canonical")
	var unavailable: Dictionary = projection.get("unavailable", {})
	for key in ["owner_review", "solver", "difficulty_v1", "timing", "provider_cost"]:
		_require(str(unavailable.get(key, "")).begins_with("NOT AVAILABLE"), "dashboard %s was not explicitly unavailable" % key)
	var studio_evidence: Dictionary = projection.get("studio_evidence", {})
	_require(studio_evidence.get("state") == "NOT AVAILABLE", "Studio evidence was not kept separate and unavailable")
	_require(FileAccess.get_file_as_bytes(manifest_path) == original_bytes, "dashboard inspection changed canonical manifest bytes")

	var corrupt_path := ProjectSettings.globalize_path("res://output/" + CORRUPT_RELATIVE_MANIFEST)
	DirAccess.make_dir_recursive_absolute(corrupt_path.get_base_dir())
	var corrupt_file := FileAccess.open(corrupt_path, FileAccess.WRITE)
	corrupt_file.store_string("{\"batch_id\":\"corrupt\"}")
	corrupt_file.close()
	_dashboard.call("set_manifest_relative_path", CORRUPT_RELATIVE_MANIFEST)
	_dashboard.call("refresh_manifest")
	await process_frame
	var corrupt_projection: Dictionary = _dashboard.call("snapshot")
	_require(corrupt_projection.get("state") == "ERROR", "malformed manifest did not fail closed")
	_require(not corrupt_projection.has("batch_id"), "malformed manifest leaked trusted batch identity")
	_require(not corrupt_projection.has("request_context"), "malformed manifest leaked trusted request context")
	_require(not str(corrupt_projection.get("error", "")).is_empty(), "malformed manifest did not report an error")
	_require(FileAccess.get_file_as_bytes(manifest_path) == original_bytes, "malformed inspection changed canonical manifest bytes")

	_dashboard.call("set_manifest_relative_path", "")
	_dashboard.call("refresh_manifest")
	await process_frame
	var empty_projection: Dictionary = _dashboard.call("snapshot")
	_require(empty_projection.get("state") == "EMPTY", "empty dashboard selection was not EMPTY")
	_require(empty_projection.get("reason") == "EMPTY — no canonical batch selected", "empty dashboard reason is not truthful")

	_cleanup_and_finish()


func _write_quality_policy(path: String) -> void:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var policy := {
		"version": "m07-quality-policy-v1",
		"difficulty": "EASY",
		"tiny_region_max_size": 3,
		"max_isolated_ratio": 0.2,
		"max_tiny_cell_ratio": 0.35,
		"max_largest_region_ratio": 0.0,
		"max_color_dominance_ratio": 1.0,
		"full_slab_min_occupied_ratio": 0.8,
		"max_checkerboard_score": 0.98,
		"reject_full_single_shape_slab": true,
	}
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(policy))
	file.close()


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	var directory := DirAccess.open(path)
	if directory == null:
		return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next()
		if entry.is_empty():
			break
		if entry in [".", ".."]:
			continue
		var child := path.path_join(entry)
		if directory.current_is_dir():
			_remove_tree(child)
		else:
			DirAccess.remove_absolute(child)
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _cleanup_and_finish() -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/" + OUTPUT_RELATIVE_ROOT))
	_remove_tree(ProjectSettings.globalize_path("res://output/" + OUTPUT_RELATIVE_ROOT + "-corrupt"))
	_finish()


func _require(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)


func _finish() -> void:
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)
