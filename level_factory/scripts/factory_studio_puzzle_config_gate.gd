@tool
class_name FactoryStudioPuzzleConfigGate
extends VBoxContainer

## Fail-closed presentation gate until a canonical, explicitly approved
## gameplay/puzzle-config edit contract exists.

const UNAVAILABLE := "UNAVAILABLE"
const NO_APPROVED_CONTRACT := "UNAVAILABLE — no approved canonical puzzle-config edit contract"
const UNVALIDATED_DISPOSITION := "UNVALIDATED — no editable canonical puzzle-config contract exists"

var _state := UNAVAILABLE
var _state_label: Label
var _detail_label: Label


func _ready() -> void:
	if get_child_count() == 0:
		_build_gate()
	_refresh_gate()


func snapshot() -> Dictionary:
	return {
		"state": _state,
		"disposition": NO_APPROVED_CONTRACT,
		"editable_fields": [],
		"controls_enabled": false,
		"mutation_available": false,
		"source_config": "UNAVAILABLE — no canonical puzzle-config source is loaded",
		"validation_disposition": UNVALIDATED_DISPOSITION,
	}


func _build_gate() -> void:
	var heading := Label.new()
	heading.name = "PuzzleConfigHeading"
	heading.text = "Approved puzzle-config edit gate"
	heading.add_theme_font_size_override("font_size", 16)
	add_child(heading)

	_state_label = Label.new()
	_state_label.name = "PuzzleConfigState"
	_state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_state_label)

	_detail_label = Label.new()
	_detail_label.name = "PuzzleConfigDetail"
	_detail_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_detail_label)


func _refresh_gate() -> void:
	if _state_label == null or _detail_label == null:
		return
	_state_label.text = "Puzzle-config editing: %s | %s — no mutation controls available" % [_state, NO_APPROVED_CONTRACT]
	_detail_label.text = "%s. No authoritative LevelData/puzzle-config schema with explicitly approved Studio-editable fields exists in this repository. GenerationRequest target fields, WFC options, artwork pixels, and presentation labels are not puzzle-config values. %s." % [NO_APPROVED_CONTRACT, UNVALIDATED_DISPOSITION]
