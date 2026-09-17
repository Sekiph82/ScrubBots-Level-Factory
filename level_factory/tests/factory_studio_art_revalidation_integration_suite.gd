extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-008-revalidation-test"
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	_remove_tree(ProjectSettings.globalize_path(TEST_OUTPUT_PATH))
	for script_path in [
		"res://scripts/factory_core_gateway.gd",
		"res://scripts/factory_studio_art_editor.gd",
		"res://scripts/factory_studio_art_revalidation.gd",
		"res://tests/factory_studio_art_revalidation_integration_suite.gd",
	]:
		_check(ResourceLoader.call(SCENE_LOADER_METHOD, script_path) as Script != null, "LF06-008 script did not load: %s" % script_path)
	var packed_scene := ResourceLoader.call(SCENE_LOADER_METHOD, MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load for LF06-008")
	if packed_scene == null:
		_finish()
		return
	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate for LF06-008")
	if instance == null:
		_finish()
		return
	root.add_child(instance)
	await process_frame
	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(navigation != null and workspace != null, "LF06-008 Studio navigation/workspace did not instantiate")
	if navigation == null or workspace == null:
		instance.queue_free()
		_finish()
		return
	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	var gateway: RefCounted = instance.get("core_gateway")
	_check(target != null and target.visible, "LF06-008 Generate target surface is unavailable")
	_check(gateway != null and gateway.call("status_name") == "AVAILABLE", "LF06-008 canonical Core gateway is unavailable")
	if target == null or gateway == null:
		instance.queue_free()
		_finish()
		return
	gateway.call("set_output_root", TEST_OUTPUT_PATH)
	var width := target.get_node_or_null("WidthRow/Width") as SpinBox
	var height := target.get_node_or_null("HeightRow/Height") as SpinBox
	var seed := target.get_node_or_null("SeedRow/Seed") as LineEdit
	var generate_button := target.get_node_or_null("ActionArea/GenerateAction") as Button
	_check(width != null and height != null and seed != null and generate_button != null, "LF06-008 Generate controls are incomplete")
	if width == null or height == null or seed == null or generate_button == null:
		instance.queue_free()
		_finish()
		return
	width.value = 20
	height.value = 21
	seed.text = "lf06-008-revalidation"
	seed.text_changed.emit(seed.text)
	await process_frame
	generate_button.pressed.emit()
	await process_frame
	var generated: Dictionary = target.call("action_result_snapshot")
	_check(generated.get("state") == "SUCCESS", "LF06-008 could not generate a real canonical source bundle")
	if generated.get("state") != "SUCCESS":
		instance.queue_free()
		_finish()
		return
	var editor := target.get_node_or_null("ActionArea/CanonicalArtEditor")
	var revalidation := target.get_node_or_null("ActionArea/ManualArtStructuralRevalidation")
	var preview := target.get_node_or_null("ActionArea/CanonicalArtworkPreview")
	var evidence := target.get_node_or_null("ActionArea/CanonicalEvidencePanel")
	var puzzle_config_gate := target.get_node_or_null("ApprovedPuzzleConfigGate")
	var validate_button := target.get_node_or_null("ActionArea/ValidateAction") as Button
	_check(editor != null and revalidation != null and preview != null and evidence != null, "LF06-008 Studio components are incomplete")
	_check(puzzle_config_gate != null and puzzle_config_gate.call("snapshot").get("state") == "UNAVAILABLE", "LF06-007 puzzle-config gate lost its truthful UNAVAILABLE state")
	_check(validate_button != null and validate_button.disabled, "LF06-003 Validate action became available during LF06-008")
	if editor == null or revalidation == null or preview == null or evidence == null:
		instance.queue_free()
		_finish()
		return
	_check(bool(editor.call("load_current_canonical_artwork")), "LF06-008 could not load the real canonical artwork into the editor")
	await process_frame
	var clean_revalidation: Dictionary = revalidation.call("snapshot")
	_check(clean_revalidation.get("state") == "NOT_REQUIRED", "CLEAN editor was presented as an available manual revalidation")
	_check(not bool(clean_revalidation.get("result_current", true)), "CLEAN editor retained a current revalidation result")
	var revalidate_button := revalidation.get_node_or_null("RevalidateManualArtwork") as Button
	_check(revalidate_button != null and revalidate_button.disabled, "CLEAN editor exposed an enabled revalidation action")
	var source_snapshot: Dictionary = editor.call("snapshot")
	var source_bundle_path := str(source_snapshot.get("source_bundle_path", ""))
	var source_files_before := _source_files(source_bundle_path)
	_check(source_files_before.size() == 3, "LF06-008 could not capture artwork.json, metadata.json and artwork.png before revalidation")
	var preview_before: Dictionary = preview.call("snapshot")
	var evidence_before: Dictionary = evidence.call("snapshot")
	var source_image: Image = editor.call("source_image_snapshot")
	_check(source_image != null, "LF06-008 source image is missing")
	var original_color := str(editor.call("canonical_color_id_for_pixel", source_image.get_pixel(0, 0))) if source_image != null else ""
	var edit_color := _different_color(original_color)
	_check(bool(editor.call("select_color", edit_color)), "LF06-008 could not select a canonical edit color")
	_check(bool(editor.call("paint_cell", 0, 0, edit_color)), "LF06-008 could not make a real C01..C16 edit")
	await process_frame
	var dirty_snapshot: Dictionary = editor.call("snapshot")
	_check(dirty_snapshot.get("state") == "DIRTY" and int(dirty_snapshot.get("dirty_cell_count", 0)) == 1, "LF06-008 edit did not produce exact DIRTY evidence")
	var available_revalidation: Dictionary = revalidation.call("snapshot")
	_check(available_revalidation.get("state") == "AVAILABLE", "DIRTY editor did not expose manual structural revalidation")
	_check(revalidate_button != null and not revalidate_button.disabled, "DIRTY editor did not enable revalidation")
	revalidate_button.pressed.emit()
	await process_frame
	var first_result: Dictionary = revalidation.call("snapshot")
	_check(first_result.get("state") in ["STRUCTURAL ACCEPT", "STRUCTURAL REJECT"], "Real canonical revalidation did not return a structural result")
	_check(first_result.get("scope") == "STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION", "Revalidation scope was not explicitly limited")
	_check(first_result.get("source_candidate_id") == source_snapshot.get("source_candidate_id"), "Revalidation source candidate identity drifted")
	_check(str(first_result.get("source_grid_hash", "")).length() == 64 and str(first_result.get("working_grid_hash", "")).length() == 64, "Revalidation did not return canonical source/working hashes")
	_check(first_result.get("quality_schema") == "scrubbots-quality" and int(first_result.get("quality_schema_version", 0)) == 1, "Revalidation did not return canonical quality schema/version")
	_check(not str(first_result.get("quality_policy_version", "")).is_empty(), "Revalidation did not expose the exact source quality policy identity")
	_check(first_result.get("result_current") == true, "Structural result was not marked current")
	_check(editor.call("snapshot").get("state") == "DIRTY", "Revalidation cleared the editor DIRTY state")
	_check(first_result.get("source_bytes_unchanged") == true, "Revalidation did not prove source bytes remained unchanged")
	_check(_source_files(source_bundle_path) == source_files_before, "Revalidation changed canonical source bundle bytes")
	_check(preview.call("snapshot").get("artwork_path") == preview_before.get("artwork_path"), "Revalidation changed canonical preview identity")
	_check(evidence.call("snapshot").get("metadata_path") == evidence_before.get("metadata_path"), "Revalidation changed canonical evidence identity")
	_check(not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path("res://output/.lf06-008-revalidation")), "Transient revalidation request directory was not removed")
	_check(str(first_result.get("disposition", "")) == "ACCEPT" or not first_result.get("rejection_codes", []).is_empty(), "Structural REJECT did not carry canonical rejection codes")

	var second_original := str(editor.call("canonical_color_id_for_pixel", source_image.get_pixel(1, 0))) if source_image != null else ""
	var second_color := _different_color(second_original)
	editor.call("paint_cell", 1, 0, second_color)
	await process_frame
	var stale: Dictionary = revalidation.call("snapshot")
	_check(stale.get("state") == "STALE", "Editing after a structural result did not make the result STALE")
	_check(not bool(stale.get("result_current", true)), "STALE result remained current")
	_check(bool(editor.call("reset_to_source")), "LF06-008 could not reset the working copy to source")
	await process_frame
	var reset: Dictionary = revalidation.call("snapshot")
	_check(reset.get("state") == "NOT_REQUIRED" and not bool(reset.get("result_current", true)), "Reset did not remove current manual revalidation status")
	_check(editor.call("snapshot").get("dirty_cell_count") == 0, "Reset did not restore exact CLEAN editor state")

	# Deterministic deliberately bad working grid: paint every cell C01 through the real editor.
	var logical_width := int(source_snapshot.get("logical_width", 0))
	var logical_height := int(source_snapshot.get("logical_height", 0))
	for y in range(logical_height):
		for x in range(logical_width):
			editor.call("paint_cell", x, y, "C01")
	await process_frame
	var bad_dirty: Dictionary = editor.call("snapshot")
	_check(bad_dirty.get("state") == "DIRTY" and int(bad_dirty.get("dirty_cell_count", 0)) > 0, "Bad manual grid did not remain DIRTY")
	revalidate_button.pressed.emit()
	await process_frame
	var rejected: Dictionary = revalidation.call("snapshot")
	_check(rejected.get("state") == "STRUCTURAL REJECT", "Bad manual grid did not receive a real structural REJECT")
	_check(not rejected.get("rejection_codes", []).is_empty(), "Bad manual grid did not expose canonical rejection codes")
	_check(rejected.get("source_bytes_unchanged") == true and _source_files(source_bundle_path) == source_files_before, "Bad-grid revalidation changed canonical source bytes")
	_check(not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path("res://output/.lf06-008-revalidation")), "Transient bad-grid request directory was not removed")
	_check(editor.call("snapshot").get("state") == "DIRTY", "Bad-grid revalidation cleared DIRTY state")
	_check(str(rejected.get("scope", "")).contains("STRUCTURAL ART QA ONLY"), "Bad-grid result was not scope-qualified")
	editor.call("reset_to_source")
	await process_frame
	_check(revalidation.call("snapshot").get("state") == "NOT_REQUIRED", "Final source restoration did not return NOT_REQUIRED")
	_remove_tree(ProjectSettings.globalize_path(TEST_OUTPUT_PATH))
	instance.queue_free()
	_finish()


