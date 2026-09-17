@tool
class_name FactoryStudioArtRevalidation
extends VBoxContainer

## Narrow manual-art structural revalidation over the existing memory-only editor.
## Canonical Python owns bundle validation, policy reuse, hashing, and quality QA.

const NOT_REQUIRED := "NOT_REQUIRED"
const AVAILABLE := "AVAILABLE"
const RUNNING := "RUNNING"
const STALE := "STALE"
const ERROR := "ERROR"
const UNAVAILABLE := "UNAVAILABLE"
const SCOPE := "STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION"
const SOLVER_LIMITATION := "Solver: UNAVAILABLE pending M03."
const DIFFICULTY_LIMITATION := "Measured difficulty: UNAVAILABLE pending M04."
const UNIFIED_LIMITATION := "Unified validation: UNAVAILABLE pending M05."
const OWNER_LIMITATION := "QA PASS != OWNER ACCEPT; structural ACCEPT does not promote the edited working copy."
const REQUEST_SCHEMA := "scrubbots-studio-manual-art-revalidation"
const REQUEST_VERSION := 1
const OPERATION := "manual-art-structural-revalidation"
const TRANSPORT_REQUEST_PATH := "res://output/.lf06-008-revalidation/request.json"

var _editor: Node
var _gateway: RefCounted
var _state := UNAVAILABLE
var _last_result: Dictionary = {}
var _last_evaluated_cells: Array[String] = []
var _result_current := false
var _error_message := ""
var _source_bytes_before: Dictionary = {}
var _source_bytes_after: Dictionary = {}
var _source_bytes_unchanged := false
var _heading: Label
var _state_label: Label
var _result_label: Label
var _limitations_label: Label
var _revalidate_button: Button


func _ready() -> void:
	if get_child_count() == 0:
		_build_panel()
	_refresh_lifecycle()


func _process(_delta: float) -> void:
	_refresh_lifecycle()


func configure_editor(editor: Node) -> void:
	_editor = editor
	_refresh_lifecycle()


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway
	_refresh_lifecycle()


func refresh_from_editor() -> void:
	_refresh_lifecycle()


func snapshot() -> Dictionary:
	_refresh_lifecycle()
	var editor_snapshot := _editor_snapshot()
	return {
		"state": _state,
		"scope": SCOPE,
		"operation": OPERATION,
		"revalidation_available": _state == AVAILABLE,
		"result_current": _result_current and _state in ["STRUCTURAL ACCEPT", "STRUCTURAL REJECT"],
		"source_candidate_id": str(_last_result.get("source_candidate_id", editor_snapshot.get("source_candidate_id", ""))),
		"source_grid_hash": str(_last_result.get("source_grid_hash", "")),
		"working_grid_hash": str(_last_result.get("working_grid_hash", "")),
		"width": int(_last_result.get("width", editor_snapshot.get("logical_width", 0))),
		"height": int(_last_result.get("height", editor_snapshot.get("logical_height", 0))),
		"dirty_cell_count": int(_last_result.get("dirty_cell_count", editor_snapshot.get("dirty_cell_count", 0))),
		"disposition": str(_last_result.get("disposition", _state)),
		"rejection_codes": _last_result.get("rejection_codes", []),
		"quality_schema": str(_last_result.get("quality_schema", "")),
		"quality_schema_version": int(_last_result.get("quality_schema_version", 0)),
		"quality_policy_version": str(_last_result.get("quality_policy_version", "")),
		"source_quality_policy": _last_result.get("source_quality_policy", {}),
		"source_bytes_unchanged": _source_bytes_unchanged,
		"source_file_sha256_before": _source_bytes_before.duplicate(true),
		"source_file_sha256_after": _source_bytes_after.duplicate(true),
		"error": _error_message,
		"result": _last_result.duplicate(true),
	}


