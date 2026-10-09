@tool
extends Control

@export var pixel_art_master: Texture2D
@export var level_factory_master: Texture2D
@export var release_pool_master: Texture2D

var _gateway: RefCounted
var _canvas: TextureRect
var _status: Label
var _file_dialog: FileDialog
var _level_dialog: ConfirmationDialog
var _level_number_input: SpinBox
var _level_number_label: Label
var _screen := "PIXEL ART"
var _last_candidate_id := ""
var _last_source_id := ""
var _last_pipeline: Dictionary = {}
var _selected_release_ids: Array[String] = []
var _release_pool: Dictionary = {}
var _operation_running := false
var _column_count := 4
var _level_number := 11


func _ready() -> void:
	_canvas = get_node_or_null("MasterCanvas") as TextureRect
	_status = get_node_or_null("Status") as Label
	_file_dialog = get_node_or_null("FileDialog") as FileDialog
	if _canvas == null or _file_dialog == null:
		return
	_file_dialog.file_selected.connect(_on_file_selected)
	_file_dialog.files_selected.connect(_on_files_selected)
	_level_dialog = ConfirmationDialog.new()
	_level_dialog.title = "Level Settings"
	_level_dialog.dialog_text = "Level Number"
	_level_number_input = SpinBox.new()
	_level_number_input.min_value = 1
	_level_number_input.max_value = 999
	_level_number_input.step = 1
	_level_number_input.value = _level_number
	_level_number_input.custom_minimum_size = Vector2(220, 40)
	_level_dialog.add_child(_level_number_input)
	_level_dialog.confirmed.connect(_save_level_number)
	add_child(_level_dialog)
	_level_number_label = Label.new()
	_level_number_label.position = Vector2(187, 353)
	_level_number_label.size = Vector2(150, 28)
	_level_number_label.add_theme_color_override("font_color", Color.WHITE)
	_level_number_label.add_theme_font_size_override("font_size", 16)
	_level_number_label.visible = false
	add_child(_level_number_label)
	_build_hotspots()
	_show_screen(_screen)


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func active_master() -> String:
	return _screen


func master_names() -> Array[String]:
	return ["PIXEL ART", "LEVEL FACTORY", "RELEASE POOL"]


func _build_hotspots() -> void:
	# Header tabs are clickable overlays aligned to the owner-approved master.
	_hotspot("PixelArtTab", Rect2(365, 22, 255, 72), _show_screen.bind("PIXEL ART"))
	_hotspot("LevelFactoryTab", Rect2(633, 22, 270, 72), _show_screen.bind("LEVEL FACTORY"))
	_hotspot("ReleasePoolTab", Rect2(918, 22, 270, 72), _show_screen.bind("RELEASE POOL"))
	# PIXEL ART actions and Batch-CSV path.
	_hotspot("GeneratePixelArt", Rect2(27, 462, 334, 49), _generate_art)
	_hotspot("BatchCsvSelect", Rect2(199, 155, 161, 43), _open_batch_csv)
	_hotspot("RunBatch", Rect2(27, 631, 334, 50), _run_batch)
	_hotspot("Regenerate", Rect2(1208, 452, 294, 48), _generate_art)
	_hotspot("EditPrompt", Rect2(1208, 506, 294, 48), _edit_prompt)
	_hotspot("AddToLevelFactory", Rect2(1208, 560, 294, 48), _send_to_level_factory)
	# LEVEL FACTORY: select artwork, set 3/4/5 columns, run real pipeline,
	# then record append-only owner acceptance or rejection for its candidate.
	_hotspot("SelectArtwork", Rect2(42, 165, 95, 100), _open_files.bind(false))
	_hotspot("LevelNumber", Rect2(172, 346, 190, 38), _edit_level_number)
	_hotspot("SupplyColumns3", Rect2(172, 392, 56, 40), _set_columns.bind(3))
	_hotspot("SupplyColumns4", Rect2(238, 392, 56, 40), _set_columns.bind(4))
	_hotspot("SupplyColumns5", Rect2(304, 392, 56, 40), _set_columns.bind(5))
	_hotspot("RunLevelPipeline", Rect2(26, 803, 335, 52), _run_level_pipeline)
	_hotspot("AcceptLevel", Rect2(1207, 686, 138, 50), _review_candidate.bind("ACCEPT"))
	_hotspot("RejectLevel", Rect2(1360, 686, 138, 50), _review_candidate.bind("REJECT"))
	# RELEASE POOL uses canonical pool, campaign, and staging operations.
	_hotspot("RefreshReleasePool", Rect2(27, 188, 330, 46), _refresh_release_pool)
	_hotspot("SelectReleaseLevel", Rect2(25, 261, 335, 68), _select_first_release)
	_hotspot("PreflightRelease", Rect2(1207, 485, 291, 40), _preflight_release)
	_hotspot("UploadToStaging", Rect2(1207, 648, 291, 54), _publish_staging)


