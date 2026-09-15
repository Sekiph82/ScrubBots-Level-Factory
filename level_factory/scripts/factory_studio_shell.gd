@tool
extends Control

const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")

var core_gateway: FactoryCoreGateway


func _ready() -> void:
	core_gateway = FactoryCoreGateway.new()
	var navigation := _resolve_navigation()
	var workspace := _resolve_workspace()
	if navigation == null:
		push_error("Factory Studio Navigation node is missing at %s." % NAVIGATION_NODE_PATH)
		return
	if workspace == null:
		push_error("Factory Studio Workspace node is missing at %s." % WORKSPACE_NODE_PATH)
		return
	workspace.configure_gateway(core_gateway)
	navigation.surface_selected.connect(workspace.show_surface)
	workspace.show_surface("Dashboard")
	$Frame/Layout/Footer/Status.text = "Canonical Core: %s — %s | %s" % [core_gateway.status_name(), core_gateway.status_message(), core_gateway.capability_summary()]


func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()
	if _resolve_navigation() == null:
		warnings.append("Factory Studio navigation node is missing at %s." % NAVIGATION_NODE_PATH)
	if _resolve_workspace() == null:
		warnings.append("Factory Studio workspace node is missing at %s." % WORKSPACE_NODE_PATH)
	return warnings


func _resolve_navigation() -> FactoryStudioNavigation:
	return get_node_or_null(NAVIGATION_NODE_PATH) as FactoryStudioNavigation


func _resolve_workspace() -> FactoryStudioWorkspacePage:
	return get_node_or_null(WORKSPACE_NODE_PATH) as FactoryStudioWorkspacePage
