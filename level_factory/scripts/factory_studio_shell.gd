@tool
extends Control

const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const MASTER_UI_NODE_PATH := NodePath("MasterUI")

var core_gateway: RefCounted


func _ready() -> void:
	DisplayServer.window_set_title("ScrubBots Factory Studio")
	_apply_native_window_icon()
	var gateway_script := ResourceLoader.call("load", "res://scripts/factory_core_gateway.gd") as Script
	core_gateway = gateway_script.new() if gateway_script != null else null
	var navigation := _resolve_navigation()
	var workspace := _resolve_workspace()
	var master_ui := get_node_or_null(MASTER_UI_NODE_PATH)
	if navigation == null or workspace == null or master_ui == null:
		push_error("Factory Studio owner presentation nodes are incomplete.")
		return
	if core_gateway != null:
		workspace.call("configure_gateway", core_gateway)
		master_ui.call("configure_gateway", core_gateway)
	navigation.connect("surface_selected", Callable(workspace, "show_surface"))
	workspace.call("show_surface", "HOME")
	var available: bool = core_gateway != null and core_gateway.status_name() == "AVAILABLE"
	$Frame/Layout/Footer/Status.text = "System: Ready" if available else "System: Needs setup"
	if core_gateway != null:
		$Frame/Layout/Footer/Status.tooltip_text = "%s — %s | %s" % [core_gateway.status_name(), core_gateway.status_message(), core_gateway.capability_summary()]


func _apply_native_window_icon() -> void:
	var icon_path := ProjectSettings.globalize_path("res://assets/icons/ScrubBots_Factory_Studio_256.png")
	var icon := Image.load_from_file(icon_path)
	if icon != null and not icon.is_empty():
		DisplayServer.window_set_icon(icon)


func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()
	for path in [NAVIGATION_NODE_PATH, WORKSPACE_NODE_PATH, MASTER_UI_NODE_PATH]:
		if get_node_or_null(path) == null:
			warnings.append("Factory Studio presentation node is missing at %s." % path)
	return warnings


func _resolve_navigation() -> Node:
	return get_node_or_null(NAVIGATION_NODE_PATH)


func _resolve_workspace() -> Node:
	return get_node_or_null(WORKSPACE_NODE_PATH)
