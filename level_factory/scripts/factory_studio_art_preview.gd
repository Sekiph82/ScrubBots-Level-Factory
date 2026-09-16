@tool
class_name FactoryStudioArtPreview
extends VBoxContainer

## Presentation-only view over a successful canonical artwork.png artifact.
## It never reconstructs artwork from draft values or metadata.

const EMPTY := "EMPTY"
const READY := "READY"
const ERROR := "ERROR"
const MAX_PREVIEW_EDGE := 512
const MAX_PRESENTATION_SCALE := 16

var _state := EMPTY
var _source_action := ""
var _candidate_id := ""
var _source_bundle_path := ""
var _artwork_path := ""
var _attempted_artwork_path := ""
var _logical_width := 0
var _logical_height := 0
var _presentation_scale := 0
var _displayed_width := 0
var _displayed_height := 0
var _retained_after_failure := false
var _error_message := ""
var _source_image: Image
var _displayed_image: Image
var _preview_texture: ImageTexture
var _state_label: Label
var _identity_label: Label
var _image_control: TextureRect


func _ready() -> void:

	if get_child_count() == 0:
		_build_preview()
	_refresh_labels()


func _build_preview() -> void:
	var heading := Label.new()
	heading.name = "PreviewHeading"
	heading.text = "Canonical artwork preview"
	heading.add_theme_font_size_override("font_size", 16)
	add_child(heading)

	_state_label = Label.new()
	_state_label.name = "PreviewState"
	_state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_state_label)

	_identity_label = Label.new()
	_identity_label.name = "PreviewIdentity"
	_identity_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_identity_label)

	_image_control = TextureRect.new()
	_image_control.name = "ArtworkImage"
	_image_control.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_image_control.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_image_control.stretch_mode = TextureRect.STRETCH_KEEP
	_image_control.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	_image_control.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	add_child(_image_control)


func consume_action_result(result: Dictionary) -> void:
	var state := str(result.get("state", ""))
	if state == "SUCCESS":
		_load_successful_artwork(result)
		return
	if _state == EMPTY:
		_refresh_labels()
		return
	_retained_after_failure = true
	_refresh_labels()


func snapshot() -> Dictionary:
	return {
		"state": _state,
		"source_action": _source_action,
		"candidate_id": _candidate_id,
		"source_bundle_path": _source_bundle_path,
		"artwork_path": _artwork_path,
		"attempted_artwork_path": _attempted_artwork_path,
		"logical_width": _logical_width,
		"logical_height": _logical_height,
		"presentation_scale": _presentation_scale,
		"displayed_width": _displayed_width,
		"displayed_height": _displayed_height,
		"retained_after_failure": _retained_after_failure,
		"error": _error_message,
	}


func displayed_image_snapshot() -> Image:
	return _displayed_image.duplicate() if _displayed_image != null else null


func _load_successful_artwork(result: Dictionary) -> void:
	var output_path := str(result.get("output_path", "")).strip_edges()
	var attempted_path := output_path.path_join("artwork.png")
	_attempted_artwork_path = attempted_path
	var image := _load_canonical_image(output_path)
	if image == null:
		_state = ERROR
		_error_message = "ERROR — successful Core evidence has no readable canonical artwork.png; no draft preview was fabricated."
		_retained_after_failure = _displayed_image != null
		_refresh_labels()
		return

	_source_image = image
	_logical_width = image.get_width()
	_logical_height = image.get_height()
	_presentation_scale = _integer_scale(_logical_width, _logical_height)
	_displayed_width = _logical_width * _presentation_scale
	_displayed_height = _logical_height * _presentation_scale
	_displayed_image = image.duplicate()
	_displayed_image.resize(_displayed_width, _displayed_height, Image.INTERPOLATE_NEAREST)
	_preview_texture = ImageTexture.create_from_image(_displayed_image)
	_source_action = str(result.get("action", ""))
	_candidate_id = str(result.get("candidate_id", ""))
	_source_bundle_path = output_path
	_artwork_path = attempted_path
	_state = READY
	_error_message = ""
	_retained_after_failure = false
	if _image_control != null:
		_image_control.texture = _preview_texture
		_image_control.custom_minimum_size = Vector2(_displayed_width, _displayed_height)
		_image_control.size = Vector2(_displayed_width, _displayed_height)
	_refresh_labels()


func _load_canonical_image(output_path: String) -> Image:
	if output_path.is_empty():
		return null
	var project_output := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var candidate_output := output_path
	if candidate_output.begins_with("res://") or not candidate_output.is_absolute_path():
		candidate_output = ProjectSettings.globalize_path(candidate_output)
	candidate_output = candidate_output.simplify_path().replace(char(92), "/")
	var normalized_output := candidate_output.to_lower()
	if normalized_output != project_output and not normalized_output.begins_with(project_output + "/"):
		return null
	var image := Image.load_from_file(candidate_output.path_join("artwork.png"))
	if image == null or image.is_empty() or image.get_width() < 1 or image.get_height() < 1:
		return null
	return image


func _integer_scale(width: int, height: int) -> int:
	return maxi(1, mini(MAX_PRESENTATION_SCALE, floori(float(MAX_PREVIEW_EDGE) / float(maxi(width, height)))))


func _refresh_labels() -> void:
	if _state_label == null or _identity_label == null:
		return
	if _state == EMPTY:
		_state_label.text = "Preview state: EMPTY — no successful canonical artwork is loaded."
		_identity_label.text = "Only a real successful-bundle artwork.png can populate this preview."
	elif _state == ERROR:
		var retained_text := " A prior preview remains labeled retained/stale." if _retained_after_failure else " No preview texture is shown."
		_state_label.text = "Preview state: ERROR — %s%s" % [_error_message, retained_text]
		_identity_label.text = "Attempted artwork path: %s" % _attempted_artwork_path
	else:
		var retention_text := " — RETAINED LAST SUCCESS" if _retained_after_failure else ""
		_state_label.text = "Preview state: READY%s" % retention_text
		_identity_label.text = "Canonical %s | candidate=%s | logical=%sx%s | scale=%sx | displayed=%sx%s\nSource: %s" % [
			_source_action,
			_candidate_id,
			_logical_width,
			_logical_height,
			_presentation_scale,
			_displayed_width,
			_displayed_height,
			_artwork_path,
		]
