@tool
class_name FactoryStudioWorkspacePage
extends PanelContainer


func show_surface(surface_name: String) -> void:
	var title: Label = $Padding/Content/Title
	var state: Label = $Padding/Content/State
	var detail: Label = $Padding/Content/Detail
	title.text = "Factory Studio — " + surface_name
	if surface_name == "Dashboard":
		state.text = "NOT AVAILABLE: canonical records and derived metrics are not connected in this foundation."
		detail.text = "This workspace shell is ready for a later audited presentation integration. No generated data is loaded."
	else:
		state.text = "NOT IMPLEMENTED: " + surface_name + " is an inert migration placeholder."
		detail.text = "No provider, import, library, solver, QA, review, batch, or output operation is performed here."
