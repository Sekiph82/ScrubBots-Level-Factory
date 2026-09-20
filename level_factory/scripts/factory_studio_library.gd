@tool
class_name FactoryStudioLibrary
extends VBoxContainer

## Derived Source Art Library over re-verified canonical OWNER_UPLOAD records.

var _gateway: RefCounted
var _projection: Dictionary = {}
var _filtered: Array = []
var _search := ""
var _search_control: LineEdit
var _label_control: LineEdit
var _tags_control: LineEdit
var _state_label: Label
var _list_label: Label
var _detail_label: Label
var _selected_source_id := ""
var _last_save_result: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_set_empty()


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func show_library() -> void:
	_render()


func refresh_library() -> void:
	if _gateway == null or not _gateway.has_method("run_studio_extension"):
		_projection = {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "error": "UNAVAILABLE — canonical Library reader is not connected."}
	else:
		_projection = _gateway.call("run_studio_extension", "library-refresh", {})
	_filter()
	_render()


func set_search(value: String) -> void:
	_search = value.strip_edges()
	if _search_control != null:
		_search_control.text = _search
	_filter()
	_render()


func select_source(source_id: String) -> void:
	_selected_source_id = source_id
	_render()


func save_selected_metadata(label: String, tags: Array = []) -> void:
	if _selected_source_id.is_empty() or _gateway == null:
		return
	var result: Variant = _gateway.call("run_studio_extension", "library-save", {"source_id": _selected_source_id, "label": label, "tags": tags})
	_last_save_result = result.duplicate(true) if result is Dictionary else {}
	if result is Dictionary and str(result.get("source_id", "")) == _selected_source_id:
		refresh_library()


func snapshot() -> Dictionary:
	return {"projection": _projection.duplicate(true), "filtered_sources": _filtered.duplicate(true), "selected_source_id": _selected_source_id, "search": _search, "last_save_result": _last_save_result.duplicate(true)}


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Source Art Library — verified asset catalog"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)
	var notice := Label.new()
	notice.text = "ASSET CATALOG ONLY — source art is not training data and Library membership is not owner acceptance."
	notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(notice)
	var row := HBoxContainer.new()
	_search_control = LineEdit.new()
	_search_control.name = "LibrarySearch"
	_search_control.placeholder_text = "Search source ID, filename, label, tag, origin"
	_search_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_search_control.text_submitted.connect(set_search)
	row.add_child(_search_control)
	var refresh := Button.new()
	refresh.name = "RefreshLibrary"
	refresh.text = "Refresh"
	refresh.pressed.connect(refresh_library)
	row.add_child(refresh)
	add_child(row)
	_state_label = _make_label("LibraryState")
	_list_label = _make_label("LibrarySources")
	_detail_label = _make_label("LibraryDetail")
	_label_control = LineEdit.new()
	_label_control.name = "LibraryLabel"
	_label_control.placeholder_text = "Selected source label"
	add_child(_label_control)
	_tags_control = LineEdit.new()
	_tags_control.name = "LibraryTags"
	_tags_control.placeholder_text = "Comma-separated bounded tags"
	add_child(_tags_control)
	var save := Button.new()
	save.name = "SaveLibraryMetadata"
	save.text = "Save label/tags only"
	save.pressed.connect(func(): save_selected_metadata(_label_control.text, _tags_control.text.split(",", false)))
	add_child(save)


func _make_label(label_name: String) -> Label:
	var label := Label.new()
	label.name = label_name
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(label)
	return label


func _set_empty() -> void:
	_projection = {"state": "EMPTY", "disposition": "EMPTY", "sources": [], "invalid_sources": []}
	_filter()
	_render()


func _filter() -> void:
	var sources: Array = _projection.get("sources", []) if _projection is Dictionary else []
	_filtered = []
	for source in sources:
		var searchable := "%s %s %s %s %s" % [source.get("source_id", ""), source.get("original_filename", ""), source.get("origin", ""), source.get("catalog", {}).get("label", ""), " ".join(source.get("catalog", {}).get("tags", []))]
		if _search.is_empty() or searchable.to_lower().contains(_search.to_lower()):
			_filtered.append(source)
	if _selected_source_id.is_empty() and not _filtered.is_empty():
		_selected_source_id = str(_filtered[0].get("source_id", ""))


func _render() -> void:
	if _state_label == null:
		return
	var state := str(_projection.get("state", "EMPTY"))
	_state_label.text = "Library state: %s | invalid/quarantined=%s" % [state, _projection.get("invalid_sources", []).size()]
	var ids: Array[String] = []
	for source in _filtered:
		ids.append(str(source.get("source_id", "")))
	_list_label.text = "Verified sources: %s" % ", ".join(ids)
	var selected: Dictionary = {}
	for source in _filtered:
		if str(source.get("source_id", "")) == _selected_source_id:
			selected = source
	if selected.is_empty():
		_detail_label.text = "Selected source: NOT AVAILABLE"
	else:
		_detail_label.text = "Selected %s | origin=%s | sha256=%s | dimensions=%sx%s | state=%s/%s | label=%s | tags=%s | review=%s | palette=%s | derived_dimensions=%s | usages=%s | immutable=%s" % [selected.get("source_id", ""), selected.get("origin", ""), selected.get("source_sha256", ""), selected.get("original_width", ""), selected.get("original_height", ""), selected.get("status", ""), selected.get("validation_state", ""), selected.get("catalog", {}).get("label", ""), selected.get("catalog", {}).get("tags", []), selected.get("owner_review", {}).get("disposition", "NOT AVAILABLE"), selected.get("palette", {}).get("disposition", "NOT AVAILABLE"), selected.get("derived_dimensions", {}).get("disposition", "NOT AVAILABLE"), selected.get("usages", {}).get("disposition", "NOT AVAILABLE"), selected.get("immutable_source_path", "NOT AVAILABLE")]
