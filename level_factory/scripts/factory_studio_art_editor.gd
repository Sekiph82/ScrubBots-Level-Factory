@tool
class_name FactoryStudioArtEditor
extends VBoxContainer

## Bounded, presentation-only logical-pixel editor over a real canonical artwork.png.
## The source bundle is immutable; all edits remain in the in-memory working image.

const EMPTY := "EMPTY"
const CLEAN := "CLEAN"
const DIRTY := "DIRTY"
const ERROR := "ERROR"
const UNVALIDATED_DISPOSITION := "UNVALIDATED — revalidation pending SB-LF06-008"
const MAX_PREVIEW_EDGE := 512
const MAX_PRESENTATION_SCALE := 16
const LOGICAL_PALETTE_IDS: Array[String] = [
	"C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
	"C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
]
const CANONICAL_PALETTE_RGB: Dictionary = {
	"C01": [233, 75, 75],
	"C02": [242, 140, 60],
	"C03": [242, 201, 76],
	"C04": [85, 184, 90],
	"C05": [99, 214, 163],
	"C06": [66, 199, 217],
	"C07": [62, 126, 219],
	"C08": [52, 81, 163],
	"C09": [132, 94, 194],
	"C10": [230, 111, 165],
	"C11": [149, 100, 71],
	"C12": [232, 207, 160],
	"C13": [184, 194, 204],
	"C14": [61, 70, 82],
	"C15": [255, 255, 255],
	"C16": [0, 0, 0],
}

var _state := EMPTY
var _latest_successful_action: Dictionary = {}
var _source_action := ""
var _source_candidate_id := ""
var _source_bundle_path := ""
var _source_artwork_path := ""
var _source_artwork_sha256 := ""
var _logical_width := 0
var _logical_height := 0
var _presentation_scale := 0
var _selected_color_id := "C01"
var _error_message := ""
var _last_operation_rejection := ""
var _source_image: Image
var _working_image: Image
var _working_texture: ImageTexture
var _load_button: Button
var _reset_button: Button
var _state_label: Label
var _identity_label: Label
var _palette_label: Label
var _board: TextureRect
var _selected_color_label: Label


func _ready() -> void:
	if get_child_count() == 0:
		_build_editor()
	_refresh_editor()


func _build_editor() -> void:
	var heading := Label.new()
	heading.name = "EditorHeading"
	heading.text = "Non-destructive logical-pixel editor"
	heading.add_theme_font_size_override("font_size", 16)
	add_child(heading)

	var explanation := Label.new()
	explanation.name = "EditorExplanation"
	explanation.text = "Edits stay in memory over the loaded canonical artwork.png. DIRTY edits are UNVALIDATED and never rewrite the source bundle."
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(explanation)

	var action_row := HBoxContainer.new()
	_load_button = Button.new()
	_load_button.name = "LoadCurrentCanonicalArtwork"
	_load_button.text = "Load current canonical artwork"
	_load_button.pressed.connect(_on_load_pressed)
	action_row.add_child(_load_button)
	_reset_button = Button.new()
	_reset_button.name = "ResetToSource"
	_reset_button.text = "Reset to source"
	_reset_button.pressed.connect(_on_reset_pressed)
	action_row.add_child(_reset_button)
	add_child(action_row)

	_state_label = Label.new()
	_state_label.name = "EditorState"
	_state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_state_label)

	_identity_label = Label.new()
	_identity_label.name = "EditorIdentity"
	_identity_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_identity_label)

	_palette_label = Label.new()
	_palette_label.name = "PaletteHeading"
	_palette_label.text = "Canonical logical paint colors — C01..C16 only; BG01 is not paintable"
	_palette_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_palette_label)

	var palette_row := HFlowContainer.new()
	palette_row.name = "CanonicalPalette"
	for color_id in LOGICAL_PALETTE_IDS:
		var color_button := Button.new()
		color_button.name = color_id + "Palette"
		color_button.text = color_id
		color_button.tooltip_text = "Select canonical %s %s" % [color_id, _color_hex(color_id)]
		color_button.custom_minimum_size = Vector2(54, 28)
		color_button.pressed.connect(_on_palette_pressed.bind(color_id))
		palette_row.add_child(color_button)
	add_child(palette_row)

	_selected_color_label = Label.new()
	_selected_color_label.name = "SelectedColor"
	add_child(_selected_color_label)

	_board = TextureRect.new()
	_board.name = "EditableArtwork"
	_board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_board.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_board.stretch_mode = TextureRect.STRETCH_KEEP
	_board.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	_board.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	_board.mouse_filter = Control.MOUSE_FILTER_STOP
	_board.gui_input.connect(_on_board_gui_input)
	add_child(_board)


