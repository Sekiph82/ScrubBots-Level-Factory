@tool
class_name FactoryStudioNavigation
extends VBoxContainer

## The future Studio surfaces are represented once here as inert navigation.
## Their implementation belongs to separately authorized work.

const NAVIGATION_SURFACES: Array[String] = [
	"Dashboard",
	"Generate",
	"Import",
	"Library",
	"Batches",
	"Candidates",
	"Review",
	"QA",
	"Providers",
	"Outputs",
	"Settings",
]

signal surface_selected(surface_name: String)


func _ready() -> void:
	if get_child_count() > 0:
		return
	for surface_name in NAVIGATION_SURFACES:
		var button := Button.new()
		button.text = surface_name
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.tooltip_text = "Workspace placeholder: " + surface_name
		button.pressed.connect(_on_surface_pressed.bind(surface_name))
		add_child(button)


func _on_surface_pressed(surface_name: String) -> void:
	surface_selected.emit(surface_name)
