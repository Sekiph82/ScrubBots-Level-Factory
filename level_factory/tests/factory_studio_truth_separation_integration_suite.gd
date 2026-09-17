extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-010-truth-separation-test"
const SEED_A := "77"
const SEED_B := "78"
const PRESENTATION_LABEL := "draft-label-only"

var failures: Array[String] = []
var test_output_absolute := ""


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	test_output_absolute = ProjectSettings.globalize_path(TEST_OUTPUT_PATH)
	_remove_tree(test_output_absolute)
	var packed_scene := ResourceLoader.call("load", MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		_finish()
		return
	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		_finish()
		return
	root.add_child(instance)
	await process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(navigation != null and workspace != null, "Studio navigation/workspace did not instantiate")
	if navigation == null or workspace == null:
		instance.queue_free()
		_finish()
		return
	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	_check(target != null and target.visible, "Generate target controls are not visible")
	if target == null:
		instance.queue_free()
		_finish()
		return
	var gateway: RefCounted = instance.get("core_gateway")
	_check(gateway != null and gateway.call("status_name") == "AVAILABLE", "Canonical Python Core gateway is not available")
	if gateway == null or gateway.call("status_name") != "AVAILABLE":
		instance.queue_free()
		_finish()
		return
	gateway.call("set_output_root", TEST_OUTPUT_PATH)

	var difficulty := target.get_node_or_null("DifficultyRow/Difficulty") as OptionButton
	var width := target.get_node_or_null("WidthRow/Width") as SpinBox
	var height := target.get_node_or_null("HeightRow/Height") as SpinBox
	var seed := target.get_node_or_null("SeedRow/Seed") as LineEdit
	var mode := target.get_node_or_null("ModeRow/Mode") as OptionButton
	var candidate_label := target.get_node_or_null("CandidatepresentationlabelRow/CandidatePresentation") as LineEdit
	var generate_button := target.get_node_or_null("ActionArea/GenerateAction") as Button
	var reproduce_button := target.get_node_or_null("ActionArea/ReproduceAction") as Button
	var validate_button := target.get_node_or_null("ActionArea/ValidateAction") as Button
	var preview := target.get_node_or_null("ActionArea/CanonicalArtworkPreview")
	var evidence := target.get_node_or_null("ActionArea/CanonicalEvidencePanel")
	var editor := target.get_node_or_null("ActionArea/CanonicalArtEditor")
	var revalidation := target.get_node_or_null("ActionArea/ManualArtStructuralRevalidation")
	_check(difficulty != null and width != null and height != null and seed != null and mode != null and candidate_label != null, "Draft controls are incomplete")
	_check(generate_button != null and reproduce_button != null and validate_button != null, "Action controls are incomplete")
	_check(preview != null and evidence != null and editor != null and revalidation != null, "Truth-domain components are incomplete")
	if difficulty == null or width == null or height == null or seed == null or mode == null or candidate_label == null or generate_button == null or reproduce_button == null or validate_button == null or preview == null or evidence == null or editor == null or revalidation == null:
		instance.queue_free()
		_finish()
		return

	_set_draft(difficulty, width, height, seed, mode, candidate_label, SEED_A, PRESENTATION_LABEL)
	await process_frame
	# Candidate A
	generate_button.pressed.emit()
	await process_frame
	var action_a: Dictionary = target.call("action_result_snapshot")
	_check(action_a.get("action") == "Generate" and action_a.get("state") == "SUCCESS", "Candidate A Generate did not succeed through the real canonical bridge")
	_check(str(action_a.get("candidate_id", "")) != PRESENTATION_LABEL, "Candidate presentation label became canonical candidate A identity")
	_check(PRESENTATION_LABEL not in str(action_a.get("captured_output", "")), "Candidate presentation label crossed the Core process boundary for A")
	var last_success_a: Dictionary = target.call("last_successful_core_evidence_snapshot")
	var preview_a: Dictionary = preview.call("snapshot")
	var evidence_a: Dictionary = evidence.call("snapshot")
	_check(preview_a.get("state") == "READY" and evidence_a.get("state") == "READY", "Canonical A preview/evidence did not become READY")
	_check(preview_a.get("candidate_id") == action_a.get("candidate_id"), "Canonical A preview identity disagrees with action A")
	_check(evidence_a.get("candidate_id") == action_a.get("candidate_id"), "Canonical A evidence identity disagrees with action A")
	_check(preview_a.get("source_bundle_path") == evidence_a.get("source_bundle_path"), "Canonical A preview/evidence bundle identities diverge")
	_check(preview_a.get("source_bundle_path") == action_a.get("output_path"), "Canonical A preview did not use the successful action bundle")

	_check(bool(editor.call("load_current_canonical_artwork")), "Explicit load of canonical A failed")
	var editor_a_clean: Dictionary = editor.call("snapshot")
	_check(editor_a_clean.get("state") == "CLEAN", "Canonical A editor source did not start CLEAN")
	_check(editor_a_clean.get("source_candidate_id") == action_a.get("candidate_id"), "Editor source was not bound to canonical A")
	var source_a_bundle := str(editor_a_clean.get("source_bundle_path", ""))
	var source_a_bytes := _bundle_bytes(source_a_bundle)
	var source_a_image: Image = editor.call("source_image_snapshot")
	_check(source_a_image != null, "Editor did not expose canonical A source image")
	var source_a_color := str(editor.call("canonical_color_id_for_pixel", source_a_image.get_pixel(0, 0))) if source_a_image != null else ""
	var paint_color := "C16" if source_a_color != "C16" else "C15"
	_check(bool(editor.call("select_color", paint_color)), "Canonical paint color was not accepted")
	_check(bool(editor.call("paint_cell", 0, 0, paint_color)), "Canonical A editor cell did not become DIRTY")
	var editor_a_dirty: Dictionary = editor.call("snapshot")
	var dirty_a_cells: Array = editor.call("working_logical_cells_snapshot")
	_check(editor_a_dirty.get("state") == "DIRTY" and editor_a_dirty.get("dirty_cell_count") == 1, "Canonical A editor did not expose exact DIRTY state")
	_check(editor_a_dirty.get("validation_disposition") == "UNVALIDATED — revalidation pending SB-LF06-008", "DIRTY editor did not remain UNVALIDATED")

	# Draft-only mutation
	var action_before_draft: Dictionary = target.call("action_result_snapshot")
	var preview_before_draft: Dictionary = preview.call("snapshot")
	var evidence_before_draft: Dictionary = evidence.call("snapshot")
	var editor_source_before_draft: Dictionary = editor.call("snapshot")
	_set_draft(difficulty, width, height, seed, mode, candidate_label, SEED_B, "changed-draft-label")
	await process_frame
	_check(target.call("action_result_snapshot") == action_before_draft, "Draft-only mutation changed latest action truth")
	_check(target.call("last_successful_core_evidence_snapshot") == last_success_a, "Draft-only mutation changed retained successful Core evidence")
	_check(preview.call("snapshot") == preview_before_draft, "Draft-only mutation changed canonical preview")
	_check(evidence.call("snapshot") == evidence_before_draft, "Draft-only mutation changed canonical evidence")
	var editor_after_draft: Dictionary = editor.call("snapshot")
	_check(editor_after_draft.get("source_candidate_id") == editor_source_before_draft.get("source_candidate_id"), "Draft-only mutation changed editor source candidate")
	_check(editor_after_draft.get("source_bundle_path") == editor_source_before_draft.get("source_bundle_path"), "Draft-only mutation changed editor source bundle")
	_check(editor.call("working_logical_cells_snapshot") == dirty_a_cells and editor_after_draft.get("dirty_cell_count") == 1, "Draft-only mutation changed DIRTY A working truth")

	# Candidate B while editor A is DIRTY
	generate_button.pressed.emit()
	await process_frame
	var action_b: Dictionary = target.call("action_result_snapshot")
	_check(action_b.get("action") == "Generate" and action_b.get("state") == "SUCCESS", "Candidate B Generate did not succeed through the real canonical bridge")
	_check(action_b.get("candidate_id") != action_a.get("candidate_id") or action_b.get("grid_hash") != action_a.get("grid_hash"), "Candidate B is not distinguishable from candidate A")
	_check(str(action_b.get("candidate_id", "")) != "changed-draft-label", "Draft presentation label became canonical candidate B identity")
	var preview_b: Dictionary = preview.call("snapshot")
	var evidence_b: Dictionary = evidence.call("snapshot")
	_check(preview_b.get("state") == "READY" and evidence_b.get("state") == "READY", "Canonical B preview/evidence did not become READY")
	_check(preview_b.get("candidate_id") == action_b.get("candidate_id"), "Canonical B preview identity disagrees with action B")
	_check(evidence_b.get("candidate_id") == action_b.get("candidate_id"), "Canonical B evidence identity disagrees with action B")
	_check(preview_b.get("source_bundle_path") == evidence_b.get("source_bundle_path") and preview_b.get("source_bundle_path") == action_b.get("output_path"), "Canonical B preview/evidence do not share the successful action bundle")
	_check(preview_b.get("artwork_path") == str(action_b.get("output_path")).path_join("artwork.png"), "Canonical B preview did not use artwork.png")
	_check(evidence_b.get("metadata_path") == str(action_b.get("output_path")).path_join("metadata.json"), "Canonical B evidence did not use metadata.json")
	_check(PRESENTATION_LABEL not in str(action_b.get("captured_output", "")), "Candidate presentation label crossed the Core process boundary for B")
	var editor_after_b: Dictionary = editor.call("snapshot")
	_check(editor_after_b.get("state") == "DIRTY", "Successful B silently replaced DIRTY editor A")
	_check(editor_after_b.get("source_candidate_id") == editor_a_dirty.get("source_candidate_id") and editor_after_b.get("source_bundle_path") == source_a_bundle, "Successful B changed editor A source identity")
	_check(editor_after_b.get("dirty_cell_count") == 1 and editor.call("working_logical_cells_snapshot") == dirty_a_cells, "Successful B changed editor A working pixels or dirty count")
	_check(editor_after_b.get("latest_successful_candidate_id") == action_b.get("candidate_id"), "Editor did not expose B as separate latest-successful identity")
	_check(_bundle_bytes(source_a_bundle) == source_a_bytes, "Successful B changed canonical A source bundle bytes")

	# Revalidate DIRTY A after B exists
	var revalidate_button := revalidation.get_node_or_null("RevalidateManualArtwork") as Button
	_check(revalidate_button != null and not revalidate_button.disabled, "Manual A revalidation was not available after B while A remained DIRTY")
	if revalidate_button != null:
		revalidate_button.pressed.emit()
		await process_frame
	var revalidation_a: Dictionary = revalidation.call("snapshot")
	_check(revalidation_a.get("state") in ["STRUCTURAL ACCEPT", "STRUCTURAL REJECT"], "Manual A revalidation did not produce structural evidence after B")
	_check(revalidation_a.get("result_current") == true, "Manual A revalidation result was not current")
	_check(revalidation_a.get("source_candidate_id") == editor_a_dirty.get("source_candidate_id"), "Manual revalidation bound to B instead of editor source A")
	_check(int(revalidation_a.get("dirty_cell_count", 0)) == 1, "Manual A revalidation did not bind exact DIRTY count")
	_check(str(revalidation_a.get("working_grid_hash", "")).length() == 64, "Manual A revalidation did not expose canonical working-grid hash")
	_check(revalidation_a.get("source_bytes_unchanged") == true, "Manual A revalidation did not prove source bytes unchanged")
	_check(preview.call("snapshot").get("source_bundle_path") == action_b.get("output_path"), "Manual A revalidation changed canonical B preview")
	_check(evidence.call("snapshot").get("source_bundle_path") == action_b.get("output_path"), "Manual A revalidation changed canonical B evidence")

	# Reproduce / action retention
	reproduce_button.pressed.emit()
	await process_frame
	var reproduced: Dictionary = target.call("action_result_snapshot")
	_check(reproduced.get("action") == "Reproduce" and reproduced.get("state") == "SUCCESS", "Canonical B Reproduce did not succeed")
	var preview_reproduced: Dictionary = preview.call("snapshot")
	var evidence_reproduced: Dictionary = evidence.call("snapshot")
	_check(preview_reproduced.get("source_action") == "Reproduce" and evidence_reproduced.get("source_action") == "Reproduce", "Reproduce did not move preview/evidence together")
	_check(preview_reproduced.get("source_bundle_path") == evidence_reproduced.get("source_bundle_path") and preview_reproduced.get("source_bundle_path") == reproduced.get("output_path"), "Reproduce preview/evidence bundle identities diverged")
	_check(preview_reproduced.get("candidate_id") == reproduced.get("candidate_id") and evidence_reproduced.get("candidate_id") == reproduced.get("candidate_id"), "Reproduce canonical identity disagreed across surfaces")
	var editor_after_reproduce: Dictionary = editor.call("snapshot")
	_check(editor_after_reproduce.get("state") == "DIRTY" and editor_after_reproduce.get("source_bundle_path") == source_a_bundle, "Reproduce silently replaced DIRTY editor A")
	_check(editor_after_reproduce.get("latest_successful_output_path") == reproduced.get("output_path"), "Editor did not expose Reproduce as separate latest success")
	var revalidation_after_reproduce: Dictionary = revalidation.call("snapshot")
	_check(revalidation_after_reproduce.get("source_candidate_id") == editor_a_dirty.get("source_candidate_id"), "Reproduce relabeled manual A revalidation source")

	_check(validate_button.disabled and "UNAVAILABLE" in validate_button.tooltip_text, "Validate did not remain visibly unavailable")
	target.call("_on_action_pressed", "Validate")
	await process_frame
	var unavailable: Dictionary = target.call("action_result_snapshot")
	_check(unavailable.get("action") == "Validate" and unavailable.get("state") == "UNAVAILABLE", "Validate did not remain a truthful unavailable action attempt")
	var retained_success: Dictionary = target.call("last_successful_core_evidence_snapshot")
	_check(retained_success.get("action") == "Reproduce" and retained_success.get("output_path") == reproduced.get("output_path"), "Unavailable Validate erased retained Reproduce evidence")
	var preview_after_unavailable: Dictionary = preview.call("snapshot")
	var evidence_after_unavailable: Dictionary = evidence.call("snapshot")
	_check(preview_after_unavailable.get("retained_after_failure") == true and preview_after_unavailable.get("source_bundle_path") == reproduced.get("output_path"), "Unavailable Validate changed retained canonical preview")
	_check(evidence_after_unavailable.get("retained_after_failure") == true and evidence_after_unavailable.get("source_bundle_path") == reproduced.get("output_path"), "Unavailable Validate changed retained canonical evidence")
	var editor_after_unavailable: Dictionary = editor.call("snapshot")
	_check(editor_after_unavailable.get("state") == "DIRTY" and editor_after_unavailable.get("source_bundle_path") == source_a_bundle and editor_after_unavailable.get("dirty_cell_count") == 1, "Unavailable Validate changed DIRTY editor A")
	var revalidation_after_unavailable: Dictionary = revalidation.call("snapshot")
	_check(revalidation_after_unavailable.get("source_candidate_id") == editor_a_dirty.get("source_candidate_id"), "Unavailable Validate rewrote manual A revalidation truth")

	# Explicit replacement boundary
	_check(bool(editor.call("load_current_canonical_artwork", true)), "Explicit replacement with latest canonical Reproduce failed")
	await process_frame
	var replaced: Dictionary = editor.call("snapshot")
	_check(replaced.get("source_action") == "Reproduce" and replaced.get("source_bundle_path") == reproduced.get("output_path"), "Editor source did not move to current canonical B only at explicit replacement")
	_check(replaced.get("state") == "CLEAN" and replaced.get("dirty_cell_count") == 0, "Explicit replacement did not make the editor CLEAN")
	_check(replaced.get("working_buffer_differs") == false, "Explicit replacement left a differing working buffer")
	var revalidation_after_replace: Dictionary = revalidation.call("snapshot")
	_check(revalidation_after_replace.get("state") == "NOT_REQUIRED" and revalidation_after_replace.get("result_current") == false, "Explicit replacement did not clear manual revalidation to NOT_REQUIRED")
	_check(_bundle_bytes(source_a_bundle) == source_a_bytes, "Explicit replacement mutated canonical A source bundle bytes")

	instance.queue_free()
	_finish()


func _set_draft(difficulty: OptionButton, width: SpinBox, height: SpinBox, seed: LineEdit, mode: OptionButton, label: LineEdit, seed_value: String, label_value: String) -> void:
	difficulty.select(0)
	difficulty.item_selected.emit(0)
	width.value = 20
	height.value = 21
	seed.text = seed_value
	seed.text_changed.emit(seed_value)
	mode.select(1)
	mode.item_selected.emit(1)
	label.text = label_value
	label.text_changed.emit(label_value)


func _bundle_bytes(bundle_path: String) -> Dictionary:
	var bytes := {}
	for file_name in ["artwork.png", "artwork.json", "metadata.json"]:
		bytes[file_name] = FileAccess.get_file_as_bytes(bundle_path.path_join(file_name))
	return bytes


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)


func _finish() -> void:
	_remove_tree(test_output_absolute)
	if failures.is_empty():
		print("SB-LF06-010-C001 editor presentation/truth separation integration PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _remove_tree(path: String) -> void:
	var directory := DirAccess.open(path)
	if directory == null:
		return
	directory.list_dir_begin()
	var entry := directory.get_next()
	while not entry.is_empty():
		if entry != "." and entry != "..":
			var child_path := path.path_join(entry)
			if directory.current_is_dir():
				_remove_tree(child_path)
			else:
				DirAccess.remove_absolute(child_path)
		entry = directory.get_next()
	directory.list_dir_end()
	DirAccess.remove_absolute(path)