func _build_panel() -> void:
	_heading = Label.new()
	_heading.name = "RevalidationHeading"
	_heading.text = "Manual artwork structural revalidation"
	_heading.add_theme_font_size_override("font_size", 16)
	add_child(_heading)

	var scope_label := Label.new()
	scope_label.name = "RevalidationScope"
	scope_label.text = SCOPE
	scope_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(scope_label)

	_state_label = Label.new()
	_state_label.name = "RevalidationState"
	_state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_state_label)

	_result_label = Label.new()
	_result_label.name = "RevalidationResult"
	_result_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_result_label)

	_limitations_label = Label.new()
	_limitations_label.name = "RevalidationLimitations"
	_limitations_label.text = "%s\n%s\n%s\n%s" % [SOLVER_LIMITATION, DIFFICULTY_LIMITATION, UNIFIED_LIMITATION, OWNER_LIMITATION]
	_limitations_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_limitations_label)

	_revalidate_button = Button.new()
	_revalidate_button.name = "RevalidateManualArtwork"
	_revalidate_button.text = "Revalidate manual artwork"
	_revalidate_button.pressed.connect(_on_revalidate_pressed)
	add_child(_revalidate_button)


func _on_revalidate_pressed() -> void:
	if _editor == null or _gateway == null or not _gateway.has_method("run_manual_art_revalidation"):
		_state = UNAVAILABLE
		_error_message = "UNAVAILABLE — canonical Python Factory Core revalidation bridge is not connected."
		_refresh_presentation()
		return
	var editor_snapshot := _editor_snapshot()
	if str(editor_snapshot.get("state", "")) != "DIRTY" or int(editor_snapshot.get("dirty_cell_count", 0)) <= 0:
		_state = NOT_REQUIRED
		_error_message = "NOT_REQUIRED — a CLEAN working copy cannot masquerade as a manual revalidation."
		_result_current = false
		_last_result = {}
		_refresh_presentation()
		return
	var source_cells: Array[String] = _editor.call("source_logical_cells_snapshot")
	var working_cells: Array[String] = _editor.call("working_logical_cells_snapshot")
	if source_cells.is_empty() or working_cells.is_empty():
		_state = ERROR
		_error_message = "ERROR — editor logical cells are not a complete canonical C01..C16 source/working snapshot."
		_refresh_presentation()
		return
	var source_bundle_path := str(editor_snapshot.get("source_bundle_path", ""))
	var source_artwork_sha256 := str(editor_snapshot.get("source_artwork_sha256", ""))
	_source_bytes_before = _source_file_hashes(source_bundle_path)
	if _source_bytes_before.size() != 3:
		_state = ERROR
		_error_message = "ERROR — source bundle bytes could not be captured before revalidation."
		_refresh_presentation()
		return
	_state = RUNNING
	_error_message = ""
	_result_current = false
	_refresh_presentation()
	var request := {
		"schema": REQUEST_SCHEMA,
		"schema_version": REQUEST_VERSION,
		"operation": OPERATION,
		"source_bundle_path": source_bundle_path,
		"source_candidate_id": str(editor_snapshot.get("source_candidate_id", "")),
		"source_artwork_sha256": source_artwork_sha256,
		"source_width": int(editor_snapshot.get("logical_width", 0)),
		"source_height": int(editor_snapshot.get("logical_height", 0)),
		"source_cells": source_cells,
		"working_width": int(editor_snapshot.get("logical_width", 0)),
		"working_height": int(editor_snapshot.get("logical_height", 0)),
		"working_cells": working_cells,
		"dirty_cell_count": int(editor_snapshot.get("dirty_cell_count", 0)),
	}
	if not _write_transport_request(request):
		_state = ERROR
		_error_message = "ERROR — manual artwork structural revalidation transport request could not be created."
		_refresh_presentation()
		return
	var result_variant: Variant = _gateway.call("run_manual_art_revalidation", TRANSPORT_REQUEST_PATH)
	_cleanup_transport_request()
	var result: Dictionary = result_variant if result_variant is Dictionary else {
		"state": "ERROR",
		"disposition": "ERROR",
		"error": "ERROR — revalidation bridge returned no structured result.",
	}
	_source_bytes_after = _source_file_hashes(source_bundle_path)
	_source_bytes_unchanged = _source_bytes_before == _source_bytes_after and _source_bytes_after.size() == 3
	if not _source_bytes_unchanged:
		_state = ERROR
		_error_message = "ERROR — canonical source bundle bytes changed during revalidation."
		_last_result = result
		_last_evaluated_cells = []
		_refresh_presentation()
		return
	_last_result = result.duplicate(true)
	_error_message = str(result.get("error", result.get("reason", "")))
	if str(result.get("state", "")) == "RESULT" and str(result.get("source_candidate_id", "")) == str(editor_snapshot.get("source_candidate_id", "")) and str(result.get("working_grid_hash", "")).length() == 64:
		_last_evaluated_cells = working_cells.duplicate()
		_result_current = true
		_state = "STRUCTURAL ACCEPT" if str(result.get("disposition", "")) == "ACCEPT" else "STRUCTURAL REJECT"
	else:
		_result_current = false
		_state = UNAVAILABLE if str(result.get("state", "")) == "UNAVAILABLE" else ERROR
	_refresh_presentation()


