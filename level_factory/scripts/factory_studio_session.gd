@tool
class_name FactoryStudioSession
extends VBoxContainer

var _gateway: RefCounted
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Session Recovery / Autosave — canonical references only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Recovery labels distinguish RESUMED, RETRIED, NEW, NOT_RESUMABLE, and NEEDS_OPERATOR_ACTION."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_session() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "secrets_persisted": false}
