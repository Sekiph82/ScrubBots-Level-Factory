@tool
class_name FactoryStudioCost
extends VBoxContainer

var _gateway: RefCounted
var _scope: LineEdit
var _provider: LineEdit
var _result: Label

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Provider Cost / Credit Center — recorded facts only"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var row := HBoxContainer.new(); _scope = LineEdit.new(); _scope.placeholder_text = "scope filter (optional)"; _scope.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_scope); _provider = LineEdit.new(); _provider.placeholder_text = "provider filter (optional)"; _provider.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_provider); var button := Button.new(); button.text = "Refresh"; button.pressed.connect(refresh); row.add_child(button); add_child(row)
		_result = Label.new(); _result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _result.text = "Unknown consumed/remaining values stay NOT AVAILABLE. No provider or network calls are made by this view."; add_child(_result)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
var _projection: Dictionary = {}
func refresh() -> void:
	var request := {"scope": _scope.text.strip_edges(), "provider": _provider.text.strip_edges()}; if request["scope"] == "": request["scope"] = null; if request["provider"] == "": request["provider"] = null
	_projection = _gateway.call("run_studio_extension", "cost-center", request) if _gateway != null else {"state": "UNAVAILABLE"}; _result.text = "Groups: %s\nValidated local evidence only; read-only." % (_projection.get("groups", []) as Array).size()
func show_cost() -> void: refresh()
func snapshot() -> Dictionary: return {"state": _projection.get("state", "AVAILABLE"), "read_only": true, "network_calls": 0, "projection": _projection.duplicate(true)}