func _refresh_lifecycle() -> void:
	if _editor == null:
		_state = UNAVAILABLE
		_refresh_presentation()
		return
	var editor_snapshot := _editor_snapshot()
	var editor_state := str(editor_snapshot.get("state", "EMPTY"))
	var cells: Array[String] = _editor.call("working_logical_cells_snapshot")
	if editor_state == "CLEAN" or editor_state == "EMPTY":
		if _result_current:
			_last_result = {}
			_last_evaluated_cells = []
			_result_current = false
		_state = NOT_REQUIRED
		_error_message = "NOT_REQUIRED — no current DIRTY manual artwork edit is present."
	elif editor_state == "ERROR":
		_state = ERROR
		_error_message = str(editor_snapshot.get("error", "ERROR — editor source is not safely loaded."))
		_result_current = false
	elif editor_state == "DIRTY":
		if _result_current and cells != _last_evaluated_cells:
			_state = STALE
			_error_message = "STALE — working artwork changed after the recorded structural result; revalidate again."
		elif not _result_current and _state != RUNNING:
			_state = AVAILABLE if _gateway != null and _gateway.has_method("run_manual_art_revalidation") else UNAVAILABLE
	_refresh_presentation()


func _refresh_presentation() -> void:
	if _state_label == null:
		return
	_state_label.text = "Manual revalidation state: %s\n%s" % [_state, _error_message]
	if _result_label != null:
		if _last_result.is_empty():
			_result_label.text = "No current structural result."
		else:
			_result_label.text = "Result: %s | source candidate=%s | source grid=%s | working grid=%s | dirty cells=%s | policy=%s | rejection_codes=%s" % [
				_last_result.get("disposition", _last_result.get("state", "")),
				_last_result.get("source_candidate_id", ""),
				_last_result.get("source_grid_hash", ""),
				_last_result.get("working_grid_hash", ""),
				_last_result.get("dirty_cell_count", ""),
				_last_result.get("quality_policy_version", ""),
				_last_result.get("rejection_codes", []),
			]
	if _revalidate_button != null:
		_revalidate_button.disabled = _state != AVAILABLE


func _editor_snapshot() -> Dictionary:
	if _editor == null or not _editor.has_method("snapshot"):
		return {}
	var value: Variant = _editor.call("snapshot")
	return value if value is Dictionary else {}


func _source_file_hashes(bundle_path: String) -> Dictionary:
	if bundle_path.is_empty():
		return {}
	var hashes: Dictionary = {}
	for file_name in ["artwork.png", "artwork.json", "metadata.json"]:
		var path := bundle_path.path_join(file_name)
		var bytes := FileAccess.get_file_as_bytes(path)
		if bytes.is_empty():
			return {}
		hashes[file_name] = _sha256(bytes)
	return hashes


func _write_transport_request(request: Dictionary) -> bool:
	var transport_root := ProjectSettings.globalize_path("res://output/.lf06-008-revalidation")
	DirAccess.make_dir_recursive_absolute(transport_root)
	var request_file := FileAccess.open(ProjectSettings.globalize_path(TRANSPORT_REQUEST_PATH), FileAccess.WRITE)
	if request_file == null:
		_cleanup_transport_request()
		return false
	request_file.store_string(JSON.stringify(request))
	request_file.close()
	return true


func _cleanup_transport_request() -> void:
	var request_path := ProjectSettings.globalize_path(TRANSPORT_REQUEST_PATH)
	DirAccess.remove_absolute(request_path)
	DirAccess.remove_absolute(ProjectSettings.globalize_path("res://output/.lf06-008-revalidation"))


func _sha256(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()
