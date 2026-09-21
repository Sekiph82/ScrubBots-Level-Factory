@tool
class_name FactoryStudioSearch
extends VBoxContainer

var _gateway: RefCounted
var _query: LineEdit
var _collection: OptionButton
var _record_type: OptionButton
var _origin: LineEdit
var _review: OptionButton
var _qa: OptionButton
var _width: SpinBox
var _height: SpinBox
var _used_color_count: SpinBox
var _result: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func refresh_search() -> void:
	var selected := _collection.get_item_text(_collection.selected) if _collection != null else "ALL"
	var filters := {}
	if _record_type != null and _record_type.selected > 0: filters["record_type"] = _record_type.get_item_text(_record_type.selected)
	if _origin != null and not _origin.text.strip_edges().is_empty(): filters["origin"] = _origin.text.strip_edges()
	if _review != null and _review.selected > 0: filters["review"] = _review.get_item_text(_review.selected)
	if _qa != null and _qa.selected > 0: filters["qa"] = _qa.get_item_text(_qa.selected)
	if _width != null and _width.value > 0: filters["width"] = int(_width.value)
	if _height != null and _height.value > 0: filters["height"] = int(_height.value)
	if _used_color_count != null and _used_color_count.value > 0: filters["used_color_count"] = int(_used_color_count.value)
	_projection = _gateway.call("run_studio_extension", "discover", {"query": _query.text, "filters": filters, "collection": null if selected == "ALL" else selected}) if _gateway != null else {"state": "UNAVAILABLE"}
	_render()


func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_search() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "Search / Filter / Smart Collections — derived discovery"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var row := HBoxContainer.new()
	_query = LineEdit.new()
	_query.placeholder_text = "Search real source/candidate fields"
	_query.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(_query)
	_collection = OptionButton.new()
	for item in ["ALL", "Needs Review", "Owner Accepted", "Owner Rejected", "Imported Sources", "Ready for Production", "Unused in Campaign"]:
		_collection.add_item(item)
	row.add_child(_collection)
	_record_type = OptionButton.new(); _record_type.add_item("All record types"); _record_type.add_item("SOURCE"); _record_type.add_item("CANDIDATE"); row.add_child(_record_type)
	_origin = LineEdit.new(); _origin.placeholder_text = "Origin"; row.add_child(_origin)
	_review = OptionButton.new(); _review.add_item("All reviews"); _review.add_item("NEEDS_REVIEW"); _review.add_item("ACCEPT"); _review.add_item("REJECT"); row.add_child(_review)
	_qa = OptionButton.new(); _qa.add_item("All QA"); _qa.add_item("ACCEPT"); _qa.add_item("REJECT"); row.add_child(_qa)
	_width = SpinBox.new(); _width.min_value = 0; _width.max_value = 59; _width.allow_greater = false; _width.prefix = "W="; row.add_child(_width)
	_height = SpinBox.new(); _height.min_value = 0; _height.max_value = 59; _height.allow_greater = false; _height.prefix = "H="; row.add_child(_height)
	_used_color_count = SpinBox.new(); _used_color_count.min_value = 0; _used_color_count.max_value = 16; _used_color_count.allow_greater = false; _used_color_count.prefix = "Colors="; row.add_child(_used_color_count)
	var refresh := Button.new()
	refresh.text = "Refresh"
	refresh.pressed.connect(refresh_search)
	row.add_child(refresh)
	add_child(row)
	_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)


func _render() -> void:
	if _result == null: return
	var records: Array = _projection.get("records", [])
	var ids: Array[String] = []
	for record in records: ids.append(str(record.get("record_id", "")))
	_result.text = "Discovery: %s | collection=%s | records=%s | %s" % [_projection.get("state", "EMPTY"), _projection.get("collection", ""), ", ".join(ids), _projection.get("reason", "No membership list is persisted; this is a fresh derived query." )]
