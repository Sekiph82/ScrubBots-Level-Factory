extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const FOOTER_STATUS_PATH := NodePath("Frame/Layout/Footer/Status")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const WIDTH_PATH := NodePath("WidthRow/Width")
const HEIGHT_PATH := NodePath("HeightRow/Height")
const SEED_PATH := NodePath("SeedRow/Seed")
const MODE_PATH := NodePath("ModeRow/Mode")
const CANDIDATE_PATH := NodePath("CandidatepresentationlabelRow/CandidatePresentation")

const EXPECTED_MODES: Array[String] = ["MASK", "RULES", "WFC", "HYBRID", "AUTO"]
const EXPECTED_PRIMARY_NAVIGATION: Array[String] = ["HOME", "CREATE", "BATCH", "SOLVE", "REVIEW", "LIBRARY", "PUBLISH", "SETTINGS"]
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var packed_scene := ResourceLoader.call(SCENE_LOADER_METHOD, MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		quit(1)
		return

	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		quit(1)
		return
	root.add_child(instance)
	await process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(navigation != null, "Navigation did not instantiate at the committed path")
	_check(workspace != null, "Workspace did not instantiate at the committed path")
	if navigation == null or workspace == null:
		instance.queue_free()
		quit(1)
		return

	_check(navigation.has_signal("surface_selected"), "Navigation surface_selected signal is missing")
	_check(_workspace_signal_is_connected(navigation, workspace), "Navigation signal is not connected to Workspace presentation")
	_check(navigation.call("primary_routes") == EXPECTED_PRIMARY_NAVIGATION, "Primary navigation is not the exact eight owner destinations")
	_check(navigation.get_child_count() == EXPECTED_PRIMARY_NAVIGATION.size(), "Technical pages remain in primary navigation")
	for index in range(EXPECTED_PRIMARY_NAVIGATION.size()):
		var nav_button := navigation.get_child(index) as Button
		_check(nav_button != null and nav_button.text == EXPECTED_PRIMARY_NAVIGATION[index], "Primary navigation label/order drifted at index %d" % index)

	var title := workspace.get_node_or_null("Padding/Content/Title") as Label
	var state := workspace.get_node_or_null("Padding/Content/State") as Label
	var footer_status := instance.get_node_or_null(FOOTER_STATUS_PATH) as Label
	_check(title != null, "Workspace title path is missing")
	_check(state != null, "Workspace state path is missing")
	_check(footer_status != null, "Core status footer path is missing")
	if title == null or state == null or footer_status == null:
		instance.queue_free()
		quit(1)
		return
	var owner_page := workspace.get_node_or_null("Padding/Content/OwnerPage") as VBoxContainer
	var owner_heading := owner_page.get_node_or_null("OwnerPageTitle") as Label if owner_page != null else null
	var owner_guidance := owner_page.get_node_or_null("OwnerPageGuidance") as Label if owner_page != null else null
	var owner_action := owner_page.get_node_or_null("ProductionWorkspace/NextStepCard/Actions/PrimaryAction") as Button if owner_page != null else null
	var preview := owner_page.get_node_or_null("ProductionWorkspace/ArtworkPreviewCard/PreviewContent/PreviewStage/PreviewCenter/ArtworkThumbnail") as TextureRect if owner_page != null else null
	var technical_toggle := owner_page.get_node_or_null("ProductionWorkspace/NextStepCard/Actions/TechnicalDetailsToggle") as Button if owner_page != null else null
	var readiness_summary := owner_page.get_node_or_null("ReadinessSummary") as HBoxContainer if owner_page != null else null
	_check(owner_page != null and owner_page.visible, "Default HOME owner page is not visible")
	_check(owner_heading != null and owner_heading.text == "Your production floor", "HOME title/guidance node is missing")
	_check(owner_guidance != null and not owner_guidance.text.is_empty(), "HOME one-line guidance is missing")
	_check(owner_action != null and owner_action.text == "Continue batch", "HOME dominant next action is missing")
	_check(preview != null, "Primary artwork preview area is missing")
	_check(readiness_summary != null and readiness_summary.get_child_count() == 5, "Compact production status cards are missing")
	if readiness_summary != null:
		var artwork_state := readiness_summary.find_child("ArtworkState", true, false) as Label
		_check(artwork_state != null and artwork_state.text == "Not selected", "Empty HOME artwork status was %s" % (artwork_state.text if artwork_state != null else "missing"))
		for card in readiness_summary.get_children():
			var card_state := card.get_child(0).get_child(1) as Label
			_check(card_state != null and "PASS" not in card_state.text.to_upper() and "READY" not in card_state.text.to_upper(), "Empty HOME fabricated positive readiness")
	_check(technical_toggle != null, "Expandable Technical details control is missing")
	_check(footer_status.text == "System: Needs setup" or footer_status.text == "System: Ready", "Footer status is not compact owner-readable state")
	_check(instance.get_window().title == "ScrubBots Factory Studio", "Normal owner runtime title changed or contains DEBUG")
	if technical_toggle != null:
		technical_toggle.button_pressed = true
		technical_toggle.toggled.emit(true)
		_check(owner_page.get_node_or_null("ProductionWorkspace/NextStepCard/Actions/TechnicalDetails").visible, "Technical details do not expand")
		technical_toggle.button_pressed = false
		technical_toggle.toggled.emit(false)
	_check(not owner_guidance.text.contains("canonical") and not owner_guidance.text.contains("immutable"), "Default HOME guidance exposes engineering vocabulary")

	var seen_tools: Dictionary = {}
	for destination in EXPECTED_PRIMARY_NAVIGATION:
		navigation.emit_signal("surface_selected", destination)
		await process_frame
		_check(owner_page != null and owner_page.visible, "%s did not open an owner page" % destination)
		_check(owner_heading != null and not owner_heading.text.is_empty(), "%s has no page title" % destination)
		_check(owner_guidance != null and not owner_guidance.text.is_empty(), "%s has no concise guidance" % destination)
		_check(owner_action != null and not owner_action.text.is_empty(), "%s has no dominant action" % destination)
		var actions := owner_page.get_node_or_null("ProductionWorkspace/NextStepCard/Actions/ContextualActions")
		if actions != null:
			for contextual_button in actions.get_children():
				seen_tools[contextual_button.text] = true
	_check(seen_tools.has("Validate") and seen_tools.has("Prepare supply"), "CREATE lost validation or pipeline preparation entry points")
	_check(seen_tools.has("Failures and retry") and seen_tools.has("Recover session"), "BATCH lost retry or recovery entry points")
	_check(seen_tools.has("Compare") and seen_tools.has("Similarity") and seen_tools.has("QA details"), "REVIEW lost compare, similarity, or QA entry points")
	_check(seen_tools.has("Search") and seen_tools.has("Revisions") and seen_tools.has("Reproduce"), "LIBRARY lost discovery or selected-item history tools")
	_check(seen_tools.has("Release pool") and seen_tools.has("Outputs"), "PUBLISH lost release or output entry points")
	_check(seen_tools.has("Providers") and seen_tools.has("Cost and credits"), "SETTINGS lost provider or accounting entry points")
	navigation.emit_signal("surface_selected", "REVIEW")
	await process_frame
	var review_action := owner_page.get_node("ProductionWorkspace/NextStepCard/Actions/PrimaryAction") as Button
	review_action.pressed.emit()
	await process_frame
	var review_surface := workspace.get_node_or_null("Padding/Content/CandidateInbox")
	_check(review_surface != null, "Contextual owner review queue is not instantiated")
	_check(review_surface != null and _find_button_by_text(review_surface, "ACCEPT") and _find_button_by_text(review_surface, "REJECT"), "Explicit owner review decisions were removed")
	navigation.emit_signal("surface_selected", "PUBLISH")
	await process_frame
	var publish_action := owner_page.get_node("ProductionWorkspace/NextStepCard/Actions/PrimaryAction") as Button
	_check(publish_action.get_meta("target_surface", "") == "Release", "PUBLISH does not route to the canonical release surface")
	var release_surface_node := workspace.get_node_or_null("ContextualToolHost/CampaignRelease")
	_check(release_surface_node != null and _find_button_by_text(release_surface_node, "Publish to STAGING"), "STAGING action was removed")
	_check(release_surface_node != null and _find_button_by_text(release_surface_node, "APPROVE and Open Release PR"), "Separate production approval was removed")

	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	_check(title.text == "Factory Studio — Generate", "Generate navigation did not reach the workspace")
	_check("DRAFT" in state.text and "UNAVAILABLE" in state.text, "Generate draft/Core state is not truthful")

	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	_check(target != null and target.visible, "Generate target controls are not visible")
	if target == null:
		instance.queue_free()
		quit(1)
		return

	var width := target.get_node_or_null(WIDTH_PATH) as SpinBox
	var height := target.get_node_or_null(HEIGHT_PATH) as SpinBox
	var seed := target.get_node_or_null(SEED_PATH) as LineEdit
	var mode := target.get_node_or_null(MODE_PATH) as OptionButton
	var candidate := target.get_node_or_null(CANDIDATE_PATH) as LineEdit
	_check(width != null, "Width control path is missing")
	_check(height != null, "Height control path is missing")
	_check(seed != null, "Seed control path is missing")
	_check(mode != null, "Mode control path is missing")
	_check(candidate != null, "Candidate presentation control path is missing")
	if width == null or height == null or seed == null or mode == null or candidate == null:
		instance.queue_free()
		quit(1)
		return

	_check(_option_values(mode) == EXPECTED_MODES, "Mode choices drifted from the accepted contract")
	_check(width.min_value == 20.0 and width.max_value == 59.0, "Width bounds are not 20..59")
	_check(height.min_value == 20.0 and height.max_value == 59.0, "Height bounds are not 20..59")
	_check(candidate.max_length == 64, "Candidate presentation label is not bounded")

	var initial_snapshot = target.call("draft_snapshot")
	_check(initial_snapshot is Dictionary, "Draft snapshot is not a dictionary")
	if not initial_snapshot is Dictionary:
		instance.queue_free()
		quit(1)
		return
	_check(initial_snapshot["state"] == "DRAFT", "Initial draft state is not DRAFT")
	_check(initial_snapshot["core_validation"] == "UNAVAILABLE", "Initial Core state is not UNAVAILABLE")
	_check(initial_snapshot["generation_state"] == "NOT EXECUTED — presentation draft only", "Initial draft claims an operation")

	width.value = 23
	height.value = 47
	seed.text = "operator-seed"
	seed.text_changed.emit(seed.text)
	mode.select(3)
	mode.item_selected.emit(3)
	candidate.text = "preview-label"
	candidate.text_changed.emit(candidate.text)
	await process_frame

	var edited_snapshot = target.call("draft_snapshot")
	_check(edited_snapshot is Dictionary, "Edited draft snapshot is not a dictionary")
	if edited_snapshot is Dictionary:
		_check(edited_snapshot["width"] == 23 and edited_snapshot["height"] == 47, "Independent rectangle did not update")
		_check(edited_snapshot["seed"] == "operator-seed", "Seed draft did not update")
		_check(edited_snapshot["mode"] == "HYBRID", "Mode draft did not update")
		_check(edited_snapshot["candidate_presentation"] == "preview-label", "Candidate presentation draft did not update")
		_check(target.call("draft_snapshot") == edited_snapshot, "Draft snapshot is not deterministic")

	_check(width.min_value == 20.0 and width.max_value == 59.0, "Width bounds changed unexpectedly")
	_check(height.min_value == 20.0 and height.max_value == 59.0, "Height bounds changed unexpectedly")
	_check(_contains_action_buttons(target), "Factory Studio action controls are missing")

	navigation.emit_signal("surface_selected", "Import")
	await process_frame
	_check(title.text == "Factory Studio — Import", "Inert Import surface is unstable")
	_check(not target.visible, "Target controls remained visible on an inert surface")
	navigation.emit_signal("surface_selected", "Release")
	await process_frame
	var release_surface := workspace.get_node_or_null("Padding/Content/CampaignRelease")
	_check(title.text == "Factory Studio — Release", "Release navigation did not reach the workspace")
	_check(release_surface != null and release_surface.visible, "Release Pool surface did not instantiate/show")
	_check(release_surface != null and release_surface.get_child_count() >= 6, "Release Pool plan/lock/approval controls are missing")
	if release_surface != null:
		var generated_utc: String = release_surface.call("_current_utc_timestamp")
		var utc_pattern := RegEx.new()
		_check(utc_pattern.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$") == OK,
			"Studio UTC timestamp pattern did not compile")
		_check(utc_pattern.search(generated_utc) != null,
			"Factory Studio did not generate canonical timezone-explicit UTC seconds: " + generated_utc)
	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	_check(target.visible, "Generate target controls did not return")
	_check(target.call("draft_snapshot") == edited_snapshot, "Draft did not remain stable across navigation")

	instance.queue_free()
	await process_frame
	if failures.is_empty():
		print("SB-LF06-002-C001-R01 committed runtime suite PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _workspace_signal_is_connected(navigation: Node, workspace: Node) -> bool:
	for connection in navigation.get_signal_connection_list("surface_selected"):
		var callback: Callable = connection.get("callable")
		if callback.get_object() == workspace and callback.get_method() == "show_surface":
			return true
	return false


func _option_values(control: OptionButton) -> Array[String]:
	var values: Array[String] = []
	for index in range(control.item_count):
		values.append(control.get_item_text(index))
	return values


func _contains_action_buttons(node: Node) -> bool:
	for action in ["Generate", "Solve", "Validate", "Analyze", "Reproduce"]:
		if node.get_node_or_null("ActionArea/" + action + "Action") == null:
			return false
	return true


func _find_button_by_text(node: Node, expected_text: String) -> bool:
	if node is Button and (node as Button).text == expected_text:
		return true
	for child in node.get_children():
		if _find_button_by_text(child, expected_text):
			return true
	return false


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
