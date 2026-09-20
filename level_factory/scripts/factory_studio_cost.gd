@tool
class_name FactoryStudioCost
extends VBoxContainer

var _gateway: RefCounted
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Provider Cost / Credit Center — recorded facts only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Unknown consumed/remaining values stay NOT AVAILABLE. No provider or network calls are made by this view."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_cost() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "read_only": true, "network_calls": 0}
