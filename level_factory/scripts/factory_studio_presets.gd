@tool
class_name FactoryStudioPresets
extends VBoxContainer

var _gateway: RefCounted
var _id: LineEdit
var _name: LineEdit
var _state: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func save_generate_preset() -> void:
	if _gateway == null: return
	_projection = _gateway.call("run_studio_extension", "preset-save", {"preset_id": _id.text.strip_edges(), "name": _name.text.strip_edges(), "operation": "Generate", "settings": {"difficulty": "EASY", "width": 20, "height": 20, "seed": 0, "mode": "MASK"}})
	_render()


func apply_preset() -> void:
	if _gateway == null: return
	_projection = _gateway.call("run_studio_extension", "preset-apply", {"preset_id": _id.text.strip_edges()})
	_render()


func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_presets() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "Presets / Production Recipes — operator convenience only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var notice := Label.new(); notice.text = "Every application expands to a full canonical request. Preset edits affect future runs only; no provider secrets or solver/difficulty fiction is accepted."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
	var row := HBoxContainer.new(); _id = LineEdit.new(); _id.placeholder_text = "preset id"; row.add_child(_id); _name = LineEdit.new(); _name.placeholder_text = "preset name"; row.add_child(_name); var save := Button.new(); save.text = "Save / Update"; save.pressed.connect(save_generate_preset); row.add_child(save); var apply := Button.new(); apply.text = "Apply expanded request"; apply.pressed.connect(apply_preset); row.add_child(apply); add_child(row)
	_state = Label.new(); _state.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state)


func _render() -> void:
	if _state == null: return
	_state.text = "Preset result: %s\n%s" % [_projection.get("state", "EMPTY"), JSON.stringify(_projection)]
