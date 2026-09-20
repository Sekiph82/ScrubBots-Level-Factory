@tool
class_name FactoryStudioReproduce
extends VBoxContainer

var _gateway: RefCounted
var _candidate: LineEdit
var _result: Label
var _projection: Dictionary = {}

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Exact Reproduce — capability-gated canonical replay"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _candidate = LineEdit.new(); _candidate.placeholder_text = "candidate ID"; _candidate.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate); var button := Button.new(); button.text = "Check capability"; button.pressed.connect(check_capability); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
	_render()
func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func check_capability() -> void: _projection = _gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": _candidate.text.strip_edges()}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_reproduce() -> void: _render()
func _render() -> void:
	if _result != null: _result.text = "Capability: %s\n%s" % [_projection.get("disposition", "NOT AVAILABLE"), _projection.get("reason", "Exact replay is disabled until a real recorded path exists.")]
