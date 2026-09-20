@tool
class_name FactoryStudioRevisions
extends VBoxContainer

var _gateway: RefCounted
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Manual Edit Revision History — immutable lineage"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var notice := Label.new(); notice.text = "Save/undo/restore selects explicit revisions; source bundles and prior revisions are never overwritten. Revalidation is bound to the working-grid hash."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
		_result.text = "Revision history is available from the canonical manual editor integration."

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_revisions() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "source_mutation": "FORBIDDEN"}
