@tool
class_name FactoryStudioTargetControls
extends VBoxContainer

## Generate target draft and action presentation for Factory Studio.
## Python Factory Core remains the authority for request interpretation and artifacts.

const CANONICAL_DIFFICULTIES: Array[String] = ["EASY", "MEDIUM", "HARD", "VERY_HARD"]
const CANONICAL_MODES: Array[String] = ["MASK", "RULES", "WFC", "HYBRID", "AUTO"]
const ACTIONS: Array[String] = ["Generate", "Solve", "Validate", "Analyze", "Reproduce"]
const MIN_DIMENSION := 20
const MAX_DIMENSION := 59
const MAX_CANDIDATE_LABEL_LENGTH := 64
const PREVIEW_SCRIPT_PATH := "res://scripts/factory_studio_art_preview.gd"
const EVIDENCE_PANEL_SCRIPT_PATH := "res://scripts/factory_studio_evidence_panel.gd"
const ART_EDITOR_SCRIPT_PATH := "res://scripts/factory_studio_art_editor.gd"
const PUZZLE_CONFIG_GATE_SCRIPT_PATH := "res://scripts/factory_studio_puzzle_config_gate.gd"
const ART_REVALIDATION_SCRIPT_PATH := "res://scripts/factory_studio_art_revalidation.gd"

var difficulty_control: OptionButton
var width_control: SpinBox
var height_control: SpinBox
var seed_control: LineEdit
var mode_control: OptionButton
var candidate_label_control: LineEdit
var draft_readout: Label
var action_result_readout: Label
var _action_buttons: Dictionary = {}
var _core_gateway: RefCounted
var _last_action_result: Dictionary = {}
var _last_successful_core_evidence: Dictionary = {}
var _art_preview: Node
var _evidence_panel: Node
var _art_editor: Node
var _art_revalidation: Node
var _action_running := false


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_refresh_draft_readout()
	_refresh_action_controls()


func configure_gateway(gateway: RefCounted) -> void:
	_core_gateway = gateway
	if _art_revalidation != null:
		_art_revalidation.call("configure_gateway", gateway)
	_refresh_action_controls()


