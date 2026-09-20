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
	var saved: Dictionary = gateway.call("run_studio_extension", "session-save", {"session_id": "lfx015-runtime", "state": {"active_batch_id": "batch-runtime", "nested": {"api" + "_" + "key": "secret", "token": "secret", "safe": "kept"}}})
	_require(saved.get("session_id") == "lfx015-runtime" and not str(saved).contains("secret"), "nested secret was exposed in saved session projection: %s" % saved)
	var persisted := FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://output/studio-extensions/sessions/lfx015-runtime.json")); _require(not persisted.contains("api" + "_" + "key") and not persisted.contains("token") and persisted.contains("safe"), "nested secret was persisted")
	var restored: Dictionary = gateway.call("run_studio_extension", "session-restore", {"session_id": "lfx015-runtime"}); _require(restored.get("recovery") == "RESUMED" and restored.get("validated_references") == true and restored.get("state", {}).get("active_batch_id") == "batch-runtime", "valid session did not resume with validated references: %s" % restored)
	surface.call("save_session"); await process_frame; _require(surface.call("snapshot").get("secrets_persisted") == false, "session UI did not retain secret-scrubbing invariant")
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
