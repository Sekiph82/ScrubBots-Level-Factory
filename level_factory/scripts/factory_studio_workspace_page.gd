@tool
class_name FactoryStudioWorkspacePage
extends PanelContainer

@onready var target_controls: Node = $Padding/Content/TargetControls
@onready var content: VBoxContainer = $Padding/Content

const DASHBOARD_SCRIPT_PATH := "res://scripts/factory_studio_dashboard.gd"
const IMPORT_SCRIPT_PATH := "res://scripts/factory_studio_import.gd"
const LIBRARY_SCRIPT_PATH := "res://scripts/factory_studio_library.gd"
const VALIDATION_SCRIPT_PATH := "res://scripts/factory_studio_import_validation.gd"
const PIPELINE_SCRIPT_PATH := "res://scripts/factory_studio_pipeline.gd"
const CANDIDATES_SCRIPT_PATH := "res://scripts/factory_studio_candidates.gd"
const COMPARISON_SCRIPT_PATH := "res://scripts/factory_studio_comparison.gd"
const PRESETS_SCRIPT_PATH := "res://scripts/factory_studio_presets.gd"
const SEARCH_SCRIPT_PATH := "res://scripts/factory_studio_search.gd"
const READINESS_SCRIPT_PATH := "res://scripts/factory_studio_readiness.gd"
const REPRODUCE_SCRIPT_PATH := "res://scripts/factory_studio_reproduce.gd"
const REVISIONS_SCRIPT_PATH := "res://scripts/factory_studio_revisions.gd"
const FAILURES_SCRIPT_PATH := "res://scripts/factory_studio_failures.gd"
const BATCH_IMPORT_SCRIPT_PATH := "res://scripts/factory_studio_batch_import.gd"
const SESSION_SCRIPT_PATH := "res://scripts/factory_studio_session.gd"
const SIMILARITY_SCRIPT_PATH := "res://scripts/factory_studio_similarity.gd"
const COST_SCRIPT_PATH := "res://scripts/factory_studio_cost.gd"
const RELEASE_SCRIPT_PATH := "res://scripts/factory_studio_release.gd"
var dashboard: Node
var import_surface: Node
var library_surface: Node
var validation_surface: Node
var pipeline_surface: Node
var candidates_surface: Node
var comparison_surface: Node
var presets_surface: Node
var search_surface: Node
var readiness_surface: Node
var reproduce_surface: Node
var revisions_surface: Node
var failures_surface: Node
var batch_import_surface: Node
var session_surface: Node
var similarity_surface: Node
var cost_surface: Node
var release_surface: Node
var owner_page: VBoxContainer
var owner_heading: Label
var owner_guidance: Label
var owner_system_state: Label
var owner_state_cards: HBoxContainer
var owner_preview_texture: TextureRect
var owner_preview_caption: Label
var owner_action_button: Button
var owner_tools_row: HFlowContainer
var owner_technical_button: Button
var owner_technical_panel: VBoxContainer
var owner_technical_text: Label
var return_button: Button
var owner_action_layout: VBoxContainer
var legacy_tool_host: Node
var active_tool_node: Control
var active_owner_route := "HOME"
var active_tool_route := ""
var core_gateway: RefCounted

const OWNER_PAGES := {
	"HOME": {
		"title": "Your production floor",
		"guidance": "Pick up where you left off or bring new artwork into the Factory.",
		"action": "Continue batch", "target": "Pipeline",
		"tools": [["Open batch", "Pipeline"], ["Import artwork", "Import"], ["Batch PNGs", "Batch Import"]],
	},
	"CREATE": {
		"title": "Create levels from artwork",
		"guidance": "Choose one PNG or a group, then prepare and generate from the original pixels.",
		"action": "Choose a PNG", "target": "Import",
		"tools": [["Generate", "Generate"], ["Batch PNGs", "Batch Import"], ["Validate", "Import Validation"], ["Prepare supply", "Pipeline"], ["Recipes", "Presets"]],
	},
	"BATCH": {
		"title": "Run a batch",
		"guidance": "Track every artwork, resume saved work, and retry only eligible failures.",
		"action": "Add PNGs to batch", "target": "Batch Import",
		"tools": [["Continue pipeline", "Pipeline"], ["Failures and retry", "Failures"], ["Recover session", "Session Recovery"]],
	},
	"SOLVE": {
		"title": "Make a playable level",
		"guidance": "Review the artwork and supply columns, then run the official solver and difficulty check.",
		"action": "Open solve workspace", "target": "Generate",
		"tools": [["Solve / re-solve", "Generate"], ["Readiness", "Readiness"], ["Pipeline", "Pipeline"]],
	},
	"REVIEW": {
		"title": "Review levels",
		"guidance": "Inspect the artwork and evidence. Your explicit decision controls acceptance.",
		"action": "Open review queue", "target": "Review",
		"tools": [["Compare", "Comparison"], ["Readiness", "Readiness"], ["Similarity", "Similarity"], ["QA details", "Review"]],
	},
	"LIBRARY": {
		"title": "Find your artwork",
		"guidance": "Search verified sources and revisit saved history, recipes, and reproductions.",
		"action": "Browse library", "target": "Library",
		"tools": [["Search", "Search"], ["Recipes", "Presets"], ["Revisions", "Revisions"], ["Reproduce", "Reproduce"]],
	},
	"PUBLISH": {
		"title": "Prepare a release",
		"guidance": "Order accepted levels, run preflight, publish to STAGING, then request production approval.",
		"action": "Open campaign order", "target": "Release",
		"tools": [["Release pool", "Release"], ["Outputs", "Outputs"]],
	},
	"SETTINGS": {
		"title": "Factory settings",
		"guidance": "Manage provider setup, cost information, paths, and advanced diagnostics.",
		"action": "Open diagnostics", "target": "Diagnostics",
		"tools": [["Providers", "Providers"], ["Cost and credits", "Cost Center"], ["Session recovery", "Session Recovery"], ["Technical details", "Diagnostics"]],
	},
}