func manual_editor_reference() -> Node:
	return _art_editor


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Generate target — presentation draft"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)

	var explanation := Label.new()
	explanation.text = "Edit target values locally. Generate and Reproduce use the canonical Python Core; other actions remain unavailable until their governing capability exists."
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(explanation)

	var puzzle_config_gate_script := ResourceLoader.call("load", PUZZLE_CONFIG_GATE_SCRIPT_PATH) as Script
	if puzzle_config_gate_script != null:
		var puzzle_config_gate := puzzle_config_gate_script.new() as Node
		puzzle_config_gate.name = "ApprovedPuzzleConfigGate"
		add_child(puzzle_config_gate)

	difficulty_control = OptionButton.new()
	difficulty_control.name = "Difficulty"
	for difficulty in CANONICAL_DIFFICULTIES:
		difficulty_control.add_item(difficulty)
	difficulty_control.select(0)
	difficulty_control.item_selected.connect(_on_control_changed)
	add_child(_make_row("Difficulty", difficulty_control))

	width_control = _make_dimension_control("Width")
	add_child(_make_row("Width", width_control))
	height_control = _make_dimension_control("Height")
	add_child(_make_row("Height", height_control))

	seed_control = LineEdit.new()
	seed_control.name = "Seed"
	seed_control.placeholder_text = "integer or text seed"
	seed_control.text_changed.connect(_on_control_changed)
	add_child(_make_row("Seed", seed_control))

	mode_control = OptionButton.new()
	mode_control.name = "Mode"
	for mode in CANONICAL_MODES:
		mode_control.add_item(mode)
	mode_control.select(0)
	mode_control.item_selected.connect(_on_control_changed)
	add_child(_make_row("Mode", mode_control))

	candidate_label_control = LineEdit.new()
	candidate_label_control.name = "CandidatePresentation"
	candidate_label_control.placeholder_text = "optional bounded presentation label"
	candidate_label_control.max_length = MAX_CANDIDATE_LABEL_LENGTH
	candidate_label_control.text_changed.connect(_on_control_changed)
	add_child(_make_row("Candidate presentation label", candidate_label_control))

	draft_readout = Label.new()
	draft_readout.name = "DraftReadout"
	draft_readout.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(draft_readout)

	var action_heading := Label.new()
	action_heading.name = "ActionHeading"
	action_heading.text = "Action controls"
	action_heading.add_theme_font_size_override("font_size", 16)
	add_child(action_heading)

	var action_area := VBoxContainer.new()
	action_area.name = "ActionArea"
	add_child(action_area)
	for action in ACTIONS:
		var button := Button.new()
		button.name = action + "Action"
		button.text = action
		button.pressed.connect(_on_action_pressed.bind(action))
		_action_buttons[action] = button
		action_area.add_child(button)

	action_result_readout = Label.new()
	action_result_readout.name = "ActionResult"
	action_result_readout.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	action_result_readout.text = "Action result: IDLE"
	action_area.add_child(action_result_readout)

	var preview_script := ResourceLoader.call("load", PREVIEW_SCRIPT_PATH) as Script
	if preview_script != null:
		_art_preview = preview_script.new() as Node
		_art_preview.name = "CanonicalArtworkPreview"
		action_area.add_child(_art_preview)
	var evidence_script := ResourceLoader.call("load", EVIDENCE_PANEL_SCRIPT_PATH) as Script
	if evidence_script != null:
		_evidence_panel = evidence_script.new() as Node
		_evidence_panel.name = "CanonicalEvidencePanel"
		action_area.add_child(_evidence_panel)
	var editor_script := ResourceLoader.call("load", ART_EDITOR_SCRIPT_PATH) as Script
	if editor_script != null:
		_art_editor = editor_script.new() as Node
		_art_editor.name = "CanonicalArtEditor"
		action_area.add_child(_art_editor)
	var revalidation_script := ResourceLoader.call("load", ART_REVALIDATION_SCRIPT_PATH) as Script
	if revalidation_script != null:
		_art_revalidation = revalidation_script.new() as Node
		_art_revalidation.name = "ManualArtStructuralRevalidation"
		action_area.add_child(_art_revalidation)
		_art_revalidation.call("configure_editor", _art_editor)
		if _core_gateway != null:
			_art_revalidation.call("configure_gateway", _core_gateway)


func _make_dimension_control(control_name: String) -> SpinBox:
	var control := SpinBox.new()
	control.name = control_name
	control.min_value = MIN_DIMENSION
	control.max_value = MAX_DIMENSION
	control.step = 1
	control.value = MIN_DIMENSION
	control.allow_greater = false
	control.allow_lesser = false
	control.value_changed.connect(_on_control_changed)
	return control


func _make_row(label_text: String, control: Control) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = label_text.replace(" ", "") + "Row"
	var label := Label.new()
	label.text = label_text
	label.custom_minimum_size = Vector2(220, 0)
	row.add_child(label)
	control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(control)
	return row


func _on_control_changed(_value: Variant = null) -> void:
	_refresh_draft_readout()
	_refresh_action_controls()


func draft_snapshot() -> Dictionary:
	return {
		"state": "DRAFT",
		"core_validation": "UNAVAILABLE",
		"generation_state": "NOT EXECUTED — presentation draft only",
		"difficulty": _selected_option(difficulty_control, CANONICAL_DIFFICULTIES[0]),
		"width": int(width_control.value) if width_control != null else MIN_DIMENSION,
		"height": int(height_control.value) if height_control != null else MIN_DIMENSION,
		"seed": seed_control.text if seed_control != null else "",
		"mode": _selected_option(mode_control, CANONICAL_MODES[0]),
		"candidate_presentation": candidate_label_control.text if candidate_label_control != null else "",
	}


func action_result_snapshot() -> Dictionary:
	return _last_action_result.duplicate(true)


func last_successful_core_evidence_snapshot() -> Dictionary:
	return _last_successful_core_evidence.duplicate(true)


