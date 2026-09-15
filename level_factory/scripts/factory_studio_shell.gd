@tool
extends Control

var core_gateway: FactoryCoreGateway


func _ready() -> void:
	core_gateway = FactoryCoreGateway.new()
	var navigation: FactoryStudioNavigation = $Frame/Layout/Body/Navigation
	var workspace: FactoryStudioWorkspacePage = $Frame/Layout/Body/Workspace
	navigation.surface_selected.connect(workspace.show_surface)
	workspace.show_surface("Dashboard")
	$Frame/Layout/Footer/Status.text = "Canonical Core: %s — %s" % [core_gateway.status_name(), core_gateway.status_message()]


func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()
	if not has_node("Frame/Layout/Body/Navigation"):
		warnings.append("Factory Studio navigation node is missing.")
	if not has_node("Frame/Layout/Body/Workspace"):
		warnings.append("Factory Studio workspace node is missing.")
	return warnings