func _ready() -> void:
	_ensure_dashboard()
	_ensure_import()
	_ensure_library()
	_ensure_validation()
	_ensure_pipeline()
	_ensure_candidates()
	_ensure_comparison()
	_ensure_presets()
	_ensure_search()
	_ensure_readiness()
	_ensure_reproduce()
	_ensure_revisions()
	_ensure_failures()
	_ensure_batch_import()
	_ensure_session()
	_ensure_similarity()
	_ensure_cost()
	_ensure_release()
	_build_owner_page()
	_build_return_button()
	_park_all_legacy_surfaces()


func _build_owner_page() -> void:
	owner_page = VBoxContainer.new()
	owner_page.name = "OwnerPage"
	owner_page.visible = false
	owner_page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	owner_page.add_theme_constant_override("separation", 12)
	content.add_child(owner_page)
	owner_heading = Label.new()
	owner_heading.name = "OwnerPageTitle"
	owner_heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_heading.add_theme_font_size_override("font_size", 28)
	owner_page.add_child(owner_heading)
	owner_guidance = Label.new()
	owner_guidance.name = "OwnerPageGuidance"
	owner_guidance.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_guidance.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	owner_page.add_child(owner_guidance)
	owner_state_cards = HBoxContainer.new()
	owner_state_cards.name = "ReadinessSummary"
	owner_state_cards.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_state_cards.add_theme_constant_override("separation", 8)
	owner_page.add_child(owner_state_cards)
	for item in [["Artwork", "Not selected"], ["Supply", "Waiting"], ["Solver", "Not run"], ["Review", "Waiting"], ["Release", "Not started"]]:
		var card := PanelContainer.new()
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		owner_state_cards.add_child(card)
		var card_content := VBoxContainer.new()
		card_content.add_theme_constant_override("separation", 3)
		card.add_child(card_content)
		var card_heading := Label.new()
		card_heading.text = str(item[0]).to_upper()
		card_heading.add_theme_font_size_override("font_size", 11)
		card_content.add_child(card_heading)
		var card_state := Label.new()
		card_state.name = str(item[0]) + "State"
		card_state.text = str(item[1])
		card_state.add_theme_font_size_override("font_size", 13)
		card_content.add_child(card_state)
	var body := HBoxContainer.new()
	body.name = "ProductionWorkspace"
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 18)
	owner_page.add_child(body)
	var preview_card := PanelContainer.new()
	preview_card.name = "ArtworkPreviewCard"
	preview_card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	preview_card.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(preview_card)
	var preview_layout := VBoxContainer.new()
	preview_layout.name = "PreviewContent"
	preview_layout.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	preview_layout.add_theme_constant_override("separation", 10)
	preview_card.add_child(preview_layout)
	var preview_heading := Label.new()
	preview_heading.text = "ARTWORK PREVIEW"
	preview_heading.add_theme_font_size_override("font_size", 14)
	preview_layout.add_child(preview_heading)
	var preview_stage := PanelContainer.new()
	preview_stage.name = "PreviewStage"
	preview_stage.size_flags_vertical = Control.SIZE_EXPAND_FILL
	preview_stage.custom_minimum_size = Vector2(0, 280)
	preview_layout.add_child(preview_stage)
	var stage_stack := CenterContainer.new()
	stage_stack.name = "PreviewCenter"
	stage_stack.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	preview_stage.add_child(stage_stack)
	owner_preview_texture = TextureRect.new()
	owner_preview_texture.name = "ArtworkThumbnail"
	owner_preview_texture.custom_minimum_size = Vector2(250, 250)
	owner_preview_texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	owner_preview_texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	owner_preview_texture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	owner_preview_texture.visible = false
	stage_stack.add_child(owner_preview_texture)
	var empty_label := Label.new()
	empty_label.name = "PreviewEmptyState"
	empty_label.text = "Your pixel art will appear here\nafter you choose a PNG"
	empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	empty_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	empty_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	stage_stack.add_child(empty_label)
	owner_preview_caption = Label.new()
	owner_preview_caption.name = "PreviewCaption"
	owner_preview_caption.text = "No artwork selected"
	owner_preview_caption.add_theme_color_override("font_color", Color("#aab5cc"))
	preview_layout.add_child(owner_preview_caption)
	var action_card := PanelContainer.new()
	action_card.name = "NextStepCard"
	action_card.custom_minimum_size = Vector2(330, 0)
	body.add_child(action_card)
	var action_layout := VBoxContainer.new()
	action_layout.name = "Actions"
	action_layout.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	action_layout.add_theme_constant_override("separation", 12)
	owner_action_layout = action_layout
	action_card.add_child(action_layout)
	var next_label := Label.new()
	next_label.text = "NEXT STEP"
	next_label.add_theme_font_size_override("font_size", 14)
	action_layout.add_child(next_label)
	owner_system_state = Label.new()
	owner_system_state.name = "ProductionState"
	owner_system_state.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	owner_system_state.custom_minimum_size.y = 54
	action_layout.add_child(owner_system_state)
	owner_action_button = Button.new()
	owner_action_button.name = "PrimaryAction"
	owner_action_button.custom_minimum_size = Vector2(0, 52)
	owner_action_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_action_button.pressed.connect(_on_primary_action)
	action_layout.add_child(owner_action_button)
	var tools_heading := Label.new()
	tools_heading.text = "MORE FOR THIS STEP"
	tools_heading.add_theme_font_size_override("font_size", 13)
	action_layout.add_child(tools_heading)
	owner_tools_row = HFlowContainer.new()
	owner_tools_row.name = "ContextualActions"
	owner_tools_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_tools_row.add_theme_constant_override("h_separation", 8)
	owner_tools_row.add_theme_constant_override("v_separation", 8)
	action_layout.add_child(owner_tools_row)
	owner_technical_button = Button.new()
	owner_technical_button.name = "TechnicalDetailsToggle"
	owner_technical_button.text = "Technical details  +"
	owner_technical_button.toggled.connect(_on_technical_details_toggled)
	action_layout.add_child(owner_technical_button)
	owner_technical_panel = VBoxContainer.new()
	owner_technical_panel.name = "TechnicalDetails"
	owner_technical_panel.visible = false
	owner_technical_text = Label.new()
	owner_technical_text.name = "TechnicalEvidence"
	owner_technical_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	owner_technical_panel.add_child(owner_technical_text)


