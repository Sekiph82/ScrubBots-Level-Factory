@tool
class_name FactoryStudioBatchImport
extends VBoxContainer

var _gateway: RefCounted
var _paths: LineEdit
var _result: Label
var _file_dialog: FileDialog

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Multi-File OWNER_UPLOAD Batch Import"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); var choose := Button.new(); choose.text = "Choose PNG files…"; choose.pressed.connect(open_file_dialog); row.add_child(choose); _paths = LineEdit.new(); _paths.placeholder_text = "headless/test path setter"; _paths.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_paths); var button := Button.new(); button.text = "Import batch"; button.pressed.connect(import_batch); row.add_child(button); add_child(row)
		_file_dialog = FileDialog.new(); _file_dialog.name = "BatchFileDialog"; _file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILES; _file_dialog.access = FileDialog.ACCESS_FILESYSTEM; _file_dialog.filters = PackedStringArray(["*.png ; PNG files"]); _file_dialog.files_selected.connect(_on_files_selected); add_child(_file_dialog)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Each selected file uses the canonical LFX-002 importer and keeps independent identity/provenance."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func set_paths(value: String) -> void: _paths.text = value
func open_file_dialog() -> void:
	if _file_dialog != null: _file_dialog.popup_centered_ratio(0.8)
func _on_files_selected(paths: PackedStringArray) -> void:
	if _paths != null: _paths.text = "|".join(Array(paths))
var _projection: Dictionary = {}
func import_batch() -> void:
	var paths: Array[String] = []
	for value in _paths.text.split("|", false): paths.append(value.strip_edges())
	_projection = _gateway.call("run_studio_extension", "batch-import", {"paths": paths}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "Batch: %s\nItems: %s\nCounts: %s" % [_projection.get("batch_id", _projection.get("disposition", "UNAVAILABLE")), (_projection.get("items", []) as Array).size(), _projection.get("counts", {})]
func show_batch_import() -> void: pass
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "per_item_provenance": true, "projection": _projection.duplicate(true)}
