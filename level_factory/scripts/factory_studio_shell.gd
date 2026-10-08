@tool
extends Control

const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")

var core_gateway: RefCounted


func _ready() -> void:
	DisplayServer.window_set_title("ScrubBots Factory Studio")
	_apply_native_window_icon()
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
	workspace.call("show_surface", "HOME")
	var available: bool = core_gateway.status_name() == "AVAILABLE"
	$Frame/Layout/Footer/Status.text = "System: Ready" if available else "System: Needs setup"
	$Frame/Layout/Footer/Status.tooltip_text = "%s — %s | %s" % [core_gateway.status_name(), core_gateway.status_message(), core_gateway.capability_summary()]


func _apply_native_window_icon() -> void:
	if OS.get_name() != "Windows" or not DisplayServer.has_feature(DisplayServer.FEATURE_NATIVE_ICON):
		return
	var icon_path := ProjectSettings.globalize_path("res://assets/icons/ScrubBots_Factory_Studio.ico")
	if not FileAccess.file_exists(icon_path):
		push_warning("Factory Studio native window icon is unavailable: %s" % icon_path)
		return
	DisplayServer.set_native_icon(icon_path)


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
