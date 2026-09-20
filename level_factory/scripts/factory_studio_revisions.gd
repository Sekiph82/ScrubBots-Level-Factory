@tool
class_name FactoryStudioRevisions
extends VBoxContainer

var _gateway: RefCounted
var _candidate: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Manual Edit Revisions — immutable lineage"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var notice := Label.new(); notice.text = "Save/undo/restore selects explicit revisions; source bundles and prior revisions are never overwritten. Revalidation is bound to the working-grid hash."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
		var row := HBoxContainer.new(); _candidate = LineEdit.new(); _candidate.placeholder_text = "candidate ID"; _candidate.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate); var button := Button.new(); button.text = "List revisions"; button.pressed.connect(list_revisions); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
		_result.text = "Revision history is available from the canonical manual editor integration."

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func list_revisions() -> void:
	_projection = _gateway.call("run_studio_extension", "revision-list", {"candidate_id": _candidate.text.strip_edges()}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "Revision operation: %s\nCount: %s" % [_projection.get("disposition", _projection.get("state", "UNAVAILABLE")), (_projection.get("revisions", []) as Array).size()]
func show_revisions() -> void: pass
var _projection: Dictionary = {}
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "source_mutation": "FORBIDDEN", "projection": _projection.duplicate(true)}