func _selected_option(control: OptionButton, fallback: String) -> String:
	if control == null or control.selected < 0:
		return fallback
	return control.get_item_text(control.selected)


func _refresh_draft_readout() -> void:
	if draft_readout == null:
		return
	var snapshot := draft_snapshot()
	draft_readout.text = "State: %s | Core validation: %s | %s\nDraft: %s × %s, %s, %s, seed=%s, candidate=%s" % [
		snapshot["state"],
		snapshot["core_validation"],
		snapshot["generation_state"],
		snapshot["width"],
		snapshot["height"],
		snapshot["difficulty"],
		snapshot["mode"],
		snapshot["seed"],
		snapshot["candidate_presentation"],
	]


func _refresh_action_controls() -> void:
	if _action_buttons.is_empty():
		return
	var matrix: Dictionary = {}
	if _core_gateway != null and _core_gateway.has_method("capability_matrix"):
		matrix = _core_gateway.call("capability_matrix")
	var seed_present := not str(draft_snapshot().get("seed", "")).strip_edges().is_empty()
	for action in ACTIONS:
		var button: Button = _action_buttons[action]
		var capability: Dictionary = matrix.get(action, {"available": false, "reason": "UNAVAILABLE — canonical action capability is not connected."})
		var available := bool(capability.get("available", false))
		var reason := str(capability.get("reason", "UNAVAILABLE"))
		if action == "Generate" and available and not seed_present:
			available = false
			reason = "UNAVAILABLE — enter a seed for a deterministic canonical Generate request."
		button.disabled = _action_running or not available
		button.tooltip_text = "" if available else reason


func _on_action_pressed(action: String) -> void:
	if _action_running or _core_gateway == null or not _core_gateway.has_method("run_action"):
		return
	_action_running = true
	_refresh_action_controls()
	var result: Variant = _core_gateway.call("run_action", action, draft_snapshot())
	_last_action_result = result if result is Dictionary else {"action": action, "state": "FAILED", "reason": "FAILED — action bridge returned no structured result."}
	if _last_action_result.get("state") == "SUCCESS":
		_last_successful_core_evidence = _last_action_result.duplicate(true)
	if _art_preview != null:
		_art_preview.call("consume_action_result", _last_action_result)
	if _evidence_panel != null:
		_evidence_panel.call("consume_action_result", _last_action_result)
	if _art_editor != null:
		_art_editor.call("observe_action_result", _last_action_result)
	if _art_revalidation != null:
		_art_revalidation.call("refresh_from_editor")
	_action_running = false
	_render_action_result()
	_refresh_action_controls()


func _render_action_result() -> void:
	if action_result_readout == null:
		return
	var state := str(_last_action_result.get("state", "IDLE"))
	var action := str(_last_action_result.get("action", ""))
	var disposition := str(_last_action_result.get("disposition", state))
	var message := str(_last_action_result.get("reason", ""))
	if state == "SUCCESS":
		message = "Core evidence: candidate=%s | seed=%s | mode=%s | dimensions=%s | grid_hash=%s | output=%s | metadata=%s" % [
			_last_action_result.get("candidate_id", ""),
			_last_action_result.get("selected_seed", ""),
			_last_action_result.get("mode", ""),
			_last_action_result.get("dimensions", ""),
			_last_action_result.get("grid_hash", ""),
			_last_action_result.get("output_path", ""),
			_last_action_result.get("metadata_path", ""),
		]
	elif not _last_successful_core_evidence.is_empty():
		message += "\nLast successful Core evidence retained: candidate=%s | grid_hash=%s | output=%s | metadata=%s" % [
			_last_successful_core_evidence.get("candidate_id", ""),
			_last_successful_core_evidence.get("grid_hash", ""),
			_last_successful_core_evidence.get("output_path", ""),
			_last_successful_core_evidence.get("metadata_path", ""),
		]
	action_result_readout.text = "Action result: %s / %s / exit=%s\n%s" % [action, disposition, _last_action_result.get("exit_code", ""), message]