func _build_return_button() -> void:
	return_button = Button.new()
	return_button.name = "ReturnToOwnerPage"
	return_button.text = "← Back to %s" % active_owner_route.capitalize()
	return_button.visible = false
	return_button.pressed.connect(func(): show_surface(active_owner_route))
	content.add_child(return_button)


func _park_all_legacy_surfaces() -> void:
	legacy_tool_host = Node.new()
	legacy_tool_host.name = "ContextualToolHost"
	add_child(legacy_tool_host)
	for child in content.get_children():
		if child == owner_page or child == return_button or child == $Padding/Content/Title or child == $Padding/Content/State or child == $Padding/Content/Detail:
			child.visible = false
			continue
		if child is Control:
			content.remove_child(child)
			legacy_tool_host.add_child(child)
			child.visible = false


func _park_active_tool() -> void:
	if active_tool_node == null:
		return
	if active_tool_node.get_parent() == content:
		content.remove_child(active_tool_node)
		legacy_tool_host.add_child(active_tool_node)
	active_tool_node.visible = false
	active_tool_node = null


func _tool_for_surface(surface_name: String) -> Control:
	match surface_name:
		"Dashboard": return dashboard
		"Generate": return target_controls
		"Import": return import_surface
		"Library": return library_surface
		"Import Validation": return validation_surface
		"Pipeline": return pipeline_surface
		"Candidates", "Review": return candidates_surface
		"Comparison": return comparison_surface
		"Presets": return presets_surface
		"Search": return search_surface
		"Readiness": return readiness_surface
		"Reproduce": return reproduce_surface
		"Revisions": return revisions_surface
		"Failures": return failures_surface
		"Batch Import": return batch_import_surface
		"Session Recovery": return session_surface
		"Similarity": return similarity_surface
		"Cost Center": return cost_surface
		"Release": return release_surface
		_: return null