func _hotspot(node_name: String, rect: Rect2, action: Callable) -> void:
	var button := Button.new()
	button.name = node_name
	button.position = rect.position
	button.size = rect.size
	button.flat = true
	button.focus_mode = Control.FOCUS_NONE
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_stylebox_override("normal", _transparent_style())
	button.add_theme_stylebox_override("hover", _transparent_style())
	button.add_theme_stylebox_override("pressed", _transparent_style())
	button.add_theme_stylebox_override("focus", _transparent_style())
	button.pressed.connect(action)
	add_child(button)


func _transparent_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0, 0, 0, 0)
	style.border_color = Color(0, 0, 0, 0)
	return style


func _show_screen(name: String) -> void:
	if name not in master_names() or _canvas == null:
		return
	_screen = name
	var texture: Texture2D = pixel_art_master if name == "PIXEL ART" else level_factory_master if name == "LEVEL FACTORY" else release_pool_master
	if texture == null:
		_report("Owner-approved screen master is unavailable: " + name)
		return
	_canvas.texture = texture
	if _status != null:
		_status.visible = false
	if name == "RELEASE POOL":
		_refresh_release_pool(false)


func _report(message: String) -> void:
	if _status == null:
		return
	_status.text = message
	_status.visible = true


func _open_files(multiple: bool) -> void:
	if _file_dialog == null:
		return
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILES if multiple else FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.title = "Select artwork PNG"
	_file_dialog.clear_filters()
	_file_dialog.add_filter("*.png ; PNG image")
	_file_dialog.popup_centered_ratio(0.72)


func _open_batch_csv() -> void:
	if _file_dialog == null:
		return
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.title = "Select artwork batch CSV"
	_file_dialog.clear_filters()
	_file_dialog.add_filter("*.csv ; CSV batch")
	_file_dialog.popup_centered_ratio(0.72)


func _on_file_selected(path: String) -> void:
	if path.get_extension().to_lower() == "csv":
		_generate_batch_csv(path)
		return
	if _screen == "LEVEL FACTORY":
		var imported: Dictionary = _extension("batch-import", {"paths": [path]})
		var items: Array = imported.get("items", [])
		if not items.is_empty():
			_last_source_id = str(items[0].get("source_id", ""))
			if _last_source_id.is_empty():
				_report(str(items[0].get("state", imported.get("state", "Import unavailable"))))
			else:
				_last_candidate_id = ""
				_report("Artwork selected. Run the canonical pipeline to continue.")
		else:
			_report(str(imported.get("reason", imported.get("error", "Artwork import unavailable."))))
	else:
		var imported: Dictionary = _extension("batch-import", {"paths": [path]})
		_report(str(imported.get("state", imported.get("reason", "Artwork imported."))))


