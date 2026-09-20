@tool
class_name FactoryStudioFailures
extends VBoxContainer

var _gateway: RefCounted
var _failure: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Failure Inbox / Retry Center — preserved evidence"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _failure = LineEdit.new(); _failure.placeholder_text = "failure ID"; _failure.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_failure); var list := Button.new(); list.text = "Refresh inbox"; list.pressed.connect(refresh); row.add_child(list); var retry := Button.new(); retry.text = "Retry"; retry.pressed.connect(retry_selected); row.add_child(retry); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Retry is enabled only for real eligible FAILED/REJECTED/INCONCLUSIVE evidence."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
var _projection: Dictionary = {}
func refresh() -> void:
	_projection = _gateway.call("run_studio_extension", "failures-list", {}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func retry_selected() -> void:
	_projection = _gateway.call("run_studio_extension", "retry-failure", {"failure_id": _failure.text.strip_edges(), "changes": {"operator_note": "Studio retry"}}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func _render() -> void: _result.text = "Failure operation: %s\nFailures: %s\nRetry: %s" % [_projection.get("disposition", _projection.get("state", "AVAILABLE")), (_projection.get("failures", []) as Array).size(), _projection.get("attempt_id", "not executed")]
func show_failures() -> void: refresh()
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "original_failure_preserved": true, "projection": _projection.duplicate(true)}