func _show_owner_page(route: String) -> void:
	_park_active_tool()
	active_owner_route = route
	active_tool_route = ""
	owner_page.visible = true
	$Padding/Content/Title.visible = false
	$Padding/Content/State.visible = false
	$Padding/Content/Detail.visible = false
	return_button.visible = false
	owner_technical_button.button_pressed = false
	owner_technical_panel.visible = false
	var page: Dictionary = OWNER_PAGES[route]
	owner_heading.text = str(page["title"])
	owner_guidance.text = str(page["guidance"])
	owner_action_button.text = str(page["action"])
	owner_action_button.set_meta("target_surface", str(page["target"]))
	for child in owner_tools_row.get_children():
		child.queue_free()
	for tool in page["tools"]:
		var button := Button.new()
		button.text = str(tool[0])
		button.set_meta("target_surface", str(tool[1]))
		button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		button.pressed.connect(_open_tool.bind(str(tool[1])))
		owner_tools_row.add_child(button)
	_refresh_owner_state()
	_refresh_owner_preview()
	var technical := "System status: %s\n" % _system_state_name()
	if core_gateway != null:
		technical += "Core: %s — %s\n" % [core_gateway.status_name(), core_gateway.status_message()]
		technical += "Capabilities: %s" % core_gateway.capability_summary()
	owner_technical_text.text = technical


func _refresh_owner_state() -> void:
	var state := "No artwork selected yet. Choose a PNG to begin."
	if target_controls != null and target_controls.has_method("action_result_snapshot"):
		var result: Dictionary = target_controls.call("action_result_snapshot")
		if not result.is_empty():
			var disposition := str(result.get("state", ""))
			var action := str(result.get("action", "Production step"))
			state = "%s: %s" % [action, "Completed" if disposition == "SUCCESS" else "Needs attention" if disposition in ["FAILED", "ERROR"] else "Not available"]
	if active_owner_route == "HOME":
		owner_system_state.text = "No batch selected\nChoose artwork or continue a saved batch."
	elif active_owner_route == "BATCH":
		owner_system_state.text = "Ready for artwork\nPer-item progress appears after a batch starts."
	elif active_owner_route == "PUBLISH":
		owner_system_state.text = "No release batch selected\nAccepted levels and preflight will appear here."
	else:
		owner_system_state.text = state
	var defaults: Dictionary = {
		"HOME": ["Not selected", "Waiting", "Not run", "Waiting", "Not started"],
		"CREATE": ["Not selected", "Waiting", "Not run", "Waiting", "Not started"],
		"BATCH": ["No items", "Waiting", "Waiting", "Not run", "Not started"],
		"SOLVE": ["Waiting", "Not prepared", "Not run", "Not checked", "Not started"],
		"REVIEW": ["Waiting", "Waiting", "Not run", "No decision", "Not started"],
		"LIBRARY": ["Browse sources", "—", "—", "—", "—"],
		"PUBLISH": ["Accepted only", "—", "—", "Preflight pending", "Not published"],
		"SETTINGS": ["System", _system_state_name(), "—", "—", "—"],
	}
	var labels := ["ArtworkState", "SupplyState", "SolverState", "ReviewState", "ReleaseState"]
	var states: Array = defaults.get(active_owner_route, defaults["HOME"])
	if target_controls != null and target_controls.has_method("last_successful_core_evidence_snapshot"):
		var last_success: Dictionary = target_controls.call("last_successful_core_evidence_snapshot")
		if last_success.get("state", "") == "SUCCESS":
			states[0] = "Generated"
	for index in range(labels.size()):
		var status_label := owner_state_cards.find_child(str(labels[index]), true, false) as Label
		if status_label != null:
			status_label.text = str(states[index])


func _refresh_owner_preview() -> void:
	var image: Image = null
	if target_controls != null:
		var preview := target_controls.get_node_or_null("ActionArea/CanonicalArtworkPreview")
		if preview != null and preview.has_method("displayed_image_snapshot"):
			image = preview.call("displayed_image_snapshot") as Image
	var empty_state := owner_page.find_child("PreviewEmptyState", true, false) as Label
	if image != null and not image.is_empty():
		owner_preview_texture.texture = ImageTexture.create_from_image(image)
		owner_preview_texture.visible = true
		empty_state.visible = false
		var snapshot: Dictionary = target_controls.call("action_result_snapshot") if target_controls.has_method("action_result_snapshot") else {}
		owner_preview_caption.text = "Latest canonical artwork · %s" % str(snapshot.get("candidate_id", "candidate"))
	else:
		owner_preview_texture.texture = null
		owner_preview_texture.visible = false
		empty_state.visible = true
		owner_preview_caption.text = "No artwork selected"


func _on_primary_action() -> void:
	_open_tool(str(owner_action_button.get_meta("target_surface", "")))


func _on_technical_details_toggled(enabled: bool) -> void:
	owner_technical_panel.visible = enabled
	if enabled and owner_technical_panel.get_parent() == null:
		owner_action_layout.add_child(owner_technical_panel)
	elif not enabled and owner_technical_panel.get_parent() == owner_action_layout:
		owner_action_layout.remove_child(owner_technical_panel)
	owner_technical_button.text = "Technical details  −" if enabled else "Technical details  +"


