extends SceneTree

const PASS_MARKER := "SB-LFX-015-C001 SESSION recovery integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/SessionRecovery")
	_require(gateway != null and surface != null, "session surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var fixture_root := OS.get_temp_dir().path_join("scrubbots_lfx_015_session_fixture"); _remove_tree(fixture_root); DirAccess.make_dir_recursive_absolute(fixture_root); var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var source_path := fixture_root.path_join("session.png"); image.save_png(source_path)
	var batch: Dictionary = gateway.call("run_studio_extension", "batch-import", {"paths": [source_path]}); var session_source_id := str(batch.get("items", [])[0].get("source_id", "")); var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "12012", "mode": "MASK"}, "res://output/.lfx015-candidate"); var candidate_id := str(generated.get("candidate_id", "")); var pipeline: Dictionary = gateway.call("run_studio_extension", "pipeline", {"candidate_id": candidate_id, "request": {"interrupt_after": "CANDIDATE"}}); var run_id := str(pipeline.get("run_id", ""))
	var pipeline_bytes := FileAccess.get_file_as_bytes(ProjectSettings.globalize_path("res://output/studio-extensions/pipelines").path_join(run_id + ".json")); var batch_id := str(batch.get("batch_id", ""))
	var saved: Dictionary = gateway.call("run_studio_extension", "session-save", {"session_id": "lfx015-runtime", "state": {"surface": "Session", "active_batch_id": batch.get("batch_id", ""), "active_pipeline_run_id": run_id, "autosave_generation": 1}})
	_require(saved.get("session_id") == "lfx015-runtime" and not str(saved).contains("secret"), "typed session save exposed a secret: %s" % saved)
	var persisted := FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://output/studio-extensions/sessions/lfx015-runtime.json")); _require(persisted.contains(str(batch.get("batch_id", ""))) and not persisted.contains("token"), "typed session state was not persisted safely")
	instance.queue_free(); await process_frame; await process_frame
	var restarted := packed.instantiate(); root.add_child(restarted); await process_frame
	var gateway_after_restart: RefCounted = restarted.get("core_gateway"); var surface_after_restart := restarted.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/SessionRecovery"); surface_after_restart.call("set_session_id", "lfx015-runtime"); surface_after_restart.call("restore_session"); await process_frame
	var restored: Dictionary = surface_after_restart.call("snapshot").get("projection", {}); _require(restored.get("recovery") == "RESUMED" and restored.get("validated_references") == true, "fresh Studio did not execute real recovery: %s" % restored)
	_require(restored.get("recovery_execution", {}).get("disposition") == "RESUMED", "recovery coordinator did not report RESUMED")
	_require((restored.get("recovery_execution", {}).get("reused_successful_stage_evidence", []) as Array).size() >= 3, "successful pipeline stages were not reported as reused")
	_require(restored.get("recovery_execution", {}).get("duplicate_source_candidate_job_count") == 0, "recovery created duplicate canonical work")
	_require(FileAccess.get_file_as_bytes(ProjectSettings.globalize_path("res://output/studio-extensions/pipelines").path_join(run_id + ".json")) == pipeline_bytes, "recovery mutated original pipeline evidence")
	var batch_after: Dictionary = gateway_after_restart.call("run_studio_extension", "batch-load", {"batch_id": batch_id}); _require(batch_after.get("batch", {}).get("batch_id") == batch_id and batch_after.get("batch", {}).get("items", []).size() == batch.get("items", []).size(), "recovery changed durable batch identity")
	var missing: Dictionary = gateway.call("run_studio_extension", "session-save", {"session_id": "lfx015-missing", "state": {"surface": "Session", "active_batch_id": "batch-nonexistent"}}); _require(missing.get("reference_validation", [])[0].get("disposition") == "NEEDS_OPERATOR_ACTION", "missing canonical reference did not require operator action")
	var corrupt_path := ProjectSettings.globalize_path("res://output/studio-extensions/sessions/lfx015-runtime.json"); var corrupt := FileAccess.open(corrupt_path, FileAccess.WRITE); corrupt.store_string("{\"schema\":\"scrubbots-studio-session\"}\n"); corrupt.close(); var corrupt_restore: Dictionary = gateway.call("run_studio_extension", "session-restore", {"session_id": "lfx015-runtime"}); _require(corrupt_restore.get("state") == "ERROR", "corrupt session did not fail closed")
	surface_after_restart.call("save_session"); await process_frame; _require(surface_after_restart.call("snapshot").get("secrets_persisted") == false, "session UI did not retain secret-scrubbing invariant")
	_cleanup(restarted)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); instance.queue_free(); _finish()

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
