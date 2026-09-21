extends SceneTree

const PASS_MARKER := "SB-LFX-011-C001-R03 EXACT REPRODUCE divergence integration PASS"
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
	if gateway == null or target == null or reproduce_surface == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx011-r03-reproduce")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-reproductions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads"))
	_set_draft(target, "11031", 20, 20, 0, 0, "canonical-draft")
	var generated: Dictionary = gateway.call("run_action", "Generate", target.call("draft_snapshot"), "res://output/.lfx011-r03-reproduce")
	_require(generated.get("state") == "SUCCESS", "canonical Generate fixture failed: %s" % generated)
	var candidate_id := str(generated.get("candidate_id", "")); var source_bundle := str(generated.get("output_path", "")); var source_files := _bundle_bytes(source_bundle)
	var capability: Dictionary = gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": candidate_id})
	_require(capability.get("disposition") == "EXACT_REPRODUCIBLE", "canonical fixture was not reproducible: %s" % capability)
	# Diverge the live Studio draft after the candidate exists. Exact Reproduce must not consume it.
	_set_draft(target, "changed-live-draft", 23, 24, 2, 2, "materially-different-preset")
	var divergent_draft: Dictionary = target.call("draft_snapshot")
	_require(divergent_draft.get("seed") == "changed-live-draft" and divergent_draft.get("width") == 23 and divergent_draft.get("mode") == "WFC", "live draft did not materially diverge")
	reproduce_surface.call("set_selected_identity", candidate_id); reproduce_surface.call("check_capability"); await process_frame
	_require(reproduce_surface.call("capability_button_enabled"), "Exact Reproduce was not enabled for canonical evidence")
	reproduce_surface.call("exact_reproduce"); await process_frame
	var replay_surface: Dictionary = reproduce_surface.call("snapshot")
	_require(replay_surface.get("state") == "SUCCESS" and replay_surface.get("disposition") == "MATCH", "surface Exact Reproduce did not return MATCH: %s" % replay_surface)
	_require(_bundle_bytes(source_bundle) == source_files, "canonical source bundle changed after surface replay")
	var owner_fixture := _fixture_source(gateway)
	reproduce_surface.call("set_selected_identity", owner_fixture); reproduce_surface.call("check_capability"); await process_frame
	var unsupported_surface: Dictionary = reproduce_surface.call("snapshot")
	_require(unsupported_surface.get("disposition") == "SOURCE_RETRIEVABLE_ONLY", "real durable OWNER_UPLOAD was not classified as source-only: %s" % unsupported_surface)
	_require(not reproduce_surface.call("capability_button_enabled"), "real source-only record enabled Exact Reproduce")
	_require(str(unsupported_surface.get("reason", "")).contains("not deterministic regeneration"), "source-only capability reason was not rendered")
	_cleanup(instance)

func _set_draft(target: Node, seed_value: String, width: int, height: int, difficulty_index: int, mode_index: int, label_value: String) -> void:
	var seed_control: LineEdit = target.get("seed_control"); var width_control: SpinBox = target.get("width_control"); var height_control: SpinBox = target.get("height_control")
	var difficulty_control: OptionButton = target.get("difficulty_control"); var mode_control: OptionButton = target.get("mode_control"); var label_control: LineEdit = target.get("candidate_label_control")
	seed_control.text = seed_value; width_control.value = width; height_control.value = height; difficulty_control.select(difficulty_index); mode_control.select(mode_index); label_control.text = label_value
	target.call("_refresh_draft_readout")

func _fixture_source(gateway: RefCounted) -> String:
	var root := OS.get_temp_dir().path_join("scrubbots_lfx_011_r03_owner_fixture"); _remove_tree(root); DirAccess.make_dir_recursive_absolute(root)
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var path := root.path_join("owner-source.png"); image.save_png(path)
	var imported: Dictionary = gateway.call("run_owner_import", path)
	return str(imported.get("source_id", ""))

func _bundle_bytes(bundle: String) -> Dictionary:
	return {"artwork.png": FileAccess.get_file_as_bytes(bundle.path_join("artwork.png")), "artwork.json": FileAccess.get_file_as_bytes(bundle.path_join("artwork.json")), "metadata.json": FileAccess.get_file_as_bytes(bundle.path_join("metadata.json"))}

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx011-r03-reproduce")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-reproductions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); instance.queue_free(); _finish()

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
