@tool
class_name FactoryStudioWorkspacePage
extends PanelContainer

@onready var target_controls: Node = $Padding/Content/TargetControls


func configure_gateway(gateway: RefCounted) -> void:
	if target_controls != null and target_controls.has_method("configure_gateway"):
		target_controls.call("configure_gateway", gateway)


func show_surface(surface_name: String) -> void:
	var title: Label = $Padding/Content/Title
	var state: Label = $Padding/Content/State
	var detail: Label = $Padding/Content/Detail
	target_controls.visible = surface_name == "Generate"
	title.text = "Factory Studio — " + surface_name
	if surface_name == "Dashboard":
		state.text = "NOT AVAILABLE: canonical records and derived metrics are not connected in this foundation."
		detail.text = "This workspace shell is ready for a later audited presentation integration. No generated data is loaded."
	elif surface_name == "Generate":
		state.text = "DRAFT — CORE VALIDATION: UNAVAILABLE"
		detail.text = "Editable presentation draft; canonical execution evidence is shown separately in Action result."
	else:
		state.text = "NOT IMPLEMENTED: " + surface_name + " is an inert migration placeholder."
		detail.text = "No provider, import, library, solver, QA, review, batch, or output operation is performed here."
