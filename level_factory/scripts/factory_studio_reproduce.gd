@tool
class_name FactoryStudioReproduce
extends VBoxContainer

var _gateway: RefCounted
var _candidate: LineEdit
var _result: Label
var _reproduce_button: Button
var _capability_identity := ""
var _projection: Dictionary = {}

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Exact Reproduce — capability-gated canonical replay"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _candidate = LineEdit.new(); _candidate.name = "SelectedIdentity"; _candidate.placeholder_text = "candidate ID"; _candidate.size_flags_horizontal = Control.SIZE_EXPAND_FILL; _candidate.text_changed.connect(_on_identity_changed); row.add_child(_candidate); var button := Button.new(); button.name = "CheckCapability"; button.text = "Check capability"; button.pressed.connect(check_capability); row.add_child(button); _reproduce_button = Button.new(); _reproduce_button.name = "ExactReproduceAction"; _reproduce_button.text = "Exact Reproduce"; _reproduce_button.disabled = true; _reproduce_button.pressed.connect(exact_reproduce); row.add_child(_reproduce_button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
	_render()
func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func check_capability() -> void:
	var identity := _candidate.text.strip_edges() if _candidate != null else ""
	_projection = _gateway.call("run_studio_extension", "reproduce-capability", {"candidate_id": identity}) if _gateway != null else {"state": "UNAVAILABLE", "reason": "Core gateway is unavailable."}
	_capability_identity = identity
	if _reproduce_button != null: _reproduce_button.disabled = _projection.get("disposition") != "EXACT_REPRODUCIBLE"
	_render()
func exact_reproduce() -> void:
	var identity := _candidate.text.strip_edges() if _candidate != null else ""
	if _reproduce_button == null or _reproduce_button.disabled or identity != _capability_identity:
		_projection = {"state": "UNAVAILABLE", "disposition": "NOT_AVAILABLE", "reason": "Exact Reproduce is disabled until a fresh EXACT_REPRODUCIBLE capability result exists for this identity."}; _render(); return
	_projection = _gateway.call("run_studio_extension", "reproduce-exact", {"candidate_id": identity}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func set_selected_identity(identity: String) -> void:
	if _candidate != null:
		_candidate.text = identity
		_on_identity_changed(identity)
func capability_button_enabled() -> bool: return _reproduce_button != null and not _reproduce_button.disabled
func _on_identity_changed(_value: String) -> void:
	_capability_identity = ""
	_projection = {"state": "UNAVAILABLE", "disposition": "NOT_AVAILABLE", "reason": "Capability is stale; check the current selected identity."}
	if _reproduce_button != null: _reproduce_button.disabled = true
	_render()
func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_reproduce() -> void: _render()
func _render() -> void:
	if _result != null: _result.text = "Capability: %s | Exact Reproduce enabled=%s\n%s\nOutput: %s" % [_projection.get("disposition", "NOT AVAILABLE"), capability_button_enabled(), _projection.get("reason", _projection.get("error", "Exact replay is disabled until a real recorded path exists.")), _projection.get("output_path", "not executed")]