func _on_files_selected(paths: PackedStringArray) -> void:
	var result := _extension("batch-import", {"paths": Array(paths)})
	_report("Batch import: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _generate_art() -> void:
	if _gateway == null or _operation_running:
		return
	_operation_running = true
	var seed := "pixel-art-%d" % Time.get_unix_time_from_system()
	var output := "res://output/exact-three-master/%s" % seed
	var result: Dictionary = _gateway.call("run_action", "Generate", {
		"width": 32, "height": 32, "seed": seed, "mode": "MASK",
		"background_intent": "TRANSPARENT",
	}, output)
	_last_candidate_id = str(result.get("candidate_id", ""))
	_report("Generated %s · %s" % [_last_candidate_id, str(result.get("state", "UNAVAILABLE"))])
	_operation_running = false


func _run_batch() -> void:
	_open_batch_csv()


func _generate_batch_csv(path: String) -> void:
	if _gateway == null or _operation_running:
		return
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_report("Could not read the selected CSV file.")
		return
	var expected := PackedStringArray(["seed", "width", "height", "mode", "background_intent"])
	var header := file.get_csv_line()
	if header != expected:
		_report("CSV columns must be seed,width,height,mode,background_intent.")
		return
	_operation_running = true
	var succeeded := 0
	var row_number := 0
	var batch_id := str(Time.get_unix_time_from_system())
	while not file.eof_reached():
		var row := file.get_csv_line()
		if row.size() == 1 and row[0].strip_edges().is_empty():
			continue
		row_number += 1
		if row_number > 100:
			_report("CSV batch stopped at the 100-row owner limit.")
			break
		if row.size() != expected.size():
			_report("CSV row %d has the wrong number of fields." % row_number)
			break
		var seed := row[0].strip_edges()
		var width := int(row[1]) if row[1].is_valid_int() else 0
		var height := int(row[2]) if row[2].is_valid_int() else 0
		var mode := row[3].strip_edges()
		var background := row[4].strip_edges()
		if seed.is_empty() or width < 20 or width > 59 or height < 20 or height > 59:
			_report("CSV row %d has an invalid seed or logical dimensions." % row_number)
			break
		var output := "res://output/exact-three-master/batch-%s-%03d" % [batch_id, row_number]
		var result: Dictionary = _gateway.call("run_action", "Generate", {
			"seed": seed, "width": width, "height": height, "mode": mode,
			"background_intent": background,
		}, output)
		if result.get("state") != "SUCCESS":
			_report("CSV row %d: %s" % [row_number, str(result.get("reason", result.get("state", "FAILED")))])
			break
		_last_candidate_id = str(result.get("candidate_id", _last_candidate_id))
		succeeded += 1
	_operation_running = false
	if succeeded == row_number and row_number > 0:
		_report("Batch complete: %d artwork(s) generated." % succeeded)
	file.close()


func _edit_prompt() -> void:
	_report("Prompt-based generation is unavailable in the offline Factory Core. Generate uses the canonical local pixel generator.")


func _send_to_level_factory() -> void:
	_show_screen("LEVEL FACTORY")
	if _last_candidate_id.is_empty():
		_report("Generate or select a candidate first.")
	else:
		_report("Candidate %s selected. Choose supply columns and run the pipeline." % _last_candidate_id)


func _run_level_pipeline() -> void:
	if _gateway == null or _operation_running:
		return
	if _last_candidate_id.is_empty() and _last_source_id.is_empty():
		_report("Select or generate a candidate first.")
		return
	_operation_running = true
	var request := {"column_count": _column_count, "level_number": _level_number, "game_project": OS.get_environment("SCRUBBOTS_PROJECT")}
	var pipeline_request := {"source_id": _last_source_id, "request": request} if not _last_source_id.is_empty() else {"candidate_id": _last_candidate_id, "request": request}
	var result: Dictionary = _extension("pipeline", pipeline_request)
	_last_pipeline = result
	if not str(result.get("derived_candidate_id", "")).is_empty():
		_last_candidate_id = str(result["derived_candidate_id"])
	_report("Pipeline %s · %s" % [str(result.get("disposition", result.get("state", "UNKNOWN"))), str(result.get("run_id", ""))])
	_operation_running = false


func _set_columns(columns: int) -> void:
	_column_count = columns if columns in [3, 4, 5] else 4
	_report("Supply columns: %d" % _column_count)


func _edit_level_number() -> void:
	_level_number_input.value = _level_number
	_level_dialog.popup_centered()


func _save_level_number() -> void:
	_level_number = int(_level_number_input.value)
	_level_number_label.text = str(_level_number)
	_level_number_label.visible = _level_number != 11
	_report("Level number: %d" % _level_number)


func _review_candidate(disposition: String) -> void:
	if _last_candidate_id.is_empty():
		_report("Select a candidate before recording owner review.")
		return
	if disposition == "ACCEPT":
		var primary: Dictionary = _last_pipeline.get("primary", {})
		if str(_last_pipeline.get("disposition", "")) != "READY" or str(primary.get("state", "")) != "READY":
			_report("Accept is available only after the canonical solver, replay, Difficulty V1, and QA pipeline is READY.")
			return
	var result := _extension("owner-review", {"candidate_id": _last_candidate_id, "disposition": disposition})
	_report("Owner %s · %s" % [disposition, str(result.get("review_id", result.get("state", "UNAVAILABLE")))])
	if disposition == "ACCEPT":
		_refresh_release_pool()


func _refresh_release_pool(show_status: bool = true) -> void:
	_release_pool = _extension("release-pool", {})
	if show_status:
		_report("Ready levels: %s" % str(_release_pool.get("pool_size", 0)))


func _select_first_release() -> void:
	var entries: Array = _release_pool.get("entries", [])
	if entries.is_empty():
		_report("No owner-accepted READY level is available in the Release Pool.")
		return
	var selected: Array[String] = []
	for entry in entries.slice(0, 3):
		var id := str(entry.get("candidate_id", ""))
		if not id.is_empty():
			selected.append(id)
	_selected_release_ids = selected
	_report("Selected %d owner-accepted Release Pool level(s)" % selected.size())


func _preflight_release() -> void:
	if _selected_release_ids.is_empty():
		_report("Select an owner-accepted READY level first.")
		return
	var result := _extension("scrubbots-publish", {
		"action": "preflight", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release", "content_version": 2,
		"created_at_utc": Time.get_datetime_string_from_system(true, false) + "Z",
	})
	_release_pool["publish_preflight"] = result
	_report("Publish preflight: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _publish_staging() -> void:
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	var reviewed: Dictionary = preflight.get("reviewed_identity", {})
	if reviewed.is_empty():
		_report("Run publish preflight before STAGING upload.")
		return
	var result := _extension("scrubbots-publish", {
		"action": "publish-staging", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release", "content_version": 2,
		"created_at_utc": str(reviewed.get("created_at_utc", "")),
		"reviewed_identity": reviewed,
	})
	_report("STAGING: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _extension(operation: String, request: Dictionary) -> Dictionary:
	if _gateway == null or not _gateway.has_method("run_studio_extension"):
		return {"state": "UNAVAILABLE", "reason": "Canonical Factory Core gateway is unavailable."}
	var result: Variant = _gateway.call("run_studio_extension", operation, request)
	return result if result is Dictionary else {"state": "ERROR", "reason": "Canonical operation returned no structured result."}
