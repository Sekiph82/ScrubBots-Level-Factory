@tool
class_name FactoryStudioSearch
extends VBoxContainer

var _gateway: RefCounted
var _query: LineEdit
var _collection: OptionButton
var _result: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func refresh_search() -> void:
	var selected := _collection.get_item_text(_collection.selected) if _collection != null else "ALL"
	_projection = _gateway.call("run_studio_extension", "discover", {"query": _query.text, "collection": null if selected == "ALL" else selected}) if _gateway != null else {"state": "UNAVAILABLE"}
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
