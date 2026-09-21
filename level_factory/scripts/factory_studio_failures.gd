@tool
class_name FactoryStudioFailures
extends VBoxContainer

var _gateway: RefCounted
var _failure: LineEdit
var _result: Label
var _retry_button: Button
var _selected: Dictionary = {}

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Failure Inbox / Retry Center — preserved evidence"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _failure = LineEdit.new(); _failure.placeholder_text = "failure ID"; _failure.size_flags_horizontal = Control.SIZE_EXPAND_FILL; _failure.text_changed.connect(_on_failure_changed); row.add_child(_failure); var list := Button.new(); list.text = "Refresh inbox"; list.pressed.connect(refresh); row.add_child(list); _retry_button = Button.new(); _retry_button.name = "RetrySelected"; _retry_button.text = "Retry"; _retry_button.disabled = true; _retry_button.pressed.connect(retry_selected); row.add_child(_retry_button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Retry is enabled only for real eligible FAILED/REJECTED/INCONCLUSIVE evidence."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
var _projection: Dictionary = {}
func refresh() -> void:
	_projection = _gateway.call("run_studio_extension", "failures-list", {}) if _gateway != null else {"state": "UNAVAILABLE"}
	var failures: Array = _projection.get("failures", [])
	_selected = failures[0] if not failures.is_empty() else {}
	if _failure != null and not _selected.is_empty(): _failure.text = str(_selected.get("failure_id", ""))
	_render()
func retry_selected() -> void:
	if _retry_button == null or _retry_button.disabled: return
	_projection = _gateway.call("run_studio_extension", "retry-failure", {"failure_id": _failure.text.strip_edges(), "changes": {"operator_note": "Studio retry"}}) if _gateway != null else {"state": "UNAVAILABLE"}; _render()
func _on_failure_changed(value: String) -> void:
	_selected = {}
	for failure in _projection.get("failures", []):
		if str(failure.get("failure_id", "")) == value.strip_edges(): _selected = failure
	_render()
func select_failure(failure_id: String) -> void:
	if _failure != null: _failure.text = failure_id
	_on_failure_changed(failure_id)
func _render() -> void:
	if _result == null: return
	var failures: Array = _projection.get("failures", [])
	var rows: Array[String] = []
	for failure in failures: rows.append("%s | %s/%s | %s | evidence=%s | %s" % [failure.get("failure_id", ""), failure.get("operation", ""), failure.get("stage", ""), failure.get("reason", ""), failure.get("originating_evidence_id", ""), "RETRYABLE" if failure.get("retryable", false) else "NOT RETRYABLE: " + str(failure.get("non_retryable_reason", ""))])
	if _retry_button != null: _retry_button.disabled = _selected.is_empty() or not bool(_selected.get("retryable", false))
	_result.text = "Failure operation: %s\nRows:\n%s\nSelected: %s | Retry enabled=%s" % [_projection.get("disposition", _projection.get("state", "AVAILABLE")), "\n".join(rows), _selected.get("failure_id", "NONE"), not _retry_button.disabled if _retry_button != null else false]
func show_failures() -> void: refresh()
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "original_failure_preserved": true, "projection": _projection.duplicate(true)}
