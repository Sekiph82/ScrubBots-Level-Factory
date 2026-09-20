extends SceneTree

const PASS_MARKER := "SB-LFX-013-C001 FAILURE retry integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/FailureInbox")
	_require(gateway != null and surface != null, "failure surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var failure: Dictionary = gateway.call("run_studio_extension", "record-failure", {"operation": "import-validation", "stage": "VALIDATE", "disposition": "REJECTED", "reason": "SOURCE_INVALID", "inputs": {"source_id": "owner-upload-missing"}})
	_require(not str(failure.get("failure_id", "")).is_empty() and bool(failure.get("retryable", false)), "eligible failure was not recorded as retryable: %s" % failure)
	var listed: Dictionary = gateway.call("run_studio_extension", "failures-list", {}); _require(listed.get("state") == "SUCCESS" and (listed.get("failures", []) as Array).size() == 1, "failure inbox did not list canonical evidence: %s" % listed)
	var retry: Dictionary = gateway.call("run_studio_extension", "retry-failure", {"failure_id": failure.get("failure_id", ""), "changes": {"operator_note": "runtime retry"}})
	_require(retry.get("disposition") == "RETRY_FAILED" and retry.get("execution", {}).get("state") == "ERROR", "retry did not execute and preserve failure diagnostics: %s" % retry)
	var forbidden: Dictionary = gateway.call("run_studio_extension", "retry-failure", {"failure_id": failure.get("failure_id", ""), "changes": {"source_id": "different-source"}}); _require(forbidden.get("state") == "ERROR", "retry accepted an unauthorized identity change")
	var blocked: Dictionary = gateway.call("run_studio_extension", "record-failure", {"operation": "pipeline", "stage": "SOLVE", "disposition": "INCONCLUSIVE", "reason": "M03 unavailable", "inputs": {}}); _require(bool(blocked.get("retryable", true)) == false, "unavailable solver failure was marked retryable")
	surface.call("refresh"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("state") == "SUCCESS", "failure UI did not invoke canonical inbox list")
	_cleanup(instance)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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
