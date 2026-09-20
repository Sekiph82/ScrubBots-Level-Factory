@tool
class_name FactoryStudioSimilarity
extends VBoxContainer

var _gateway: RefCounted
var _left: LineEdit
var _right: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Advisory Visual Similarity — exact identity remains stronger"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var notice := Label.new(); notice.text = "LOGICAL_CELL_HAMMING_V1 is offline, identity-bound, deterministic, and advisory. POSSIBLE_SIMILAR never auto-rejects, accepts, ranks, or mutates review."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
		var row := HBoxContainer.new(); _left = LineEdit.new(); _left.placeholder_text = "left candidate/revision ID"; _left.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_left); _right = LineEdit.new(); _right.placeholder_text = "right candidate/revision ID"; _right.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_right); var button := Button.new(); button.text = "Compare"; button.pressed.connect(compare); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
var _projection: Dictionary = {}
func set_ids(left_id: String, right_id: String) -> void: _left.text = left_id; _right.text = right_id
func compare() -> void:
	_projection = _gateway.call("run_studio_extension", "similarity", {"left_id": _left.text.strip_edges(), "right_id": _right.text.strip_edges(), "threshold": 0.92}) if _gateway != null else {"state": "UNAVAILABLE"}
	_result.text = "%s — %s vs %s\nScore: %s Distance: %s Threshold: %s\n%s" % [_projection.get("disposition", _projection.get("state", "UNAVAILABLE")), _projection.get("left_identity", ""), _projection.get("right_identity", ""), _projection.get("score", "NOT AVAILABLE"), _projection.get("distance", "NOT AVAILABLE"), _projection.get("threshold", "NOT AVAILABLE"), _projection.get("advisory_note", "Advisory only.")]
func show_similarity() -> void: pass
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "advisory_only": true, "projection": _projection.duplicate(true)}
