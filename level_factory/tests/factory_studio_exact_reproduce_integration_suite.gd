extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-011-exact-reproduce-test"
const SOURCE_SEED_A := "77"
const SOURCE_SEED_B := "78"
const A_PRESENTATION_LABEL := "source-a-presentation-only"
const CHANGED_DRAFT_LABEL := "changed-draft-presentation-only"
const B_CHANGED_DRAFT_LABEL := "changed-b-draft-presentation-only"
const ARTIFACT_NAMES := ["metadata.json", "artwork.json", "artwork.png", "artwork.preview.png"]

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
	var gateway: RefCounted = instance.get("core_gateway")
	_check(target != null and target.visible, "Generate target controls are not visible")
	_check(gateway != null and gateway.call("status_name") == "AVAILABLE", "Canonical Python Core gateway is not available")
	if target == null or gateway == null or gateway.call("status_name") != "AVAILABLE":
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
	_check(difficulty != null and width != null and height != null and seed != null and mode != null and candidate_label != null, "Reproduce draft controls are incomplete")
	_check(generate_button != null and reproduce_button != null and validate_button != null, "Reproduce action controls are incomplete")
	if difficulty == null or width == null or height == null or seed == null or mode == null or candidate_label == null or generate_button == null or reproduce_button == null or validate_button == null:
		instance.queue_free()
		_finish()
		return

	# Reproduce unavailable before a successful canonical source exists.
	_check(reproduce_button.disabled, "Reproduce was enabled before a successful metadata source existed")
	_check("UNAVAILABLE" in reproduce_button.tooltip_text, "Pre-source Reproduce did not expose truthful UNAVAILABLE reason")
	var pre_source_reproduce: Dictionary = gateway.call("run_action", "Reproduce", {"seed": SOURCE_SEED_A}, TEST_OUTPUT_PATH)
	_check(pre_source_reproduce.get("state") == "UNAVAILABLE", "Pre-source Reproduce did not remain unavailable")

	# Source A
	_set_draft(difficulty, width, height, seed, mode, candidate_label, 1, 20, 21, SOURCE_SEED_A, 1, A_PRESENTATION_LABEL)
	await process_frame
	generate_button.pressed.emit()
	await process_frame
	var generated_a: Dictionary = target.call("action_result_snapshot")
	_check(generated_a.get("action") == "Generate" and generated_a.get("state") == "SUCCESS", "Canonical source A Generate did not succeed")
	_check(generated_a.get("exit_code") == 0, "Canonical source A Generate did not exit successfully")
	_check(str(generated_a.get("candidate_id", "")) != A_PRESENTATION_LABEL, "Source A presentation label became candidate identity")
	_check(A_PRESENTATION_LABEL not in str(generated_a.get("captured_output", "")), "Source A presentation label crossed the Core boundary")
	var source_a_metadata_path := str(generated_a.get("metadata_path", ""))
	var source_a_bundle_path := str(generated_a.get("output_path", ""))
	_check(source_a_metadata_path.ends_with("metadata.json"), "Source A did not expose metadata.json")
	var source_a_metadata: Dictionary = _read_metadata(source_a_metadata_path)
	var source_a_request: Dictionary = _generation_request(source_a_metadata)
	_check(source_a_request.get("schema") == "scrubbots-generation-request", "Source A request schema was not canonical")
	_check(int(source_a_request.get("schema_version", 0)) in [1, 2], "Source A request schema version was not canonical")
	_check(source_a_request.get("seed") is Dictionary, "Source A request did not preserve typed seed")
	_check(source_a_request.get("seed", {}).get("type") == "int" and source_a_request.get("seed", {}).get("value") == 77, "Source A typed seed was not recorded canonically")
	_check(source_a_request.get("difficulty") == "MEDIUM", "Source A recorded difficulty did not match the configured request")
	_check(source_a_request.get("width") == 20 and source_a_request.get("height") == 21, "Source A recorded rectangular dimensions did not match the configured request")
	_check(source_a_request.get("generator_mode") == "RULES", "Source A recorded mode did not match the configured request")
	var source_a_bytes := _artifact_bytes(source_a_bundle_path)
	_check(gateway.call("last_successful_metadata_path") == source_a_metadata_path, "Gateway did not retain source A metadata path")
	_check(not reproduce_button.disabled, "Reproduce did not become available after successful source A")

	# Draft divergence before reproducing A.
	_set_draft(difficulty, width, height, seed, mode, candidate_label, 2, 23, 24, "draft-changed-seed", 4, CHANGED_DRAFT_LABEL)
	await process_frame
	_check(gateway.call("last_successful_metadata_path") == source_a_metadata_path, "Draft-only mutation changed retained source A metadata path")
	_check(str(target.call("action_result_snapshot").get("candidate_id", "")) == str(generated_a.get("candidate_id", "")), "Draft-only mutation changed latest action identity")

	# Reproduce source A from retained metadata, not current draft.
	reproduce_button.pressed.emit()
	await process_frame
	var reproduced_a: Dictionary = target.call("action_result_snapshot")
	_check(reproduced_a.get("action") == "Reproduce" and reproduced_a.get("state") == "SUCCESS", "Studio Reproduce A did not succeed")
	_check(reproduced_a.get("disposition") == "MATCH", "Studio Reproduce A did not return canonical MATCH")
	_check(reproduced_a.get("candidate_id") == generated_a.get("candidate_id"), "Reproduce A candidate identity differs from source A")
	_check(reproduced_a.get("grid_hash") == generated_a.get("grid_hash"), "Reproduce A grid hash differs from source A")
	_check(reproduced_a.get("selected_seed") == generated_a.get("selected_seed"), "Reproduce A selected typed seed differs from source A")
	_check(reproduced_a.get("mode") == generated_a.get("mode") and reproduced_a.get("dimensions") == generated_a.get("dimensions"), "Reproduce A mode/dimensions differ from source A")
	_check(str(reproduced_a.get("output_path", "")) != source_a_bundle_path, "Reproduce A overwrote the source A bundle")
	var reproduced_a_metadata: Dictionary = _read_metadata(str(reproduced_a.get("metadata_path", "")))
	_check(_generation_request(reproduced_a_metadata) == source_a_request, "Reproduce A metadata generation.request differs from source A")
	_check(_artifact_bytes(str(reproduced_a.get("output_path", ""))) == source_a_bytes, "Reproduce A canonical artifact bytes differ from source A")
	_check(_artifact_bytes(source_a_bundle_path) == source_a_bytes, "Reproduce A mutated source A canonical artifact bytes")
	_check(CHANGED_DRAFT_LABEL not in str(reproduced_a.get("captured_output", "")), "Changed draft presentation label crossed Reproduce boundary")
	_check(str(reproduced_a.get("candidate_id", "")) != CHANGED_DRAFT_LABEL, "Changed draft presentation label became Reproduce A identity")

	# Source B transition
	_set_draft(difficulty, width, height, seed, mode, candidate_label, 2, 22, 20, SOURCE_SEED_B, 4, "source-b-presentation-only")
	await process_frame
	generate_button.pressed.emit()
	await process_frame
	var generated_b: Dictionary = target.call("action_result_snapshot")
	_check(generated_b.get("action") == "Generate" and generated_b.get("state") == "SUCCESS", "Canonical source B Generate did not succeed")
	_check(generated_b.get("candidate_id") != generated_a.get("candidate_id") or generated_b.get("grid_hash") != generated_a.get("grid_hash"), "Source B was not distinguishable from source A")
	var source_b_metadata_path := str(generated_b.get("metadata_path", ""))
	var source_b_bundle_path := str(generated_b.get("output_path", ""))
	var source_b_metadata: Dictionary = _read_metadata(source_b_metadata_path)
	var source_b_request: Dictionary = _generation_request(source_b_metadata)
	var source_b_bytes := _artifact_bytes(source_b_bundle_path)
	_check(gateway.call("last_successful_metadata_path") == source_b_metadata_path, "Gateway did not transition retained source metadata from A to B")
	_check(source_b_request.get("seed", {}).get("value") == 78, "Source B recorded seed was not the canonical B seed")

	# Draft divergence after B and exact B reproduction.
	_set_draft(difficulty, width, height, seed, mode, candidate_label, 3, 25, 26, "another-draft-seed", 3, B_CHANGED_DRAFT_LABEL)
	await process_frame
	_check(gateway.call("last_successful_metadata_path") == source_b_metadata_path, "Draft-only mutation redirected retained source B metadata path")
	reproduce_button.pressed.emit()
	await process_frame
	var reproduced_b: Dictionary = target.call("action_result_snapshot")
	_check(reproduced_b.get("action") == "Reproduce" and reproduced_b.get("state") == "SUCCESS" and reproduced_b.get("disposition") == "MATCH", "Studio Reproduce B did not return canonical MATCH")
	_check(reproduced_b.get("candidate_id") == generated_b.get("candidate_id") and reproduced_b.get("grid_hash") == generated_b.get("grid_hash"), "Reproduce B identity differs from source B")
	_check(reproduced_b.get("selected_seed") == generated_b.get("selected_seed") and reproduced_b.get("mode") == generated_b.get("mode") and reproduced_b.get("dimensions") == generated_b.get("dimensions"), "Reproduce B did not use source B typed seed/config")
	_check(_generation_request(_read_metadata(str(reproduced_b.get("metadata_path", "")))) == source_b_request, "Reproduce B metadata generation.request differs from source B")
	_check(_artifact_bytes(str(reproduced_b.get("output_path", ""))) == source_b_bytes, "Reproduce B canonical artifact bytes differ from source B")
	_check(_artifact_bytes(source_b_bundle_path) == source_b_bytes, "Reproduce B mutated source B canonical artifact bytes")
	_check(B_CHANGED_DRAFT_LABEL not in str(reproduced_b.get("captured_output", "")), "Changed B draft presentation label crossed Reproduce boundary")

	# Unavailable action retention and subsequent reproduction source.
	_check(validate_button.disabled and "UNAVAILABLE" in validate_button.tooltip_text, "Validate did not remain truthfully unavailable")
	target.call("_on_action_pressed", "Validate")
	await process_frame
	var unavailable: Dictionary = target.call("action_result_snapshot")
	_check(unavailable.get("action") == "Validate" and unavailable.get("state") == "UNAVAILABLE", "Validate did not remain an unavailable action attempt")
	_check(gateway.call("last_successful_metadata_path") == source_b_metadata_path, "Unavailable Validate redirected retained source B metadata")
	reproduce_button.pressed.emit()
	await process_frame
	var reproduced_b_after_unavailable: Dictionary = target.call("action_result_snapshot")
	_check(reproduced_b_after_unavailable.get("action") == "Reproduce" and reproduced_b_after_unavailable.get("state") == "SUCCESS" and reproduced_b_after_unavailable.get("disposition") == "MATCH", "Reproduce after unavailable Validate did not still MATCH source B")
	_check(reproduced_b_after_unavailable.get("candidate_id") == generated_b.get("candidate_id") and reproduced_b_after_unavailable.get("grid_hash") == generated_b.get("grid_hash"), "Unavailable Validate redirected subsequent Reproduce identity")
	_check(_artifact_bytes(str(reproduced_b_after_unavailable.get("output_path", ""))) == source_b_bytes, "Reproduce after unavailable Validate changed canonical B artifact bytes")

	instance.queue_free()
	_finish()