func observe_action_result(result: Dictionary) -> void:
	if str(result.get("state", "")) == "SUCCESS":
		_latest_successful_action = result.duplicate(true)
		_last_operation_rejection = ""
		_refresh_editor()
		return
	# A failed or unavailable action never erases the editor working buffer.
	_refresh_editor()


func latest_successful_action_snapshot() -> Dictionary:
	return _latest_successful_action.duplicate(true)


func snapshot() -> Dictionary:
	var dirty_count := _reconcile_state()
	return {
		"state": _state,
		"source_action": _source_action,
		"source_candidate_id": _source_candidate_id,
		"source_bundle_path": _source_bundle_path,
		"source_artwork_path": _source_artwork_path,
		"source_artwork_sha256": _source_artwork_sha256,
		"logical_width": _logical_width,
		"logical_height": _logical_height,
		"selected_color_id": _selected_color_id,
		"dirty_cell_count": dirty_count,
		"validation_disposition": UNVALIDATED_DISPOSITION,
		"working_buffer_differs": dirty_count > 0,
		"latest_successful_candidate_id": str(_latest_successful_action.get("candidate_id", "")),
		"latest_successful_output_path": str(_latest_successful_action.get("output_path", "")),
		"error": _error_message,
		"last_operation_rejection": _last_operation_rejection,
	}


func source_image_snapshot() -> Image:
	return _source_image.duplicate() if _source_image != null else null


func working_image_snapshot() -> Image:
	return _working_image.duplicate() if _working_image != null else null


func source_logical_cells_snapshot() -> Array[String]:
	return _logical_cells_snapshot(_source_image)


func working_logical_cells_snapshot() -> Array[String]:
	return _logical_cells_snapshot(_working_image)


func select_color(color_id: String) -> bool:
	if not LOGICAL_PALETTE_IDS.has(color_id) or color_id == "BG01" or not CANONICAL_PALETTE_RGB.has(color_id):
		_last_operation_rejection = "REJECTED — only canonical C01..C16 logical colors are paintable."
		return false
	_selected_color_id = color_id
	_last_operation_rejection = ""
	_refresh_editor()
	return true


func paint_cell(x: int, y: int, color_id: String = "") -> bool:
	_last_operation_rejection = ""
	if _state == EMPTY:
		_last_operation_rejection = "REJECTED — no real successful canonical artwork is loaded."
		return false
	if _state == ERROR or _working_image == null:
		_last_operation_rejection = "REJECTED — editor source is not safely loaded."
		return false
	if x < 0 or y < 0 or x >= _logical_width or y >= _logical_height:
		_last_operation_rejection = "REJECTED — logical cell is outside the loaded artwork bounds."
		return false
	var chosen_color := color_id if not color_id.is_empty() else _selected_color_id
	if not LOGICAL_PALETTE_IDS.has(chosen_color) or chosen_color == "BG01" or not CANONICAL_PALETTE_RGB.has(chosen_color):
		_last_operation_rejection = "REJECTED — only canonical C01..C16 logical colors are paintable."
		return false
	var target_color := _canonical_color(chosen_color)
	if _working_image.get_pixel(x, y) == target_color:
		_reconcile_state()
		_refresh_editor()
		return true
	_working_image.set_pixel(x, y, target_color)
	_reconcile_state()
	_refresh_editor()
	return true


