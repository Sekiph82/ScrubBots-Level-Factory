extends SceneTree

const PASS_MARKER := "SB-LFX-008-C001 PRESETS integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var presets := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ProductionPresets")
	var gateway: RefCounted = instance.get("core_gateway")
	_require(presets != null and gateway != null, "preset surface or gateway did not instantiate")
	if presets == null or gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-preset-runs")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var settings_a := {"difficulty": "EASY", "width": 20, "height": 20, "seed": 88008, "mode": "MASK"}
	var saved: Dictionary = gateway.call("run_studio_extension", "preset-save", {"preset_id": "lfx008-runtime", "name": "Runtime recipe", "operation": "Generate", "settings": settings_a})
	_require(_request_equal(saved.get("settings", {}), settings_a), "preset did not persist canonical settings: %s" % saved)
	var applied: Dictionary = gateway.call("run_studio_extension", "preset-apply", {"preset_id": "lfx008-runtime"})
	_require(applied.get("state") == "SUCCESS", "Apply Preset did not execute canonical Generate: %s" % applied)
	var execution_a: Dictionary = applied.get("execution", {})
	var metadata_path_a := ProjectSettings.globalize_path("res://../" + str(execution_a.get("source_bundle_path", "")).trim_prefix("res://")).path_join("metadata.json")
	var metadata_a: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(metadata_path_a))
	_require(metadata_a.get("generation", {}).get("request", {}) == execution_a.get("expanded_request", {}), "execution expanded request does not exactly equal bundle metadata request: %s" % execution_a)
	_require(execution_a.get("expanded_request", {}).get("seed", {}).get("type") == "int", "expanded request did not persist typed seed")
	_require(execution_a.get("expanded_request", {}).has("generator_options"), "expanded request omitted generator defaults/options")
	var execution_path := ProjectSettings.globalize_path("res://output/studio-extensions/preset-executions").path_join("%s.json" % execution_a.get("execution_id", ""))
	var execution_before := FileAccess.get_file_as_bytes(execution_path)
	var updated_settings := {"difficulty": "HARD", "width": 21, "height": 22, "seed": 88009, "mode": "RULES"}
	gateway.call("run_studio_extension", "preset-save", {"preset_id": "lfx008-runtime", "name": "Updated recipe", "operation": "Generate", "settings": updated_settings})
	var reapplied: Dictionary = gateway.call("run_studio_extension", "preset-apply", {"preset_id": "lfx008-runtime"})
	var updated_request: Dictionary = reapplied.get("execution", {}).get("expanded_request", {})
	_require(updated_request.get("difficulty") == "HARD" and updated_request.get("width") == 21 and updated_request.get("height") == 22 and updated_request.get("seed", {}).get("value") == 88009 and updated_request.get("generator_mode") == "RULES", "updated preset did not affect the new canonical execution: %s" % reapplied)
	_require(FileAccess.get_file_as_bytes(execution_path) == execution_before, "updating preset changed prior execution evidence")
	gateway.call("run_studio_extension", "preset-delete", {"preset_id": "lfx008-runtime"})
	_require(FileAccess.get_file_as_bytes(execution_path) == execution_before, "deleting preset invalidated prior execution evidence")
	var invalid: Dictionary = gateway.call("run_studio_extension", "preset-save", {"preset_id": "lfx008-invalid-runtime", "name": "Invalid", "operation": "Generate", "settings": {"difficulty": "EASY", "width": 20, "height": 20, "seed": 1, "mode": "MASK", "unknown": true}})
	_require(invalid.get("state") == "ERROR", "unknown preset field did not fail closed")
	presets.call("show_presets"); await process_frame
	_cleanup(instance)

func _request_equal(left: Dictionary, right: Dictionary) -> bool:
	for key in right.keys():
		var left_value: Variant = left.get(key, "")
		var right_value: Variant = right.get(key, "")
		if left_value is float and right_value is int:
			if not is_equal_approx(left_value, float(right_value)): return false
		elif left_value is int and right_value is float:
			if not is_equal_approx(float(left_value), right_value): return false
		elif left_value != right_value:
			return false
	return true

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-preset-runs")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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
