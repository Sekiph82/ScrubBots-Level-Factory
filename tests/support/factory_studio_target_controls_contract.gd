extends Node

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const DIFFICULTY_PATH := NodePath("DifficultyRow/Difficulty")
const WIDTH_PATH := NodePath("WidthRow/Width")
const HEIGHT_PATH := NodePath("HeightRow/Height")
const SEED_PATH := NodePath("SeedRow/Seed")
const MODE_PATH := NodePath("ModeRow/Mode")
const CANDIDATE_PATH := NodePath("CandidatepresentationlabelRow/CandidatePresentation")

const EXPECTED_DIFFICULTIES: Array[String] = ["EASY", "MEDIUM", "HARD", "VERY_HARD"]
const EXPECTED_MODES: Array[String] = ["MASK", "RULES", "WFC", "HYBRID", "AUTO"]

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_contract")


func _run_contract() -> void:
	var packed_scene := load(MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		get_tree().quit(1)
		return

	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		get_tree().quit(1)
		return
	get_tree().root.add_child(instance)
	await get_tree().process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH) as FactoryStudioNavigation
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH) as FactoryStudioWorkspacePage
	_check(navigation != null, "Navigation did not instantiate")
	_check(workspace != null, "Workspace did not instantiate")
	if navigation == null or workspace == null:
		instance.queue_free()
		get_tree().quit(1)
		return

	var generate_button := _find_navigation_button(navigation, "Generate")
	_check(generate_button != null, "Generate navigation control is missing")
	if generate_button == null:
		instance.queue_free()
		get_tree().quit(1)
		return

	generate_button.pressed.emit()
	await get_tree().process_frame
	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	_check(target != null, "Generate navigation did not expose target controls")
	if target == null:
		instance.queue_free()
		get_tree().quit(1)
		return
	_check(target.visible, "Generate target controls are not visible")

	var difficulty := target.get_node_or_null(DIFFICULTY_PATH) as OptionButton
	var width := target.get_node_or_null(WIDTH_PATH) as SpinBox
	var height := target.get_node_or_null(HEIGHT_PATH) as SpinBox
	var seed := target.get_node_or_null(SEED_PATH) as LineEdit
	var mode := target.get_node_or_null(MODE_PATH) as OptionButton
	var candidate := target.get_node_or_null(CANDIDATE_PATH) as LineEdit
	_check(difficulty != null, "Difficulty control path is missing")
	_check(width != null, "Width control path is missing")
	_check(height != null, "Height control path is missing")
	_check(seed != null, "Seed control path is missing")
	_check(mode != null, "Mode control path is missing")
	_check(candidate != null, "Candidate presentation control path is missing")
	if difficulty == null or width == null or height == null or seed == null or mode == null or candidate == null:
		instance.queue_free()
		get_tree().quit(1)
		return

	_check(_option_values(difficulty) == EXPECTED_DIFFICULTIES, "Difficulty choices drifted from the canonical Python choices")
	_check(_option_values(mode) == EXPECTED_MODES, "Mode choices drifted from the canonical Python choices")
	_check(width.min_value == 20.0 and width.max_value == 59.0, "Width presentation envelope is not 20..59")
	_check(height.min_value == 20.0 and height.max_value == 59.0, "Height presentation envelope is not 20..59")
	_check(candidate.max_length == 64, "Candidate presentation label is not bounded")

	var initial_snapshot: Dictionary = target.call("draft_snapshot")
	_check(initial_snapshot["state"] == "DRAFT", "Initial Generate state is not DRAFT")
	_check(initial_snapshot["core_validation"] == "UNAVAILABLE", "Initial Generate Core state is not UNAVAILABLE")
	_check(initial_snapshot["generation_state"] == "NOT EXECUTED — presentation draft only", "Initial Generate state implies an operation")

	difficulty.select(3)
	difficulty.item_selected.emit(3)
	width.value = 23
	height.value = 47
	seed.text = "operator-seed"
	seed.text_changed.emit(seed.text)
	mode.select(3)
	mode.item_selected.emit(3)
	candidate.text = "preview-label"
	candidate.text_changed.emit(candidate.text)
	await get_tree().process_frame
	var edited_snapshot: Dictionary = target.call("draft_snapshot")
	_check(edited_snapshot["difficulty"] == "VERY_HARD", "Difficulty draft did not update")
	_check(edited_snapshot["width"] == 23 and edited_snapshot["height"] == 47, "Independent rectangular dimensions did not update")
	_check(edited_snapshot["seed"] == "operator-seed", "Seed draft did not update")
	_check(edited_snapshot["mode"] == "HYBRID", "Mode draft did not update")
	_check(edited_snapshot["candidate_presentation"] == "preview-label", "Candidate presentation draft did not update")
	_check(target.call("draft_snapshot") == edited_snapshot, "Draft snapshot is not deterministic")

	for difficulty_index in range(EXPECTED_DIFFICULTIES.size()):
		difficulty.select(difficulty_index)
		difficulty.item_selected.emit(difficulty_index)
		_check(width.min_value == 20.0 and width.max_value == 59.0, "Difficulty changed the width envelope")
		_check(height.min_value == 20.0 and height.max_value == 59.0, "Difficulty changed the height envelope")

	_check(_contains_action_buttons(target), "Factory Studio action controls are missing")

	var dashboard_button := _find_navigation_button(navigation, "Dashboard")
	_check(dashboard_button != null, "Dashboard navigation control is missing")
	if dashboard_button != null:
		dashboard_button.pressed.emit()
		await get_tree().process_frame
		_check(not target.visible, "Target controls remained visible after leaving Generate")
		generate_button.pressed.emit()
		await get_tree().process_frame
		_check(target.visible, "Generate target controls were not stable after navigation round trip")
		_check(target.call("draft_snapshot") == edited_snapshot, "Draft state was not stable across navigation round trip")

	instance.queue_free()
	if failures.is_empty():
		print("SB-LF06-002-C001 target controls runtime contract PASS")
		get_tree().quit(0)
		return
	for failure in failures:
		push_error(failure)
	get_tree().quit(1)


func _find_navigation_button(navigation: FactoryStudioNavigation, label: String) -> Button:
	for child in navigation.get_children():
		if child is Button and (child as Button).text == label:
			return child as Button
	return null


func _option_values(control: OptionButton) -> Array[String]:
	var values: Array[String] = []
	for index in range(control.item_count):
		values.append(control.get_item_text(index))
	return values


func _contains_action_buttons(node: Node) -> bool:
	for action in ["Generate", "Solve", "Validate", "Analyze", "Reproduce"]:
		if node.get_node_or_null("ActionArea/" + action + "Action") == null:
			return false
	return true


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