func load_current_canonical_artwork(replace_dirty: bool = false) -> bool:
	if _latest_successful_action.is_empty():
		_last_operation_rejection = "REJECTED — no successful canonical artwork is available to load."
		if _source_image == null:
			_state = EMPTY
		_refresh_editor()
		return false
	if _state == DIRTY and not replace_dirty:
		_last_operation_rejection = "REJECTED — DIRTY working buffer requires explicit replacement."
		_refresh_editor()
		return false
	var result := _latest_successful_action
	var output_path := str(result.get("output_path", "")).strip_edges()
	var candidate_id := str(result.get("candidate_id", "")).strip_edges()
	if str(result.get("state", "")) != "SUCCESS" or output_path.is_empty() or candidate_id.is_empty():
		return _set_load_error("ERROR — latest action is not a complete successful canonical result.")
	if not _safe_output_path(output_path):
		return _set_load_error("ERROR — latest canonical output is outside the approved Factory output area.")
	var artwork_path := output_path.path_join("artwork.png")
	var absolute_artwork_path := _globalize_path(artwork_path)
	var bytes := FileAccess.get_file_as_bytes(absolute_artwork_path)
	if bytes.is_empty():
		return _set_load_error("ERROR — successful canonical artwork.png could not be read.")
	var image := Image.load_from_file(absolute_artwork_path)
	if image == null or image.is_empty() or image.get_width() < 1 or image.get_height() < 1:
		return _set_load_error("ERROR — successful canonical artwork.png could not be decoded.")
	_source_image = image.duplicate()
	_working_image = image.duplicate()
	_source_artwork_sha256 = _sha256(bytes)
	_source_action = str(result.get("action", ""))
	_source_candidate_id = candidate_id
	_source_bundle_path = output_path
	_source_artwork_path = artwork_path
	_logical_width = image.get_width()
	_logical_height = image.get_height()
	_state = CLEAN
	_error_message = ""
	_last_operation_rejection = ""
	_refresh_editor()
	return true


func reset_to_source() -> bool:
	if _source_image == null:
		_last_operation_rejection = "REJECTED — no immutable canonical source is loaded."
		_refresh_editor()
		return false
	_working_image = _source_image.duplicate()
	_state = CLEAN
	_error_message = ""
	_last_operation_rejection = ""
	_refresh_editor()
	return true


func load_revision_cells(width: int, height: int, cells: Array) -> bool:
	if _source_image == null or width != _logical_width or height != _logical_height or cells.size() != width * height:
		_last_operation_rejection = "REJECTED — revision dimensions do not match the loaded canonical editor source."
		_refresh_editor()
		return false
	var revision_image := Image.create(width, height, false, Image.FORMAT_RGBA8)
	for index in range(cells.size()):
		var color_id := str(cells[index])
		if not CANONICAL_PALETTE_RGB.has(color_id):
			_last_operation_rejection = "REJECTED — revision contains a non-canonical logical color."
			_refresh_editor()
			return false
		revision_image.set_pixel(index % width, index / width, _canonical_color(color_id))
	_working_image = revision_image
	_error_message = ""
	_last_operation_rejection = ""
	_reconcile_state()
	_refresh_editor()
	return true


func manual_editor_reference() -> Node:
	return self


func canonical_color_id_for_pixel(pixel: Color) -> String:
	for color_id in LOGICAL_PALETTE_IDS:
		if _canonical_color(color_id) == pixel:
			return color_id
	return ""


func _on_load_pressed() -> void:
	# The button itself is the explicit operator approval to replace a DIRTY buffer.
	load_current_canonical_artwork(true)


func _on_reset_pressed() -> void:
	reset_to_source()


func _on_palette_pressed(color_id: String) -> void:
	select_color(color_id)


func _on_board_gui_input(event: InputEvent) -> void:
	if not event is InputEventMouseButton:
		return
	var mouse_event := event as InputEventMouseButton
	if not mouse_event.pressed or mouse_event.button_index != MOUSE_BUTTON_LEFT:
		return
	if _presentation_scale < 1:
		return
	var logical_x := floori(mouse_event.position.x / float(_presentation_scale))
	var logical_y := floori(mouse_event.position.y / float(_presentation_scale))
	paint_cell(logical_x, logical_y)
	get_viewport().set_input_as_handled()


func _set_load_error(message: String) -> bool:
	_state = ERROR
	_error_message = message
	_last_operation_rejection = message
	_refresh_editor()
	return false


