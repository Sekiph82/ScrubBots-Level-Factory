@tool
extends Control

const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")

var core_gateway: RefCounted


func _ready() -> void:
	var gateway_script := ResourceLoader.call("load", "res://scripts/factory_core_gateway.gd") as Script
	core_gateway = gateway_script.new() if gateway_script != null else null
	var navigation := _resolve_navigation()
	var workspace := _resolve_workspace()
	if navigation == null:
		push_error("Factory Studio Navigation node is missing at %s." % NAVIGATION_NODE_PATH)
		return
	if workspace == null:
		push_error("Factory Studio Workspace node is missing at %s." % WORKSPACE_NODE_PATH)
		return
	workspace.configure_gateway(core_gateway)
	navigation.connect("surface_selected", Callable(workspace, "show_surface"))
	workspace.call("show_surface", "Dashboard")
	$Frame/Layout/Footer/Status.text = "Canonical Core: %s — %s | %s" % [core_gateway.status_name(), core_gateway.status_message(), core_gateway.capability_summary()]


func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()
	if _resolve_navigation() == null:
		warnings.append("Factory Studio navigation node is missing at %s." % NAVIGATION_NODE_PATH)
	if _resolve_workspace() == null:
		warnings.append("Factory Studio workspace node is missing at %s." % WORKSPACE_NODE_PATH)
	return warnings


func _resolve_navigation() -> Node:
	return get_node_or_null(NAVIGATION_NODE_PATH)


func _resolve_workspace() -> Node:
	return get_node_or_null(WORKSPACE_NODE_PATH)
