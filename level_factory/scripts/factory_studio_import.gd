@tool
class_name FactoryStudioImport
extends VBoxContainer

## Bounded OWNER_UPLOAD source ingestion presentation.
## This node never normalizes, validates, promotes, or edits source bytes.

const OWNER_UPLOAD_OPERATION := "owner-upload-import"
const SOURCE_ONLY_NOTICE := "SOURCE ONLY — validation/candidate creation pending SB-LFX-004"

var _core_gateway: RefCounted
var _file_dialog: FileDialog
var _source_path_control: LineEdit
var _state_label: Label
var _identity_label: Label
var _origin_label: Label
var _hash_label: Label
var _dimensions_label: Label
var _stored_path_label: Label
var _notice_label: Label
var _projection: Dictionary = {}
var _source_path := ""
var _import_running := false


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_set_empty()


func configure_gateway(gateway: RefCounted) -> void:
	_core_gateway = gateway


func set_source_path(path: String) -> void:
	_source_path = path.strip_edges()
	if _source_path_control != null:
		_source_path_control.text = _source_path
	if _projection.get("state", "") in ["IMPORTED", "ALREADY_IMPORTED", "ERROR"]:
		_set_empty()


func source_path() -> String:
	return _source_path


func import_selected() -> void:
	if _import_running:
		return
	_source_path = _source_path_control.text.strip_edges() if _source_path_control != null else _source_path
	if _source_path.is_empty():
		_set_empty()
		return
	if _core_gateway == null or not _core_gateway.has_method("run_owner_import"):
		_set_error("ERROR — canonical OWNER_UPLOAD operation is not connected.")
		return
	_import_running = true
	_projection = {"operation": OWNER_UPLOAD_OPERATION, "state": "IMPORTING", "disposition": "IMPORTING"}
	_render()
	var result: Variant = _core_gateway.call("run_owner_import", _source_path)
	_import_running = false
	if result is Dictionary:
		_projection = result.duplicate(true)
		if _projection.get("state") == "UNAVAILABLE":
			_projection["state"] = "ERROR"
			_projection["disposition"] = "ERROR"
	else:
		_set_error("ERROR — OWNER_UPLOAD operation returned no structured result.")
	_render()


func snapshot() -> Dictionary:
	return _projection.duplicate(true)


func show_import() -> void:
	_render()


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Manual Pixel Art Import — immutable OWNER_UPLOAD source"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)

	_notice_label = Label.new()
	_notice_label.name = "SourceOnlyNotice"
	_notice_label.text = SOURCE_ONLY_NOTICE
	_notice_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_notice_label)

	var explanation := Label.new()
	explanation.text = "Select a local strict PNG. The selected file is stored byte-for-byte as a source artifact; no resize, palette, structural QA, candidate, solver, difficulty, or promotion operation is performed."
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(explanation)

	var path_row := HBoxContainer.new()
	var path_label := Label.new()
	path_label.text = "Selected local file"
	path_label.custom_minimum_size = Vector2(180, 0)
	path_row.add_child(path_label)
	_source_path_control = LineEdit.new()
	_source_path_control.name = "SourcePath"
	_source_path_control.placeholder_text = "FileDialog path or headless test path"
	_source_path_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	path_row.add_child(_source_path_control)
	var select_button := Button.new()
	select_button.name = "SelectLocalPng"
	select_button.text = "Select local PNG"
	select_button.pressed.connect(_on_select_pressed)
	path_row.add_child(select_button)
	var import_button := Button.new()
	import_button.name = "ImportSelectedSource"
	import_button.text = "Import source"
	import_button.pressed.connect(import_selected)
	path_row.add_child(import_button)
	add_child(path_row)

	_state_label = _make_label("State")
	_identity_label = _make_label("SourceIdentity")
	_origin_label = _make_label("Origin")
	_hash_label = _make_label("SourceHash")
	_dimensions_label = _make_label("OriginalDimensions")
	_stored_path_label = _make_label("StoredPath")

	_file_dialog = FileDialog.new()
	_file_dialog.name = "OwnerUploadFileDialog"
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.access = FileDialog.ACCESS_FILESYSTEM
	_file_dialog.filters = PackedStringArray(["*.png ; Strict PNG image"])
	_file_dialog.file_selected.connect(_on_file_selected)
	add_child(_file_dialog)


func _make_label(label_name: String) -> Label:
	var label := Label.new()
	label.name = label_name
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(label)
	return label


func _on_select_pressed() -> void:
	if _file_dialog != null:
		_file_dialog.popup_centered_ratio()


func _on_file_selected(path: String) -> void:
	set_source_path(path)


func _set_empty() -> void:
	_projection = {
		"operation": OWNER_UPLOAD_OPERATION,
		"state": "EMPTY",
		"disposition": "EMPTY",
		"reason": "EMPTY — select a local strict PNG source.",
	}
	_render()


func _set_error(message: String) -> void:
	_projection = {
		"operation": OWNER_UPLOAD_OPERATION,
		"state": "ERROR",
		"disposition": "ERROR",
		"error": message,
	}
	_render()


func _render() -> void:
	if _state_label == null:
		return
	var state := str(_projection.get("state", "EMPTY"))
	var message := str(_projection.get("error", _projection.get("reason", "")))
	_state_label.text = "Import state: %s%s" % [state, ("\n" + message) if not message.is_empty() else ""]
	_notice_label.text = str(_projection.get("source_only_notice", SOURCE_ONLY_NOTICE))
	if state in ["IMPORTED", "ALREADY_IMPORTED"]:
		_identity_label.text = "Source ID: %s" % _projection.get("source_id", "")
		_origin_label.text = "Origin: %s | status=%s | validation=%s" % [_projection.get("origin", ""), _projection.get("status", ""), _projection.get("validation_state", "")]
		_hash_label.text = "SHA-256: %s | bytes=%s | media=%s | filename=%s" % [_projection.get("source_sha256", ""), _projection.get("byte_length", ""), _projection.get("media_type", ""), _projection.get("original_filename", "")]
		_dimensions_label.text = "Original dimensions: %sx%s" % [_projection.get("original_width", ""), _projection.get("original_height", "")]
		_stored_path_label.text = "Immutable stored source: %s | record: %s" % [_projection.get("immutable_relative_path", ""), _projection.get("source_record_relative_path", "")]
	else:
		_identity_label.text = "Source ID: not available until a source is imported."
		_origin_label.text = "Origin: not available"
		_hash_label.text = "SHA-256: not available"
		_dimensions_label.text = "Original dimensions: not available"
		_stored_path_label.text = "Immutable stored source: not available"