func _different_color(original: String) -> String:
	for candidate in ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16"]:
		if candidate != original:
			return candidate
	return "C01"


func _source_files(bundle_path: String) -> Dictionary:
	var result: Dictionary = {}
	for file_name in ["artwork.png", "artwork.json", "metadata.json"]:
		result[file_name] = FileAccess.get_file_as_bytes(bundle_path.path_join(file_name))
	return result if result.values().all(func(value: Variant) -> bool: return not (value as PackedByteArray).is_empty()) else {}


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	var directory := DirAccess.open(path)
	if directory == null:
		return
	directory.list_dir_begin()
	var entry := directory.get_next()
	while not entry.is_empty():
		if entry not in [".", ".."]:
			var child := path.path_join(entry)
			if directory.current_is_dir():
				_remove_tree(child)
			else:
				DirAccess.remove_absolute(child)
		entry = directory.get_next()
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		push_error(message)


func _finish() -> void:
	if failures.is_empty():
		print("SB-LF06-008-C001 manual artwork structural revalidation integration PASS")
	else:
		push_error("SB-LF06-008-C001 manual artwork structural revalidation integration FAIL: %s" % " | ".join(failures))
		_remove_tree(ProjectSettings.globalize_path(TEST_OUTPUT_PATH))
	quit(0 if failures.is_empty() else 1)