func _refresh_editor() -> void:
	if _state_label == null:
		return
	var dirty_count := _reconcile_state()
	var suffix := ""
	if _state == DIRTY:
		suffix = " — DIRTY EDIT != CANONICAL SOURCE"
	elif _state == CLEAN:
		suffix = " — working buffer matches immutable source"
	_state_label.text = "Editor state: %s%s | dirty cells=%s | %s" % [_state, suffix, dirty_count, UNVALIDATED_DISPOSITION]
	if _identity_label != null:
		if _source_image == null:
			_identity_label.text = "Source: no canonical artwork loaded. Latest successful candidate=%s" % str(_latest_successful_action.get("candidate_id", ""))
		else:
			_identity_label.text = "Source %s | candidate=%s | logical=%sx%s\nBundle: %s\nArtwork: %s\nSource SHA-256: %s" % [
				_source_action,
				_source_candidate_id,
				_logical_width,
				_logical_height,
				_source_bundle_path,
				_source_artwork_path,
				_source_artwork_sha256,
			]
	if _selected_color_label != null:
		_selected_color_label.text = "Selected logical color: %s %s" % [_selected_color_id, _color_hex(_selected_color_id)]
	if _load_button != null:
		_load_button.disabled = _latest_successful_action.is_empty()
		_load_button.text = "Load current canonical artwork" if _state != DIRTY else "Load current canonical artwork (replace DIRTY)"
	if _reset_button != null:
		_reset_button.disabled = _source_image == null
	if _board != null:
		_render_working_image()


func _render_working_image() -> void:
	if _working_image == null or _working_image.is_empty():
		_board.texture = null
		_board.custom_minimum_size = Vector2.ZERO
		_board.size = Vector2.ZERO
		return
	var presentation_scale := _integer_scale(_working_image.get_width(), _working_image.get_height())
	_presentation_scale = presentation_scale
	var displayed := _working_image.duplicate()
	displayed.resize(_working_image.get_width() * presentation_scale, _working_image.get_height() * presentation_scale, Image.INTERPOLATE_NEAREST)
	_working_texture = ImageTexture.create_from_image(displayed)
	_board.texture = _working_texture
	_board.custom_minimum_size = Vector2(displayed.get_width(), displayed.get_height())
	_board.size = Vector2(displayed.get_width(), displayed.get_height())


func _integer_scale(width: int, height: int) -> int:
	return maxi(1, mini(MAX_PRESENTATION_SCALE, floori(float(MAX_PREVIEW_EDGE) / float(maxi(width, height)))))


func _dirty_cell_count() -> int:
	if _source_image == null or _working_image == null:
		return 0
	if _source_image.get_width() != _working_image.get_width() or _source_image.get_height() != _working_image.get_height():
		return _logical_width * _logical_height
	var count := 0
	for y in range(_logical_height):
		for x in range(_logical_width):
			if _source_image.get_pixel(x, y) != _working_image.get_pixel(x, y):
				count += 1
	return count


func _reconcile_state() -> int:
	var dirty_count := _dirty_cell_count()
	if _source_image != null and _working_image != null and _state in [CLEAN, DIRTY]:
		_state = DIRTY if dirty_count > 0 else CLEAN
	return dirty_count


func _logical_cells_snapshot(image: Image) -> Array[String]:
	var cells: Array[String] = []
	if image == null or image.is_empty() or image.get_width() != _logical_width or image.get_height() != _logical_height:
		return cells
	for y in range(_logical_height):
		for x in range(_logical_width):
			var color_id := canonical_color_id_for_pixel(image.get_pixel(x, y))
			if color_id.is_empty():
				return []
			cells.append(color_id)
	return cells


func _canonical_color(color_id: String) -> Color:
	var rgb: Array = CANONICAL_PALETTE_RGB[color_id]
	return Color8(int(rgb[0]), int(rgb[1]), int(rgb[2]), 255)


func _color_hex(color_id: String) -> String:
	var rgb: Array = CANONICAL_PALETTE_RGB.get(color_id, [0, 0, 0])
	return "#%02X%02X%02X" % [int(rgb[0]), int(rgb[1]), int(rgb[2])]


func _globalize_path(path: String) -> String:
	if path.begins_with("res://") or not path.is_absolute_path():
		return ProjectSettings.globalize_path(path)
	return path


func _safe_output_path(path: String) -> bool:
	var project_output := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var candidate := _globalize_path(path).simplify_path().replace(char(92), "/").to_lower()
	return candidate == project_output or candidate.begins_with(project_output + "/")


func _sha256(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()
