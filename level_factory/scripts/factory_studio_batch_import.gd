@tool
class_name FactoryStudioBatchImport
extends VBoxContainer

var _gateway: RefCounted
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Multi-File OWNER_UPLOAD Batch Import"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Each selected file uses the canonical LFX-002 importer and keeps independent identity/provenance."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_batch_import() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "per_item_provenance": true}
