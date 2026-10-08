extends Node

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
		get_tree().quit(1)
		return

	var instance := packed_scene.instantiate()
	_check(instance != null, "main Factory Studio scene did not instantiate")
	if instance == null:
		get_tree().quit(1)
		return

	get_tree().root.add_child(instance)
	await get_tree().process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	_check(navigation is FactoryStudioNavigation, "Navigation did not resolve at the committed scene path")
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(workspace is FactoryStudioWorkspacePage, "Workspace did not resolve at the committed scene path")

	if navigation is FactoryStudioNavigation and workspace is FactoryStudioWorkspacePage:
		var workspace_page := workspace as FactoryStudioWorkspacePage
		var navigation_control := navigation as FactoryStudioNavigation
		var workspace_handler := Callable(workspace_page, "show_surface")
		_check(navigation_control.surface_selected.is_connected(workspace_handler), "Navigation signal is not connected to Workspace presentation")
		_check(navigation_control.primary_routes() == ["HOME", "CREATE", "BATCH", "SOLVE", "REVIEW", "LIBRARY", "PUBLISH", "SETTINGS"], "Primary navigation is not the exact owner destination list")

		var title := workspace_page.get_node("Padding/Content/Title") as Label
		var state := workspace_page.get_node("Padding/Content/State") as Label
		_check(workspace_page.get_node("Padding/Content/OwnerPage").visible, "initial owner HOME page is not visible")
		_check(workspace_page.get_node("Padding/Content/OwnerPage/OwnerPageTitle").text == "Your production floor", "initial HOME title is incorrect")
		_check(title.visible == false and state.visible == false, "technical status wall is visible on default HOME")

		navigation_control.surface_selected.emit("Generate")
		await get_tree().process_frame
		_check(title.text == "Factory Studio — Generate", "deterministic navigation selection did not reach the workspace")
		_check("DRAFT" in state.text, "Generate did not expose the presentation draft state")
		_check("UNAVAILABLE" in state.text, "Generate did not preserve truthful Core unavailability")
		var target_controls := workspace_page.get_node_or_null("Padding/Content/TargetControls")
		_check(target_controls != null, "Generate target controls did not resolve at the committed scene path")
		if target_controls != null:
			_check(target_controls.visible, "Generate target controls are not visible on the Generate surface")

		navigation_control.surface_selected.emit("HOME")
		await get_tree().process_frame
		_check(workspace_page.get_node("Padding/Content/OwnerPage").visible, "HOME could not be restored deterministically")

	var footer_status := instance.get_node_or_null(FOOTER_STATUS_PATH) as Label
	_check(footer_status != null, "Core status footer did not resolve")
	if footer_status != null:
		_check(footer_status.text in ["System: Needs setup", "System: Ready"], "Core status footer is not concise and truthful")

	instance.queue_free()
	if failures.is_empty():
		print("SB-LF06-001-C001-R01 runtime contract PASS")
		get_tree().quit(0)
		return

	for failure in failures:
		push_error(failure)
	get_tree().quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