func _open_tool(surface_name: String) -> void:
	_park_active_tool()
	active_tool_route = surface_name
	owner_page.visible = false
	return_button.visible = true
	return_button.text = "← Back to %s" % active_owner_route.capitalize()
	$Padding/Content/Title.visible = true
	$Padding/Content/State.visible = true
	$Padding/Content/Detail.visible = true
	active_tool_node = _tool_for_surface(surface_name)
	if active_tool_node != null:
		if active_tool_node.get_parent() == legacy_tool_host:
			legacy_tool_host.remove_child(active_tool_node)
		content.add_child(active_tool_node)
	_show_legacy_surface(surface_name)


func show_surface(surface_name: String) -> void:
	if OWNER_PAGES.has(surface_name):
		_show_owner_page(surface_name)
		return
	_open_tool(surface_name)


func _system_state_name() -> String:
	if core_gateway == null:
		return "Needs setup"
	return "Ready" if core_gateway.status_name() == "AVAILABLE" else "Needs setup"


func _ensure_dashboard() -> void:
	if dashboard != null:
		return
	var dashboard_script := ResourceLoader.call("load", DASHBOARD_SCRIPT_PATH) as Script
	if dashboard_script == null:
		return
	dashboard = dashboard_script.new() as Node
	dashboard.name = "OperationsDashboard"
	dashboard.visible = false
	content.add_child(dashboard)


func _ensure_import() -> void:
	if import_surface != null:
		return
	var import_script := ResourceLoader.call("load", IMPORT_SCRIPT_PATH) as Script
	if import_script == null:
		return
	import_surface = import_script.new() as Node
	import_surface.name = "OperationsImport"
	import_surface.visible = false
	content.add_child(import_surface)


func _ensure_library() -> void:
	if library_surface != null:
		return
	var library_script := ResourceLoader.call("load", LIBRARY_SCRIPT_PATH) as Script
	if library_script == null:
		return
	library_surface = library_script.new() as Node
	library_surface.name = "SourceArtLibrary"
	library_surface.visible = false
	content.add_child(library_surface)


func _ensure_validation() -> void:
	if validation_surface != null:
		return
	var validation_script := ResourceLoader.call("load", VALIDATION_SCRIPT_PATH) as Script
	if validation_script == null:
		return
	validation_surface = validation_script.new() as Node
	validation_surface.name = "ImportValidationWizard"
	validation_surface.visible = false
	content.add_child(validation_surface)


func _ensure_pipeline() -> void:
	if pipeline_surface != null: return
	var pipeline_script := ResourceLoader.call("load", PIPELINE_SCRIPT_PATH) as Script
	if pipeline_script == null: return
	pipeline_surface = pipeline_script.new() as Node
	pipeline_surface.name = "OneClickPipeline"
	pipeline_surface.visible = false
	content.add_child(pipeline_surface)


func _ensure_candidates() -> void:
	if candidates_surface != null: return
	var candidates_script := ResourceLoader.call("load", CANDIDATES_SCRIPT_PATH) as Script
	if candidates_script == null: return
	candidates_surface = candidates_script.new() as Node
	candidates_surface.name = "CandidateInbox"
	candidates_surface.visible = false
	content.add_child(candidates_surface)


func _ensure_comparison() -> void:
	if comparison_surface != null: return
	var comparison_script := ResourceLoader.call("load", COMPARISON_SCRIPT_PATH) as Script
	if comparison_script == null: return
	comparison_surface = comparison_script.new() as Node
	comparison_surface.name = "CandidateComparison"
	comparison_surface.visible = false
	content.add_child(comparison_surface)


func _ensure_presets() -> void:
	if presets_surface != null: return
	var presets_script := ResourceLoader.call("load", PRESETS_SCRIPT_PATH) as Script
	if presets_script == null: return
	presets_surface = presets_script.new() as Node
	presets_surface.name = "ProductionPresets"
	presets_surface.visible = false
	content.add_child(presets_surface)


func _ensure_search() -> void:
	if search_surface != null: return
	var search_script := ResourceLoader.call("load", SEARCH_SCRIPT_PATH) as Script
	if search_script == null: return
	search_surface = search_script.new() as Node
	search_surface.name = "DiscoverySearch"
	search_surface.visible = false
	content.add_child(search_surface)


func _ensure_readiness() -> void:
	if readiness_surface != null: return
	var readiness_script := ResourceLoader.call("load", READINESS_SCRIPT_PATH) as Script
	if readiness_script == null: return
	readiness_surface = readiness_script.new() as Node
	readiness_surface.name = "ProductionReadinessCard"
	readiness_surface.visible = false
	content.add_child(readiness_surface)


func _ensure_reproduce() -> void:
	if reproduce_surface != null: return
	var reproduce_script := ResourceLoader.call("load", REPRODUCE_SCRIPT_PATH) as Script
	if reproduce_script == null: return
	reproduce_surface = reproduce_script.new() as Node
	reproduce_surface.name = "ExactReproduce"
	reproduce_surface.visible = false
	content.add_child(reproduce_surface)


