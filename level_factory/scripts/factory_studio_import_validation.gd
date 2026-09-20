@tool
class_name FactoryStudioImportValidation
extends VBoxContainer

var _gateway: RefCounted
var _source_id := ""
var _source_control: LineEdit
var _state_label: Label
var _facts_label: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_set_empty()


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func set_source_id(source_id: String) -> void:
	_source_id = source_id.strip_edges()
	if _source_control != null: _source_control.text = _source_id


func run_validation() -> void:
	_source_id = _source_control.text.strip_edges() if _source_control != null else _source_id
	if _source_id.is_empty() or _gateway == null or not _gateway.has_method("run_studio_extension"):
		_projection = {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "error": "UNAVAILABLE — select a verified OWNER_UPLOAD source."}
	else:
		_projection = _gateway.call("run_studio_extension", "validate-source", {"source_id": _source_id})
	_render()


func snapshot() -> Dictionary:
	return _projection.duplicate(true)


func show_validation() -> void:
	_render()


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Import Validation Wizard — canonical analysis over immutable source"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)
	var notice := Label.new()
	notice.text = "The wizard interprets exact source pixels. DERIVED_ARTIFACT_REQUIRED names CELL_MAJORITY_V1 / PALETTE_SNAP_V1 without silently transforming the source."
	notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(notice)
	var row := HBoxContainer.new()
	_source_control = LineEdit.new()
	_source_control.name = "ValidationSourceId"
	_source_control.placeholder_text = "owner-upload-<sha256>"
	_source_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(_source_control)
	var button := Button.new()
	button.name = "RunImportValidation"
	button.text = "Run / Re-run validation"
	button.pressed.connect(run_validation)
	row.add_child(button)
	add_child(row)
	_state_label = Label.new()
	_state_label.name = "ValidationState"
	_state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_state_label)
	_facts_label = Label.new()
	_facts_label.name = "ValidationFacts"
	_facts_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_facts_label)


func _set_empty() -> void:
	_projection = {"state": "EMPTY", "disposition": "EMPTY", "reason": "Select a verified OWNER_UPLOAD source."}
	_render()


func _render() -> void:
	if _state_label == null: return
	var state := str(_projection.get("state", _projection.get("disposition", "EMPTY")))
	_state_label.text = "Validation: %s | source=%s\n%s" % [state, _projection.get("source_id", _source_id), _projection.get("error", _projection.get("reason", ""))]
	if _projection.has("original_dimensions"):
		var dimensions: Dictionary = _projection.get("original_dimensions", {})
		var palette: Dictionary = _projection.get("palette", {})
		var alpha: Dictionary = _projection.get("alpha", {})
		var structural: Dictionary = _projection.get("structural", {})
		_facts_label.text = "format=%s | dimensions=%sx%s legal=%s | logical=%s | C-ID colors=%s used=%s foreign=%s | alpha transparent=%s semi=%s | structural=%s codes=%s | solver=NOT AVAILABLE | difficulty=NOT AVAILABLE | owner=NOT AVAILABLE" % [_projection.get("format", {}).get("disposition", "NOT AVAILABLE"), dimensions.get("width", ""), dimensions.get("height", ""), _projection.get("legal_logical_dimensions", false), _projection.get("logical_dimension_status", ""), palette.get("canonical_ids", []), palette.get("used_color_count", ""), palette.get("foreign_color_count", ""), alpha.get("transparent_count", ""), alpha.get("semi_alpha_count", ""), structural.get("disposition", ""), structural.get("rejection_codes", [])]
	else:
		_facts_label.text = "Canonical facts: NOT AVAILABLE until validation runs."
