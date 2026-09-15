extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const FOOTER_STATUS_PATH := NodePath("Frame/Layout/Footer/Status")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const DIFFICULTY_PATH := NodePath("DifficultyRow/Difficulty")
const WIDTH_PATH := NodePath("WidthRow/Width")
const HEIGHT_PATH := NodePath("HeightRow/Height")
const SEED_PATH := NodePath("SeedRow/Seed")
const MODE_PATH := NodePath("ModeRow/Mode")
const CANDIDATE_PATH := NodePath("CandidatepresentationlabelRow/CandidatePresentation")

const EXPECTED_DIFFICULTIES: Array[String] = ["EASY", "MEDIUM", "HARD", "VERY_HARD"]
const EXPECTED_MODES: Array[String] = ["MASK", "RULES", "WFC", "HYBRID", "AUTO"]
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var packed_scene := ResourceLoader.call(SCENE_LOADER_METHOD, MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		quit(1)
		return

	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		quit(1)
		return
	root.add_child(instance)
	await process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(navigation != null, "Navigation did not instantiate at the committed path")
	_check(workspace != null, "Workspace did not instantiate at the committed path")
	if navigation == null or workspace == null:
		instance.queue_free()
		quit(1)
		return

	_check(navigation.has_signal("surface_selected"), "Navigation surface_selected signal is missing")
	_check(_workspace_signal_is_connected(navigation, workspace), "Navigation signal is not connected to Workspace presentation")

	var title := workspace.get_node_or_null("Padding/Content/Title") as Label
	var state := workspace.get_node_or_null("Padding/Content/State") as Label
	var footer_status := instance.get_node_or_null(FOOTER_STATUS_PATH) as Label
	_check(title != null, "Workspace title path is missing")
	_check(state != null, "Workspace state path is missing")
	_check(footer_status != null, "Core status footer path is missing")
	if title == null or state == null or footer_status == null:
		instance.queue_free()
		quit(1)
		return
	_check(title.text == "Factory Studio — Dashboard", "initial surface is not Dashboard")
	_check("NOT AVAILABLE" in state.text, "Dashboard does not report truthful unavailability")
	_check("UNAVAILABLE" in footer_status.text, "Core status is not truthful UNAVAILABLE")

	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	_check(title.text == "Factory Studio — Generate", "Generate navigation did not reach the workspace")
	_check("DRAFT" in state.text and "UNAVAILABLE" in state.text, "Generate draft/Core state is not truthful")

	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	_check(target != null and target.visible, "Generate target controls are not visible")
	if target == null:
		instance.queue_free()
		quit(1)
		return

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
		quit(1)
		return

	_check(_option_values(difficulty) == EXPECTED_DIFFICULTIES, "Difficulty choices drifted from the accepted contract")
	_check(_option_values(mode) == EXPECTED_MODES, "Mode choices drifted from the accepted contract")
	_check(width.min_value == 20.0 and width.max_value == 59.0, "Width bounds are not 20..59")
	_check(height.min_value == 20.0 and height.max_value == 59.0, "Height bounds are not 20..59")
	_check(candidate.max_length == 64, "Candidate presentation label is not bounded")

	var initial_snapshot = target.call("draft_snapshot")
	_check(initial_snapshot is Dictionary, "Draft snapshot is not a dictionary")
	if not initial_snapshot is Dictionary:
		instance.queue_free()
		quit(1)
		return
	_check(initial_snapshot["state"] == "DRAFT", "Initial draft state is not DRAFT")
	_check(initial_snapshot["core_validation"] == "UNAVAILABLE", "Initial Core state is not UNAVAILABLE")
	_check(initial_snapshot["generation_state"] == "NOT EXECUTED — presentation draft only", "Initial draft claims an operation")

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
	await process_frame

	var edited_snapshot = target.call("draft_snapshot")
	_check(edited_snapshot is Dictionary, "Edited draft snapshot is not a dictionary")
	if edited_snapshot is Dictionary:
		_check(edited_snapshot["difficulty"] == "VERY_HARD", "Difficulty draft did not update")
		_check(edited_snapshot["width"] == 23 and edited_snapshot["height"] == 47, "Independent rectangle did not update")
		_check(edited_snapshot["seed"] == "operator-seed", "Seed draft did not update")
		_check(edited_snapshot["mode"] == "HYBRID", "Mode draft did not update")
		_check(edited_snapshot["candidate_presentation"] == "preview-label", "Candidate presentation draft did not update")
		_check(target.call("draft_snapshot") == edited_snapshot, "Draft snapshot is not deterministic")

	for difficulty_index in range(EXPECTED_DIFFICULTIES.size()):
		difficulty.select(difficulty_index)
		difficulty.item_selected.emit(difficulty_index)
		_check(width.min_value == 20.0 and width.max_value == 59.0, "Difficulty changed width bounds")
		_check(height.min_value == 20.0 and height.max_value == 59.0, "Difficulty changed height bounds")
	_check(_contains_no_action_button(target), "Target controls introduced an operational action button")

	navigation.emit_signal("surface_selected", "Import")
	await process_frame
	_check(title.text == "Factory Studio — Import", "Inert Import surface is unstable")
	_check(not target.visible, "Target controls remained visible on an inert surface")
	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	_check(target.visible, "Generate target controls did not return")
	_check(target.call("draft_snapshot") == edited_snapshot, "Draft did not remain stable across navigation")

	instance.queue_free()
	if failures.is_empty():
		print("SB-LF06-002-C001-R01 committed runtime suite PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _workspace_signal_is_connected(navigation: Node, workspace: Node) -> bool:
	for connection in navigation.get_signal_connection_list("surface_selected"):
		var callback: Callable = connection.get("callable")
		if callback.get_object() == workspace and callback.get_method() == "show_surface":
			return true
	return false


func _option_values(control: OptionButton) -> Array[String]:
	var values: Array[String] = []
	for index in range(control.item_count):
		values.append(control.get_item_text(index))
	return values


func _contains_no_action_button(node: Node) -> bool:
	for child in node.get_children():
		if child is Button and not child is OptionButton:
			return false
		if not _contains_no_action_button(child):
			return false
	return true


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
