@tool
class_name FactoryStudioComparison
extends VBoxContainer

var _gateway: RefCounted
var _left: LineEdit
var _right: LineEdit
var _projection: Dictionary = {}
var _state: Label
var _details: Label


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func compare_selected() -> void:
	var ids := [_left.text.strip_edges(), _right.text.strip_edges()]
	_projection = _gateway.call("run_studio_extension", "comparison", {"candidate_ids": ids}) if _gateway != null else {"state": "UNAVAILABLE", "error": "Gateway unavailable."}
	_render()


func snapshot() -> Dictionary: return _projection.duplicate(true)
func show_comparison() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "Side-by-Side Candidate Comparison — read-only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var notice := Label.new(); notice.text = "Comparison shows identity-bound canonical preview/metrics and unavailable domains. It never computes a winner, acceptance, promotion, or cost by inference."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
	var row := HBoxContainer.new(); _left = LineEdit.new(); _left.placeholder_text = "left candidate ID"; _left.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_left); _right = LineEdit.new(); _right.placeholder_text = "right candidate ID"; _right.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_right); var button := Button.new(); button.text = "Compare"; button.pressed.connect(compare_selected); row.add_child(button); add_child(row)
	_state = Label.new(); _state.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state); _details = Label.new(); _details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_details)


func _render() -> void:
	if _state == null: return
	_state.text = "Comparison: %s | winner=%s" % [_projection.get("state", "EMPTY"), _projection.get("winner", {}).get("disposition", "NOT AVAILABLE")]
	var entries: Array[String] = []
	for candidate in _projection.get("candidates", []): entries.append("%s preview=%s dims=%sx%s colors=%s review=%s solver=%s difficulty=%s cost=%s" % [candidate.get("candidate_id", ""), candidate.get("artwork_sha256", ""), candidate.get("width", ""), candidate.get("height", ""), candidate.get("used_colors", []), candidate.get("owner_review", {}).get("disposition", "NOT AVAILABLE"), candidate.get("solver", {}).get("disposition", "NOT AVAILABLE"), candidate.get("difficulty", {}).get("disposition", "NOT AVAILABLE"), candidate.get("provider_cost", {}).get("disposition", "NOT AVAILABLE")])
	_details.text = "\n".join(entries) if not entries.is_empty() else "No comparison loaded."
