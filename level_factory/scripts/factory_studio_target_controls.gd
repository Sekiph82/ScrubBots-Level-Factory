@tool
class_name FactoryStudioTargetControls
extends VBoxContainer

## Presentation-only Generate target controls.
## Python Factory Core remains the authority for request interpretation.

const CANONICAL_DIFFICULTIES: Array[String] = ["EASY", "MEDIUM", "HARD", "VERY_HARD"]
const CANONICAL_MODES: Array[String] = ["MASK", "RULES", "WFC", "HYBRID", "AUTO"]
const MIN_DIMENSION := 20
const MAX_DIMENSION := 59
const MAX_CANDIDATE_LABEL_LENGTH := 64

var difficulty_control: OptionButton
var width_control: SpinBox
var height_control: SpinBox
var seed_control: LineEdit
var mode_control: OptionButton
var candidate_label_control: LineEdit
var draft_readout: Label


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_refresh_draft_readout()


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Generate target — presentation draft"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)

	var explanation := Label.new()
	explanation.text = "Edit target values locally. No generation, solving, validation, file, or provider operation is performed."
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(explanation)

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
