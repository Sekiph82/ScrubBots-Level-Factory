extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const GATE_NODE_PATH := NodePath("ApprovedPuzzleConfigGate")
const NO_APPROVED_CONTRACT := "UNAVAILABLE — no approved canonical puzzle-config edit contract"
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
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
	var gate := target.get_node_or_null(GATE_NODE_PATH)
	_check(gate != null and gate.visible, "Approved puzzle-config gate is not visible on Generate")
	if gate == null:
		instance.queue_free()
		_finish()
		return

	var initial_gate: Dictionary = gate.call("snapshot")
	_check(initial_gate.get("state") == "UNAVAILABLE", "Puzzle-config gate did not report UNAVAILABLE")
	_check(initial_gate.get("disposition") == NO_APPROVED_CONTRACT, "Puzzle-config gate disposition is not truthful")
	_check(initial_gate.get("editable_fields") == [], "Unavailable gate exposed editable puzzle-config fields")
	_check(initial_gate.get("controls_enabled") == false and initial_gate.get("mutation_available") == false, "Unavailable gate exposed mutation capability")
	_check("GenerationRequest" not in str(initial_gate.get("source_config", "")), "Gate synthesized a source config from GenerationRequest")
	_check("UNAVAILABLE" in str(initial_gate.get("source_config", "")), "Gate did not keep source config unavailable")
	_check("UNVALIDATED" in str(initial_gate.get("validation_disposition", "")), "Gate omitted explicit UNVALIDATED disposition")
	_check(gate.get_child_count() == 3, "Unavailable gate did not remain label-only")
	for child in gate.get_children():
		_check(child is Label, "Unavailable gate contains a mutation-capable control")
	var state_label := gate.get_node_or_null("PuzzleConfigState") as Label
	var detail_label := gate.get_node_or_null("PuzzleConfigDetail") as Label
	_check(state_label != null and NO_APPROVED_CONTRACT in state_label.text, "Unavailable state was not visibly presented")
	_check(detail_label != null and "GenerationRequest target fields" in detail_label.text, "Gate did not explain GenerationRequest separation")
	_check(detail_label != null and "No mutation controls" not in detail_label.text, "Gate detail contains an unexpected mutation claim")

	var draft_before: Dictionary = target.call("draft_snapshot")
	_check(not draft_before.is_empty(), "Generate draft snapshot was unavailable for separation proof")
	_check(gate.call("snapshot") == initial_gate, "Gate state changed without an approved config action")
	_check(target.get_node_or_null("DifficultyRow/Difficulty") != null, "Existing Generate target controls disappeared")
	_check(gate.get_node_or_null("CandidatePresentation") == null, "Gate incorrectly exposed a candidate presentation editor")

	instance.queue_free()
	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("SB-LF06-007-C001 puzzle-config UNAVAILABLE integration PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