func _ensure_revisions() -> void:
	if revisions_surface != null: return
	var revisions_script := ResourceLoader.call("load", REVISIONS_SCRIPT_PATH) as Script
	if revisions_script == null: return
	revisions_surface = revisions_script.new() as Node
	revisions_surface.name = "ManualEditRevisions"
	revisions_surface.visible = false
	content.add_child(revisions_surface)


func _ensure_failures() -> void:
	if failures_surface != null: return
	var failures_script := ResourceLoader.call("load", FAILURES_SCRIPT_PATH) as Script
	if failures_script == null: return
	failures_surface = failures_script.new() as Node
	failures_surface.name = "FailureInbox"
	failures_surface.visible = false
	content.add_child(failures_surface)


func _ensure_batch_import() -> void:
	if batch_import_surface != null: return
	var batch_script := ResourceLoader.call("load", BATCH_IMPORT_SCRIPT_PATH) as Script
	if batch_script == null: return
	batch_import_surface = batch_script.new() as Node
	batch_import_surface.name = "BatchImport"
	batch_import_surface.visible = false
	content.add_child(batch_import_surface)


func _ensure_session() -> void:
	if session_surface != null: return
	var session_script := ResourceLoader.call("load", SESSION_SCRIPT_PATH) as Script
	if session_script == null: return
	session_surface = session_script.new() as Node
	session_surface.name = "SessionRecovery"
	session_surface.visible = false
	content.add_child(session_surface)


func _ensure_similarity() -> void:
	if similarity_surface != null: return
	var similarity_script := ResourceLoader.call("load", SIMILARITY_SCRIPT_PATH) as Script
	if similarity_script == null: return
	similarity_surface = similarity_script.new() as Node
	similarity_surface.name = "VisualSimilarity"
	similarity_surface.visible = false
	content.add_child(similarity_surface)


func _ensure_cost() -> void:
	if cost_surface != null: return
	var cost_script := ResourceLoader.call("load", COST_SCRIPT_PATH) as Script
	if cost_script == null: return
	cost_surface = cost_script.new() as Node
	cost_surface.name = "ProviderCostCenter"
	cost_surface.visible = false
	content.add_child(cost_surface)


func _ensure_release() -> void:
	if release_surface != null: return
	var release_script := ResourceLoader.call("load", RELEASE_SCRIPT_PATH) as Script
	if release_script == null: return
	release_surface = release_script.new() as Node
	release_surface.name = "CampaignRelease"
	release_surface.visible = false
	content.add_child(release_surface)


func configure_gateway(gateway: RefCounted) -> void:
	if target_controls != null and target_controls.has_method("configure_gateway"):
		target_controls.call("configure_gateway", gateway)
	if dashboard != null and dashboard.has_method("configure_gateway"):
		dashboard.call("configure_gateway", gateway)
	if dashboard != null and dashboard.has_method("configure_action_source"):
		dashboard.call("configure_action_source", target_controls)
	if import_surface != null and import_surface.has_method("configure_gateway"):
		import_surface.call("configure_gateway", gateway)
	if library_surface != null and library_surface.has_method("configure_gateway"):
		library_surface.call("configure_gateway", gateway)
	if validation_surface != null and validation_surface.has_method("configure_gateway"):
		validation_surface.call("configure_gateway", gateway)
	if pipeline_surface != null and pipeline_surface.has_method("configure_gateway"):
		pipeline_surface.call("configure_gateway", gateway)
	if candidates_surface != null and candidates_surface.has_method("configure_gateway"):
		candidates_surface.call("configure_gateway", gateway)
	if comparison_surface != null and comparison_surface.has_method("configure_gateway"):
		comparison_surface.call("configure_gateway", gateway)
	if presets_surface != null and presets_surface.has_method("configure_gateway"):
		presets_surface.call("configure_gateway", gateway)
	if search_surface != null and search_surface.has_method("configure_gateway"):
		search_surface.call("configure_gateway", gateway)
	if readiness_surface != null and readiness_surface.has_method("configure_gateway"):
		readiness_surface.call("configure_gateway", gateway)
	if reproduce_surface != null and reproduce_surface.has_method("configure_gateway"):
		reproduce_surface.call("configure_gateway", gateway)
	if revisions_surface != null and revisions_surface.has_method("configure_gateway"):
		revisions_surface.call("configure_gateway", gateway)
	if revisions_surface != null and target_controls != null and target_controls.has_method("manual_editor_reference") and revisions_surface.has_method("configure_editor"):
		revisions_surface.call("configure_editor", target_controls.call("manual_editor_reference"))
	if failures_surface != null and failures_surface.has_method("configure_gateway"):
		failures_surface.call("configure_gateway", gateway)
	if batch_import_surface != null and batch_import_surface.has_method("configure_gateway"):
		batch_import_surface.call("configure_gateway", gateway)
	if session_surface != null and session_surface.has_method("configure_gateway"):
		session_surface.call("configure_gateway", gateway)
	if similarity_surface != null and similarity_surface.has_method("configure_gateway"):
		similarity_surface.call("configure_gateway", gateway)
	if cost_surface != null and cost_surface.has_method("configure_gateway"):
		cost_surface.call("configure_gateway", gateway)
	if release_surface != null and release_surface.has_method("configure_gateway"):
		release_surface.call("configure_gateway", gateway)


