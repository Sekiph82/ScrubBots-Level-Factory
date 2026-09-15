extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-003-action-test"
const SEED_VALUE := "77"
const PRESENTATION_LABEL := "presentation-only-label"
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []
var test_output_absolute := ""


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	test_output_absolute = ProjectSettings.globalize_path(TEST_OUTPUT_PATH)
	_remove_tree(test_output_absolute)
	var missing_core := FactoryCoreGateway.new("definitely;missing-scrubbots-python")
	_check(missing_core.status_name() == "UNAVAILABLE", "Invalid canonical Core executable was not reported unavailable")
	var missing_result: Dictionary = missing_core.call("run_action", "Generate", {"seed": "77"})
	_check(missing_result.get("state") == "UNAVAILABLE", "Missing canonical Core did not keep Generate unavailable")
	var packed_scene := ResourceLoader.call(SCENE_LOADER_METHOD, MAIN_SCENE_PATH) as PackedScene
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
	_check(gateway != null, "Studio did not construct the canonical Core gateway")
	if gateway == null:
		instance.queue_free()
		_finish()
		return
	gateway.call("set_output_root", TEST_OUTPUT_PATH)
	_check(gateway.call("status_name") == "AVAILABLE", "Canonical Python Core gateway did not become available")
	var capability_matrix: Dictionary = gateway.call("capability_matrix")
	_check(bool(capability_matrix["Generate"]["available"]), "Generate capability was not derived as available")
	_check(not bool(capability_matrix["Solve"]["available"]), "Solve became available without M03")
	_check(not bool(capability_matrix["Validate"]["available"]), "Validate became available without standalone canonical validation")
	_check(not bool(capability_matrix["Analyze"]["available"]), "Analyze became available without M04")
	var invalid_request: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "NOT_A_DIFFICULTY", "width": 20, "height": 21, "seed": "77", "mode": "RULES"}, TEST_OUTPUT_PATH)
	_check(invalid_request.get("state") == "FAILED" and int(invalid_request.get("exit_code", 0)) != 0, "Canonical nonzero action failure was not mapped to FAILED")

	var difficulty := target.get_node_or_null("DifficultyRow/Difficulty") as OptionButton
	var width := target.get_node_or_null("WidthRow/Width") as SpinBox
	var height := target.get_node_or_null("HeightRow/Height") as SpinBox
	var seed := target.get_node_or_null("SeedRow/Seed") as LineEdit
	var mode := target.get_node_or_null("ModeRow/Mode") as OptionButton
	var candidate := target.get_node_or_null("CandidatepresentationlabelRow/CandidatePresentation") as LineEdit
	_check(difficulty != null and width != null and height != null and seed != null and mode != null and candidate != null, "Action integration controls are incomplete")
	if difficulty == null or width == null or height == null or seed == null or mode == null or candidate == null:
		instance.queue_free()
		_finish()
		return
	width.value = 20
	height.value = 21
	seed.text = SEED_VALUE
	seed.text_changed.emit(seed.text)
	mode.select(1)
	mode.item_selected.emit(1)
	candidate.text = PRESENTATION_LABEL
	candidate.text_changed.emit(candidate.text)
	await process_frame

	var generate_button := target.get_node_or_null("ActionArea/GenerateAction") as Button
	var reproduce_button := target.get_node_or_null("ActionArea/ReproduceAction") as Button
	_check(generate_button != null and reproduce_button != null, "Generate/Reproduce action controls are missing")
	_check(generate_button != null and not generate_button.disabled, "Generate was not enabled for a complete canonical draft")
	for action in ["Solve", "Validate", "Analyze"]:
		var button := target.get_node_or_null("ActionArea/" + action + "Action") as Button
		_check(button != null and button.disabled and "UNAVAILABLE" in button.tooltip_text, action + " is not visibly unavailable with a truthful reason")
	if generate_button == null or reproduce_button == null:
		instance.queue_free()
		_finish()
		return

	generate_button.pressed.emit()
	await process_frame
	var generated: Dictionary = target.call("action_result_snapshot")
	_check(generated.get("action") == "Generate" and generated.get("state") == "SUCCESS", "Real Studio Generate did not return canonical success evidence")
	_check(generated.get("exit_code") == 0, "Canonical Generate did not exit with code 0")
	_check(str(generated.get("candidate_id", "")) != PRESENTATION_LABEL, "Candidate presentation label was used as a canonical candidate ID")
	_check(str(generated.get("captured_output", "")).contains("SUCCESS candidate_id="), "Generate did not capture the canonical CLI summary")
	_check(str(generated.get("metadata_path", "")).ends_with("metadata.json"), "Generate did not expose metadata.json evidence")
	_check(_under_output_area(str(generated.get("output_path", ""))), "Generate output escaped the approved Factory output area")
	_check(not reproduce_button.disabled, "Reproduce was not enabled after a successful Generate")

	reproduce_button.pressed.emit()
	await process_frame
	var reproduced: Dictionary = target.call("action_result_snapshot")
	_check(reproduced.get("action") == "Reproduce" and reproduced.get("state") == "SUCCESS", "Real Studio Reproduce did not return canonical success evidence")
	_check(reproduced.get("disposition") == "MATCH", "Canonical Reproduce did not report MATCH")
	_check(reproduced.get("candidate_id") == generated.get("candidate_id"), "Reproduce candidate identity drifted")
	_check(reproduced.get("grid_hash") == generated.get("grid_hash"), "Reproduce grid hash did not match Generate")
	_check(str(reproduced.get("output_path", "")) != str(generated.get("output_path", "")), "Reproduce targeted the original Generate bundle")
	_check(_under_output_area(str(reproduced.get("output_path", ""))), "Reproduce output escaped the approved Factory output area")

	instance.queue_free()
	_finish()


func _under_output_area(path: String) -> bool:
	var output_root := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var normalized := path.simplify_path().replace(char(92), "/").to_lower()
	return normalized.begins_with(output_root + "/")


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


func _finish() -> void:
	_remove_tree(test_output_absolute)
	if failures.is_empty():
		print("SB-LF06-003-C001 Studio/Core action integration PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
