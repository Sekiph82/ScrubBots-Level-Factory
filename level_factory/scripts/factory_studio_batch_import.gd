@tool
class_name FactoryStudioBatchImport
extends VBoxContainer

var _gateway: RefCounted
var _paths: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Multi-File OWNER_UPLOAD Batch Import"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _paths = LineEdit.new(); _paths.placeholder_text = "absolute PNG paths separated by |"; _paths.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_paths); var button := Button.new(); button.text = "Import batch"; button.pressed.connect(import_batch); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Each selected file uses the canonical LFX-002 importer and keeps independent identity/provenance."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func set_paths(value: String) -> void: _paths.text = value
var _projection: Dictionary = {}
func import_batch() -> void:
	var paths: Array[String] = []
	for value in _paths.text.split("|", false): paths.append(value.strip_edges())
	_projection = _gateway.call("run_studio_extension", "batch-import", {"paths": paths}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "Batch: %s\nItems: %s\nCounts: %s" % [_projection.get("batch_id", _projection.get("disposition", "UNAVAILABLE")), (_projection.get("items", []) as Array).size(), _projection.get("counts", {})]
func show_batch_import() -> void: pass
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "per_item_provenance": true, "projection": _projection.duplicate(true)}
