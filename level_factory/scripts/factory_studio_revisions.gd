@tool
class_name FactoryStudioRevisions
extends VBoxContainer

var _gateway: RefCounted
var _candidate: LineEdit
var _revision: LineEdit
var _compare_left: LineEdit
var _compare_right: LineEdit
var _result: Label
var _editor: Node

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Manual Edit Revisions — immutable lineage"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var notice := Label.new(); notice.text = "Save/undo/restore selects explicit revisions; source bundles and prior revisions are never overwritten. Revalidation is bound to the working-grid hash."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
		var row := HBoxContainer.new(); _candidate = LineEdit.new(); _candidate.placeholder_text = "candidate ID"; _candidate.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate); var list := Button.new(); list.text = "List revisions"; list.pressed.connect(list_revisions); row.add_child(list); var save := Button.new(); save.text = "Save Revision"; save.pressed.connect(save_revision); row.add_child(save); add_child(row)
		var revision_row := HBoxContainer.new(); _revision = LineEdit.new(); _revision.placeholder_text = "revision ID"; revision_row.add_child(_revision); var select := Button.new(); select.text = "Select / Undo"; select.pressed.connect(select_revision); revision_row.add_child(select); var restore := Button.new(); restore.text = "Restore Source"; restore.pressed.connect(restore_source); revision_row.add_child(restore); add_child(revision_row)
		var compare_row := HBoxContainer.new(); _compare_left = LineEdit.new(); _compare_left.placeholder_text = "left revision"; compare_row.add_child(_compare_left); _compare_right = LineEdit.new(); _compare_right.placeholder_text = "right revision"; compare_row.add_child(_compare_right); var compare := Button.new(); compare.text = "Compare"; compare.pressed.connect(compare_revisions); compare_row.add_child(compare); add_child(compare_row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)
		_result.text = "Revision history is available from the canonical manual editor integration."

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func configure_editor(editor: Node) -> void: _editor = editor
func set_candidate_id(candidate_id: String) -> void:
	if _candidate != null: _candidate.text = candidate_id
func set_revision_id(revision_id: String) -> void:
	if _revision != null: _revision.text = revision_id
func set_compare_revisions(left_id: String, right_id: String) -> void:
	if _compare_left != null: _compare_left.text = left_id
	if _compare_right != null: _compare_right.text = right_id
func list_revisions() -> void:
	var candidate_id := _candidate.text.strip_edges() if _candidate != null else ""
	if candidate_id.is_empty() and _editor != null: candidate_id = str(_editor.call("snapshot").get("source_candidate_id", ""))
	_projection = _gateway.call("run_studio_extension", "revision-list", {"candidate_id": candidate_id}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "Revision operation: %s\nCount: %s" % [_projection.get("disposition", _projection.get("state", "UNAVAILABLE")), (_projection.get("revisions", []) as Array).size()]
func save_revision() -> Dictionary:
	if _gateway == null or _editor == null: _projection = {"state": "UNAVAILABLE", "reason": "A real manual editor source is required."}; return _projection
	var editor_state: Dictionary = _editor.call("snapshot")
	var candidate_id := str(editor_state.get("source_candidate_id", "")); var cells: Array = _editor.call("working_logical_cells_snapshot")
	var revisions: Dictionary = _gateway.call("run_studio_extension", "revision-list", {"candidate_id": candidate_id})
	var existing: Array = revisions.get("revisions", [])
	var selected_parent := _revision.text.strip_edges() if _revision != null else ""
	var parent_id = selected_parent if not selected_parent.is_empty() else (existing.back().get("revision_id") if not existing.is_empty() else null)
	_projection = _gateway.call("run_studio_extension", "revision-create", {"candidate_id": candidate_id, "width": int(editor_state.get("logical_width", 0)), "height": int(editor_state.get("logical_height", 0)), "cells": cells, "parent_revision_id": parent_id, "change_summary": "Manual editor working-copy snapshot", "edit_operations": []})
	_result.text = "Revision save: %s" % _projection.get("disposition", _projection.get("state", "UNAVAILABLE"))
	return _projection
func select_revision() -> void:
	var candidate_id := _candidate.text.strip_edges(); var revision_id := _revision.text.strip_edges()
	_projection = _gateway.call("run_studio_extension", "revision-load", {"candidate_id": candidate_id, "revision_id": revision_id}) if _gateway != null else {"state": "UNAVAILABLE"}
	if _projection.get("state") == "SUCCESS" and _editor != null:
		var value: Dictionary = _projection.get("revision", {}); _editor.call("load_revision_cells", int(value.get("width", 0)), int(value.get("height", 0)), value.get("cells", []))
	_result.text = "Revision select/undo: %s" % _projection.get("disposition", _projection.get("state", "UNAVAILABLE"))
func restore_source() -> void:
	if _editor != null: _editor.call("reset_to_source"); _projection = {"state": "SUCCESS", "disposition": "SOURCE_RESTORED", "source_mutation": "FORBIDDEN"}
	else: _projection = {"state": "UNAVAILABLE"}
	_result.text = "Restore Source: %s" % _projection.get("disposition", _projection.get("state", "UNAVAILABLE"))
func compare_revisions() -> void:
	_projection = _gateway.call("run_studio_extension", "revision-compare", {"candidate_id": _candidate.text.strip_edges(), "left_revision_id": _compare_left.text.strip_edges(), "right_revision_id": _compare_right.text.strip_edges()}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "Revision compare: %s" % _projection.get("disposition", _projection.get("state", "UNAVAILABLE"))
func show_revisions() -> void: pass
var _projection: Dictionary = {}
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "source_mutation": "FORBIDDEN", "projection": _projection.duplicate(true)}
