extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const FOOTER_STATUS_PATH := NodePath("Frame/Layout/Footer/Status")

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_contract")


func _run_contract() -> void:
	var packed_scene := load(MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "main Factory Studio scene did not load")
	if packed_scene == null:
		quit(1)
		return

	var instance := packed_scene.instantiate()
	_check(instance != null, "main Factory Studio scene did not instantiate")
	if instance == null:
		quit(1)
		return

	root.add_child(instance)
	await process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	_check(navigation is FactoryStudioNavigation, "Navigation did not resolve at the committed scene path")
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(workspace is FactoryStudioWorkspacePage, "Workspace did not resolve at the committed scene path")

	if navigation is FactoryStudioNavigation and workspace is FactoryStudioWorkspacePage:
		var workspace_page := workspace as FactoryStudioWorkspacePage
		var navigation_control := navigation as FactoryStudioNavigation
		var workspace_handler := Callable(workspace_page, "show_surface")
		_check(navigation_control.surface_selected.is_connected(workspace_handler), "Navigation signal is not connected to Workspace presentation")

		var title := workspace_page.get_node("Padding/Content/Title") as Label
		var state := workspace_page.get_node("Padding/Content/State") as Label
		_check(title.text == "Factory Studio — Dashboard", "initial surface is not Dashboard")
		_check("NOT AVAILABLE" in state.text, "initial Dashboard does not report truthful unavailability")
		_check("generated data" not in state.text.to_lower(), "initial Dashboard exposes fabricated/generated operational state")

		navigation_control.surface_selected.emit("Generate")
		await process_frame
		_check(title.text == "Factory Studio — Generate", "deterministic navigation selection did not reach the workspace")
		_check("NOT IMPLEMENTED" in state.text, "navigation selection did not remain an inert placeholder")

		navigation_control.surface_selected.emit("Dashboard")
		await process_frame
		_check(title.text == "Factory Studio — Dashboard", "Dashboard could not be restored deterministically")

	var footer_status := instance.get_node_or_null(FOOTER_STATUS_PATH) as Label
	_check(footer_status != null, "Core status footer did not resolve")
	if footer_status != null:
		_check("UNAVAILABLE" in footer_status.text, "Core status is not truthful UNAVAILABLE")

	instance.queue_free()
	if failures.is_empty():
		print("SB-LF06-001-C001-R01 runtime contract PASS")
		quit(0)
		return

	for failure in failures:
		push_error(failure)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
