@tool
class_name FactoryStudioFailures
extends VBoxContainer

var _gateway: RefCounted
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Failure Inbox / Retry Center — preserved evidence"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Retry is enabled only for real eligible FAILED/REJECTED/INCONCLUSIVE evidence."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_failures() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "original_failure_preserved": true}
