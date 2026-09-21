extends SceneTree

const PASS_MARKER := "SB-LFX-011-C001 EXACT REPRODUCE integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway")
	var target := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/TargetControls")
	var reproduce_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ExactReproduce")
	_require(gateway != null and target != null and reproduce_surface != null, "target, reproduce surface, or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx011-reproduce")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-reproductions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "11011", "mode": "MASK"}, "res://output/.lfx011-reproduce")
	_require(generated.get("state") == "SUCCESS", "canonical Generate fixture failed: %s" % generated)
	var candidate_id := str(generated.get("candidate_id", ""))
	var metadata_path := str(generated.get("metadata_path", ""))
	var bundle_root := metadata_path.get_base_dir()
	var original_files := {}
	for name in ["artwork.png", "artwork.json", "metadata.json"]: original_files[name] = FileAccess.get_file_as_bytes(bundle_root.path_join(name))
	var capability: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": candidate_id})
	_require(capability.get("disposition") == "EXACT_REPRODUCIBLE", "valid recorded Generate was not exact-reproducible: %s" % capability)
	_require(str(capability.get("recorded_metadata", "")).ends_with("metadata.json"), "capability did not expose the recorded metadata evidence")
	reproduce_surface.call("set_selected_identity", candidate_id); await process_frame
	_require(not reproduce_surface.call("capability_button_enabled"), "Exact Reproduce was enabled before a fresh capability check")
	reproduce_surface.call("check_capability"); await process_frame
	_require(reproduce_surface.call("capability_button_enabled"), "Exact Reproduce did not enable for a fresh EXACT_REPRODUCIBLE capability")
	reproduce_surface.call("set_selected_identity", "tampered-selection"); await process_frame
	_require(not reproduce_surface.call("capability_button_enabled"), "candidate identity edit did not invalidate capability")
	_set_draft(target, "changed-live-draft", 23, 24, 2, 2, "materially-different-preset")
	var divergent_draft: Dictionary = target.call("draft_snapshot")
	_require(divergent_draft.get("seed") == "changed-live-draft" and divergent_draft.get("width") == 23 and divergent_draft.get("mode") == "WFC", "draft/preset values did not materially diverge")
	reproduce_surface.call("set_selected_identity", candidate_id); reproduce_surface.call("check_capability"); await process_frame
	reproduce_surface.call("exact_reproduce"); await process_frame
	var reproduced: Dictionary = reproduce_surface.call("snapshot")
	_require(reproduced.get("state") == "SUCCESS" and reproduced.get("disposition") == "MATCH", "exact reproduction did not MATCH: %s" % reproduced)
	var output_path := str(reproduced.get("output_path", ""))
	var repository_root := ProjectSettings.globalize_path("res://" + ".." + "/")
	_require(not output_path.is_empty() and output_path != bundle_root and output_path.contains("studio-reproductions") and DirAccess.dir_exists_absolute(repository_root.path_join(output_path)), "exact reproduction did not create a separate output bundle")
	for name in original_files.keys(): _require(FileAccess.get_file_as_bytes(bundle_root.path_join(name)) == original_files[name], "source bundle changed after exact reproduction: %s" % name)
	var metadata_before := FileAccess.get_file_as_bytes(bundle_root.path_join("metadata.json"))
	var corrupt := FileAccess.open(bundle_root.path_join("metadata.json"), FileAccess.WRITE); corrupt.store_string("{\"tampered\":true}\n"); corrupt.close()
	var stale: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": candidate_id})
	_require(stale.get("disposition") == "STALE/INVALID", "tampered metadata was not rejected fail-closed: %s" % stale)
	var restore := FileAccess.open(bundle_root.path_join("metadata.json"), FileAccess.WRITE); restore.store_buffer(metadata_before); restore.close()
	var owner_fixture := _fixture_source(gateway)
	var owner_only: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": owner_fixture})
	_require(owner_only.get("disposition") == "SOURCE_RETRIEVABLE_ONLY", "verified OWNER_UPLOAD was not source-retrievable-only: %s" % owner_only)
	var missing_owner: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": "owner-upload-missing"})
	_require(missing_owner.get("disposition") in ["STALE/INVALID", "NOT_REPRODUCIBLE"], "nonexistent OWNER_UPLOAD was falsely source-retrievable: %s" % missing_owner)
	var unsupported: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": "unsupported-provider-record"})
	_require(unsupported.get("disposition") != "EXACT_REPRODUCIBLE", "unsupported record was enabled for exact reproduction")
	reproduce_surface.call("set_selected_identity", owner_fixture); reproduce_surface.call("check_capability"); await process_frame
	var owner_surface: Dictionary = reproduce_surface.call("snapshot")
	_require(owner_surface.get("disposition") == "SOURCE_RETRIEVABLE_ONLY" and not reproduce_surface.call("capability_button_enabled"), "real source-only record was enabled through the UI")
	_require(str(owner_surface.get("reason", "")).contains("not deterministic regeneration"), "source-only UI reason was not rendered")
	_cleanup(instance)

func _set_draft(target: Node, seed_value: String, width: int, height: int, difficulty_index: int, mode_index: int, label_value: String) -> void:
	var seed_control: LineEdit = target.get("seed_control"); var width_control: SpinBox = target.get("width_control"); var height_control: SpinBox = target.get("height_control")
	var difficulty_control: OptionButton = target.get("difficulty_control"); var mode_control: OptionButton = target.get("mode_control"); var label_control: LineEdit = target.get("candidate_label_control")
	seed_control.text = seed_value; width_control.value = width; height_control.value = height; difficulty_control.select(difficulty_index); mode_control.select(mode_index); label_control.text = label_value
	target.call("_refresh_draft_readout")

func _fixture_source(gateway: RefCounted) -> String:
	var root := OS.get_temp_dir().path_join("scrubbots_lfx_011_owner_fixture"); _remove_tree(root); DirAccess.make_dir_recursive_absolute(root)
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var path := root.path_join("owner-source.png"); image.save_png(path)
	var imported: Dictionary = gateway.call("run_owner_import", path)
	return str(imported.get("source_id", ""))

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx011-reproduce")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-reproductions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); instance.queue_free(); _finish()

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
