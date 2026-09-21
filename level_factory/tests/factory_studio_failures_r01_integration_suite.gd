extends SceneTree

const PASS_MARKER := "SB-LFX-013-C001 FAILURE retry integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/FailureInbox")
	_require(gateway != null and surface != null, "failure surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads"))
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_013_failure_fixture"); _remove_tree(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root)
	var invalid_image := Image.create(19, 20, false, Image.FORMAT_RGB8); invalid_image.fill(Color8(233, 75, 75)); var invalid_path := _fixture_root.path_join("invalid.png"); invalid_image.save_png(invalid_path)
	var imported_invalid: Dictionary = gateway.call("run_owner_import", invalid_path); var invalid_id := str(imported_invalid.get("source_id", "")); _require(imported_invalid.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "real invalid source import failed")
	var validation: Dictionary = gateway.call("run_studio_extension", "validate-source", {"source_id": invalid_id}); _require(validation.get("exact_logical_source") == false, "invalid source validation did not produce canonical rejection")
	var pipeline_failure: Dictionary = gateway.call("run_studio_extension", "pipeline", {"source_id": invalid_id}); _require((pipeline_failure.get("stages", []) as Array).any(func(stage): return stage.get("disposition") == "BLOCKED"), "real failed pipeline did not persist blocked stage evidence")
	var valid_image := Image.create(20, 20, false, Image.FORMAT_RGB8); valid_image.fill(Color8(233, 75, 75)); var valid_path := _fixture_root.path_join("valid.png"); valid_image.save_png(valid_path)
	var imported_valid: Dictionary = gateway.call("run_owner_import", valid_path); var valid_id := str(imported_valid.get("source_id", "")); gateway.call("run_studio_extension", "pipeline", {"source_id": valid_id})
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "13013", "mode": "MASK"}, "res://output/.lfx013-success"); _require(generated.get("state") == "SUCCESS", "successful control candidate failed"); gateway.call("run_studio_extension", "pipeline", {"candidate_id": generated.get("candidate_id", "")})
	var listed: Dictionary = gateway.call("run_studio_extension", "failures-list", {}); var failures: Array = listed.get("failures", []); _require(listed.get("state") == "SUCCESS" and failures.any(func(item): return item.get("originating_evidence_id", "").begins_with(invalid_id)), "Failure Inbox did not derive the real validation evidence")
	_require(not failures.any(func(item): return bool(item.get("retryable", false)) and item.get("inputs", {}).get("candidate_id", "") == generated.get("candidate_id", "")), "successful control work appeared as retryable failure truth")
	var pipeline_entry: Dictionary = failures.filter(func(item): return item.get("operation") == "pipeline" and item.get("inputs", {}).get("source_id", "") == invalid_id)[0] if failures.any(func(item): return item.get("operation") == "pipeline" and item.get("inputs", {}).get("source_id", "") == invalid_id) else {}
	_require(not pipeline_entry.is_empty(), "canonical failed pipeline evidence was not indexed")
	_require(not bool(pipeline_entry.get("retryable", true)) and str(pipeline_entry.get("non_retryable_reason", "")).contains("safely retryable"), "unsupported pipeline failure remained retryable")
	var pipeline_evidence_path := _repo_path(str(pipeline_entry.get("evidence_reference", ""))); var pipeline_evidence_before := FileAccess.get_file_as_bytes(pipeline_evidence_path); var pipeline_count_before := _json_files(ProjectSettings.globalize_path("res://output/studio-extensions/pipelines"))
	var retry: Dictionary = gateway.call("run_studio_extension", "retry-failure", {"failure_id": pipeline_entry.get("failure_id", ""), "changes": {"operator_note": "runtime retry"}}); _require(retry.get("parent_failure_id") == pipeline_entry.get("failure_id") and retry.get("disposition") == "NOT_AVAILABLE", "unsupported pipeline retry was not reported as NOT_AVAILABLE")
	_require(retry.get("originating_pipeline_run_id") == pipeline_failure.get("run_id", ""), "retry did not bind the originating pipeline run")
	_require((retry.get("reused_successful_stage_evidence", []) as Array).size() >= 1 and (retry.get("reused_prior_stage_ids", []) as Array).size() >= 1, "retry did not record immutable prior-stage references")
	_require((retry.get("newly_attempted_stages", []) as Array).is_empty(), "unsupported pipeline retry attempted a stage")
	_require(FileAccess.get_file_as_bytes(pipeline_evidence_path) == pipeline_evidence_before, "originating canonical pipeline evidence changed during retry")
	_require(_json_files(ProjectSettings.globalize_path("res://output/studio-extensions/pipelines")) == pipeline_count_before, "unsupported retry created a duplicate pipeline run")
	var retryable: Dictionary = failures.filter(func(item): return bool(item.get("retryable", false)) and item.get("operation") == "import-validation" and item.get("inputs", {}).get("source_id", "") == invalid_id)[0] if failures.any(func(item): return bool(item.get("retryable", false)) and item.get("operation") == "import-validation" and item.get("inputs", {}).get("source_id", "") == invalid_id) else {}
	_require(not retryable.is_empty(), "real eligible validation failure was not retryable")
	var evidence_path := _repo_path(str(retryable.get("evidence_reference", ""))); var evidence_before := FileAccess.get_file_as_bytes(evidence_path)
	var validation_retry: Dictionary = gateway.call("run_studio_extension", "retry-failure", {"failure_id": retryable.get("failure_id", ""), "changes": {"operator_note": "runtime validation retry"}}); _require(validation_retry.get("parent_failure_id") == retryable.get("failure_id") and validation_retry.get("disposition") in ["RETRY_FAILED", "RETRY_EXECUTED"], "canonical validation retry did not preserve originating failure")
	_require(FileAccess.get_file_as_bytes(evidence_path) == evidence_before, "originating canonical validation evidence changed during retry")
	_require(validation_retry.get("originating_evidence_sha256_before") == validation_retry.get("originating_evidence_sha256_after") and validation_retry.get("originating_evidence_sha256_before") == retryable.get("evidence_sha256", ""), "validation retry did not preserve originating evidence identity")
	var unavailable := failures.filter(func(item): return item.get("stage") in ["SOLVE", "DIFFICULTY"]); _require(unavailable.any(func(item): return not bool(item.get("retryable", true))), "unavailable SOLVE/DIFFICULTY evidence was retryable")
	surface.call("refresh"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("state") == "SUCCESS", "failure UI did not invoke canonical inbox list")
	if not retryable.is_empty(): surface.call("select_failure", str(retryable.get("failure_id", ""))); _require(not surface.call("snapshot").get("projection", {}).get("failures", []).is_empty(), "failure UI did not render selectable canonical rows")
	_cleanup(instance)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/.lfx013-success")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); _remove_tree(_fixture_root); instance.queue_free(); _finish()

func _repo_path(relative_path: String) -> String:
	return ProjectSettings.globalize_path("res://" + "../" + relative_path)

func _json_files(path: String) -> int:
	if not DirAccess.dir_exists_absolute(path): return 0
	var directory := DirAccess.open(path); if directory == null: return 0
	var count := 0
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next(); if entry.is_empty(): break
		if not directory.current_is_dir() and entry.ends_with(".json"): count += 1
	directory.list_dir_end()
	return count

func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path): return
	var directory := DirAccess.open(path); if directory == null: return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next(); if entry.is_empty(): break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): _remove_tree(child)
		else: DirAccess.remove_absolute(child)
	directory.list_dir_end(); DirAccess.remove_absolute(path)

func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)

func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
