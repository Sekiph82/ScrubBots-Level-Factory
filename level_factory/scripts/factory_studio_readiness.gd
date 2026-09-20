@tool
class_name FactoryStudioReadiness
extends VBoxContainer

var _gateway: RefCounted
var _candidate: LineEdit
var _result: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Production Readiness Card — canonical gates"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _candidate = LineEdit.new(); _candidate.placeholder_text = "candidate ID"; _candidate.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate); var button := Button.new(); button.text = "Refresh card"; button.pressed.connect(refresh_card); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func refresh_card() -> void: _projection = _gateway.call("run_studio_extension", "readiness", {"candidate_id": _candidate.text.strip_edges()}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func refresh_candidate(candidate_id: String) -> void:
	if _candidate != null: _candidate.text = candidate_id
	refresh_card()
func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_readiness() -> void: _render()


func _render() -> void:
	if _result == null: return
	var rows: Array[String] = []
	for key in ["SOURCE", "PALETTE", "STRUCTURE", "SOLVER", "DIFFICULTY", "QA", "OWNER", "EXPORT"]:
		var gate: Dictionary = _projection.get("gates", {}).get(key, {"disposition": "NOT AVAILABLE", "reason": "No card loaded."})
		rows.append("%s=%s" % [key, gate.get("disposition", "NOT AVAILABLE")])
	_result.text = "Overall: %s | %s\n%s" % [_projection.get("overall", "NOT AVAILABLE"), _projection.get("reason", ""), " | ".join(rows)]