func _show_legacy_surface(surface_name: String) -> void:
	var title: Label = $Padding/Content/Title
	var state: Label = $Padding/Content/State
	var detail: Label = $Padding/Content/Detail
	target_controls.visible = surface_name == "Generate"
	if dashboard != null:
		dashboard.visible = surface_name == "Dashboard"
	if import_surface != null:
		import_surface.visible = surface_name == "Import"
	if library_surface != null:
		library_surface.visible = surface_name == "Library"
	if validation_surface != null:
		validation_surface.visible = surface_name == "Import" + " Validation"
	if pipeline_surface != null:
		pipeline_surface.visible = surface_name == "Pipeline"
	if candidates_surface != null:
		candidates_surface.visible = surface_name in ["Candidates", "Review"]
	if comparison_surface != null:
		comparison_surface.visible = surface_name == "Comparison"
	if presets_surface != null:
		presets_surface.visible = surface_name == "Presets"
	if search_surface != null:
		search_surface.visible = surface_name == "Search"
	if readiness_surface != null:
		readiness_surface.visible = surface_name == "Readiness"
	if reproduce_surface != null:
		reproduce_surface.visible = surface_name == "Reproduce"
	if revisions_surface != null:
		revisions_surface.visible = surface_name == "Revisions"
	if failures_surface != null:
		failures_surface.visible = surface_name == "Failures"
	if batch_import_surface != null:
		batch_import_surface.visible = surface_name == "Batch Import"
	if session_surface != null:
		session_surface.visible = surface_name == "Session Recovery"
	if similarity_surface != null:
		similarity_surface.visible = surface_name == "Similarity"
	if cost_surface != null:
		cost_surface.visible = surface_name == "Cost Center"
	if release_surface != null:
		release_surface.visible = surface_name == "Release"
	title.text = "Factory Studio — " + surface_name
	if surface_name == "Dashboard":
		state.text = "READ-ONLY DERIVED VIEW — canonical batch evidence (NOT AVAILABLE until a canonical manifest is selected)"
		detail.text = "No generated data is loaded until Dashboard refresh reads a validated batch-manifest.json under res://output/. It does not mutate canonical records or imply owner acceptance, solver evidence, measured difficulty, timing, or provider cost."
		if dashboard != null and dashboard.has_method("show_dashboard"):
			dashboard.call("show_dashboard")
	elif surface_name == "Import":
		state.text = "SOURCE INGESTION ONLY — OWNER_UPLOAD / UNVALIDATED"
		detail.text = "SOURCE ONLY — validation/candidate creation pending SB-LFX-004. The selected local PNG remains byte-identical and is stored as a content-addressed source."
		if import_surface != null and import_surface.has_method("show_import"):
			import_surface.call("show_import")
	elif surface_name == "Generate":
		state.text = "DRAFT — CORE VALIDATION: UNAVAILABLE"
		detail.text = "Editable presentation draft; canonical execution evidence is shown separately in Action result."
	elif surface_name == "Library":
		state.text = "DERIVED ASSET CATALOG — VERIFIED OWNER_UPLOAD SOURCES ONLY"
		detail.text = "Refresh re-verifies source.json and source.png. Only bounded label/tag sidecar metadata is editable."
		if library_surface != null and library_surface.has_method("show_library"):
			library_surface.call("show_library")
	elif surface_name == "Import" + " Validation":
		state.text = "CANONICAL " + "IMPORT" + " ANALYSIS — IMMUTABLE SOURCE"
		detail.text = "Run/re-run validation for an OWNER_UPLOAD source. Derived-artifact requirements are explicit; no source bytes are changed."
		if validation_surface != null and validation_surface.has_method("show_validation"):
			validation_surface.call("show_validation")
	elif surface_name == "Pipeline":
		state.text = "TRUTHFUL PIPELINE ORCHESTRATION — STOPS AT REAL BLOCKERS"
		detail.text = "Pipeline records stage lineage and never fabricates solver, difficulty, QA, or owner-review truth."
		if pipeline_surface != null and pipeline_surface.has_method("show_pipeline"):
			pipeline_surface.call("show_pipeline")
	elif surface_name in ["Candidates", "Review"]:
		state.text = "DERIVED CANDIDATE INBOX — EXPLICIT OWNER REVIEW"
		detail.text = "ACCEPT and REJECT append identity-bound evidence. Similarity is advisory only; owner review decides significance. Review history is retained and independent from QA."
		if candidates_surface != null and candidates_surface.has_method("show_candidates"):
			candidates_surface.call("show_candidates")
	elif surface_name == "Comparison":
		state.text = "READ-ONLY SIDE-BY-SIDE COMPARISON"
		detail.text = "Evidence is shown only when bound to the selected candidate/artwork identity; similarity is advisory only and owner review decides significance. Missing solver, difficulty, and cost evidence stays unavailable."
		if comparison_surface != null and comparison_surface.has_method("show_comparison"):
			comparison_surface.call("show_comparison")
	elif surface_name == "Presets":
		state.text = "VERSIONED OPERATOR PRESETS — EXPANDED CANONICAL REQUESTS"
		detail.text = "Presets are convenience records; execution history binds full resolved controls and does not depend on preset survival."
		if presets_surface != null and presets_surface.has_method("show_presets"):
			presets_surface.call("show_presets")
	elif surface_name == "Search":
		state.text = "DERIVED SEARCH / FILTER / SMART COLLECTIONS"
		detail.text = "Queries are deterministic views over canonical records. Similarity is advisory only; enter a canonical peer ID to render backend evidence, and owner review decides significance. Unavailable domains remain unavailable and no membership list is persisted."
		if search_surface != null and search_surface.has_method("show_search"):
			search_surface.call("show_search")
	elif surface_name == "Readiness":
		state.text = "IDENTITY-BOUND PRODUCTION READINESS GATES"
		detail.text = "Overall READY is impossible while solver, difficulty, QA, owner, or export authority is missing."
		if readiness_surface != null and readiness_surface.has_method("show_readiness"):
			readiness_surface.call("show_readiness")
	elif surface_name == "Reproduce":
		state.text = "CAPABILITY-GATED EXACT REPRODUCE"
		detail.text = "Recorded canonical Generate metadata is required. OWNER_UPLOAD retrieval is never mislabeled as regeneration."
		if reproduce_surface != null and reproduce_surface.has_method("show_reproduce"):
			reproduce_surface.call("show_reproduce")
	elif surface_name == "Revisions":
		state.text = "IMMUTABLE MANUAL EDIT REVISION HISTORY"
		detail.text = "Revision identities bind exact logical working grids and canonical source identity; restore and undo preserve later lineage."
		if revisions_surface != null and revisions_surface.has_method("show_revisions"):
			revisions_surface.call("show_revisions")
	elif surface_name == "Failures":
		state.text = "DERIVED FAILURE INBOX — SELECTIVE RETRY WITH LINEAGE"
		detail.text = "Original failure evidence remains immutable. Successful or unavailable stages are not retried."
		if failures_surface != null and failures_surface.has_method("show_failures"):
			failures_surface.call("show_failures")
	elif surface_name == "Batch Import":
		state.text = "PER-FILE IMMUTABLE OWNER_UPLOAD BATCH IMPORT"
		detail.text = "Partial success is truthful; same-name files retain independent SHA-derived identities and corrupt items fail independently."
		if batch_import_surface != null and batch_import_surface.has_method("show_batch_import"):
			batch_import_surface.call("show_batch_import")
	elif surface_name == "Session Recovery":
		state.text = "SESSION RECOVERY — DURABLE REFERENCES, NO SHADOW TRUTH"
		detail.text = "Restore revalidates canonical references and does not rerun successful durable stages or persist secrets."
		if session_surface != null and session_surface.has_method("show_session"):
			session_surface.call("show_session")
	elif surface_name == "Similarity":
		state.text = "ADVISORY OFFLINE VISUAL SIMILARITY"
		detail.text = "Similarity evidence is identity-bound and advisory; exact SHA/grid duplicate identity remains authoritative."
		if similarity_surface != null and similarity_surface.has_method("show_similarity"):
			similarity_surface.call("show_similarity")
	elif surface_name == "Cost Center":
		state.text = "READ-ONLY PROVIDER COST / CREDIT ACCOUNTING"
		detail.text = "Provider, currency, credit units, balance, and owner-accepted denominators remain separated; unknown values are not estimated."
		if cost_surface != null and cost_surface.has_method("show_cost"):
			cost_surface.call("show_cost")
	elif surface_name == "Release":
		state.text = "OWNER RELEASE POOL — EXPLICIT CONTIGUOUS BATCH APPROVAL"
		detail.text = "ACCEPT adds a READY level to the pool. CampaignBuilder reads current Scrubbots cadence and catalog authority; APPROVE publishes the validated contiguous prefix as one transaction."
		if release_surface != null and release_surface.has_method("show_release"):
			release_surface.call("show_release")
	else:
		state.text = "NOT IMPLEMENTED: " + surface_name + " is an inert migration placeholder."
		detail.text = "No provider, import, library, solver, QA, review, batch, or output operation is performed here."