func _set_draft(difficulty: OptionButton, width: SpinBox, height: SpinBox, seed: LineEdit, mode: OptionButton, label: LineEdit, difficulty_index: int, width_value: int, height_value: int, seed_value: String, mode_index: int, label_value: String) -> void:
	difficulty.select(difficulty_index)
	difficulty.item_selected.emit(difficulty_index)
	width.value = width_value
	height.value = height_value
	seed.text = seed_value
	seed.text_changed.emit(seed_value)
	mode.select(mode_index)
	mode.item_selected.emit(mode_index)
	label.text = label_value
	label.text_changed.emit(label_value)


func _read_metadata(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


func _generation_request(metadata: Dictionary) -> Dictionary:
	var generation: Variant = metadata.get("generation", {})
	return generation.get("request", {}) if generation is Dictionary else {}


func _artifact_bytes(bundle_path: String) -> Dictionary:
	var result := {}
	for file_name in ARTIFACT_NAMES:
		var path := bundle_path.path_join(file_name)
		result[file_name] = {"exists": FileAccess.file_exists(path), "bytes": FileAccess.get_file_as_bytes(path)}
	return result


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)


func _finish() -> void:
	_remove_tree(test_output_absolute)
	if failures.is_empty():
		print("SB-LF06-011-C001 exact recorded seed/config reproduction integration PASS")
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
