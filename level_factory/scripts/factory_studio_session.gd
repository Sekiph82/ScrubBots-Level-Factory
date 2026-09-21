@tool
class_name FactoryStudioSession
extends VBoxContainer

var _gateway: RefCounted
var _session: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Session Recovery / Autosave — canonical references only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _session = LineEdit.new(); _session.placeholder_text = "session ID"; _session.text = "studio-session"; _session.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_session); var save := Button.new(); save.text = "Save"; save.pressed.connect(save_session); row.add_child(save); var restore := Button.new(); restore.text = "Restore"; restore.pressed.connect(restore_session); row.add_child(restore); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Recovery labels distinguish RESUMED, RETRIED, NEW, NOT_RESUMABLE, and NEEDS_OPERATOR_ACTION."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
var _projection: Dictionary = {}
func set_session_id(session_id: String) -> void:
	if _session != null: _session.text = session_id
func save_session() -> void:
	_projection = _gateway.call("run_studio_extension", "session-save", {"session_id": _session.text.strip_edges(), "state": {"surface": "Session", "autosave_generation": 0}}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func restore_session() -> void:
	_projection = _gateway.call("run_studio_extension", "session-restore", {"session_id": _session.text.strip_edges()}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func _render() -> void: _result.text = "Recovery: %s\nReferences validated: %s" % [_projection.get("recovery", _projection.get("state", "AVAILABLE")), _projection.get("validated_references", false)]
func show_session() -> void: pass
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "secrets_persisted": false, "projection": _projection.duplicate(true)}
