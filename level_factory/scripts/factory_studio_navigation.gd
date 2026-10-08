@tool
class_name FactoryStudioNavigation
extends VBoxContainer

## Eight owner destinations. Legacy surface IDs remain available through
## contextual actions inside the owner pages and in direct integration tests.
const PRIMARY_DESTINATIONS: Array[Dictionary] = [
	{"label": "HOME", "route": "HOME", "icon": "⌂"},
	{"label": "CREATE", "route": "CREATE", "icon": "+"},
	{"label": "BATCH", "route": "BATCH", "icon": "▦"},
	{"label": "SOLVE", "route": "SOLVE", "icon": "◇"},
	{"label": "REVIEW", "route": "REVIEW", "icon": "✓"},
	{"label": "LIBRARY", "route": "LIBRARY", "icon": "▤"},
	{"label": "PUBLISH", "route": "PUBLISH", "icon": "↑"},
	{"label": "SETTINGS", "route": "SETTINGS", "icon": "⚙"},
]

signal surface_selected(surface_name: String)

var _buttons: Dictionary = {}


func _ready() -> void:
	if get_child_count() > 0:
		return
	add_theme_constant_override("separation", 8)
	for destination in PRIMARY_DESTINATIONS:
		var route := str(destination["route"])
		var button := Button.new()
		button.name = "Primary" + route.capitalize()
		button.text = str(destination["label"])
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.custom_minimum_size = Vector2(0, 48)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.focus_mode = Control.FOCUS_ALL
		button.pressed.connect(_on_surface_pressed.bind(route))
		add_child(button)
		_buttons[route] = button
	select_destination("HOME")


func select_destination(route: String) -> void:
	for destination in _buttons:
		var button: Button = _buttons[destination]
		button.toggle_mode = true
		button.button_pressed = destination == route


func primary_routes() -> Array[String]:
	var routes: Array[String] = []
	for destination in PRIMARY_DESTINATIONS:
		routes.append(str(destination["route"]))
	return routes


func _on_surface_pressed(surface_name: String) -> void:
	select_destination(surface_name)
	surface_selected.emit(surface_name)
