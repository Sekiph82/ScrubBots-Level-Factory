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
var owner_live_details: RichTextLabel
var owner_interaction_row: HFlowContainer
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
var owner_projection: Dictionary = {}
var selected_owner_candidate_id := ""
var selected_owner_query := ""
var selected_owner_collection := "ALL"

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
	owner_live_details = RichTextLabel.new()
	owner_live_details.name = "OwnerLiveDetails"
	owner_live_details.fit_content = true
	owner_live_details.scroll_active = true
	owner_live_details.custom_minimum_size.y = 92
	owner_live_details.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_live_details.bbcode_enabled = false
	owner_page.add_child(owner_live_details)
	owner_interaction_row = HFlowContainer.new()
	owner_interaction_row.name = "OwnerPageActions"
	owner_interaction_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	owner_page.add_child(owner_interaction_row)
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
			if child == release_surface:
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
	_refresh_owner_projection()
	_refresh_owner_state()
	_refresh_owner_preview()
	_render_owner_route_details()
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
	var candidates: Array = owner_projection.get("candidates", [])
	var pipelines: Array = owner_projection.get("pipelines", [])
	var batches: Array = owner_projection.get("batches", [])
	var failures: Array = owner_projection.get("failures", [])
	var accepted := 0
	var reviewed := 0
	var ready_runs := {}
	for candidate in candidates:
		var review_state := str(candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW"))
		if review_state == "ACCEPT": accepted += 1
		if review_state in ["ACCEPT", "REJECT"]: reviewed += 1
	for pipeline in pipelines:
		if str(pipeline.get("disposition", "")) == "READY":
			ready_runs[str(pipeline.get("candidate_id", pipeline.get("source_id", pipeline.get("run_id", ""))))] = true
	if not batches.is_empty() or not candidates.is_empty():
		var latest_batch: Dictionary = batches[0] if not batches.is_empty() else {}
		var item_count := (latest_batch.get("items", []) as Array).size()
		var imported_count := int(latest_batch.get("counts", {}).get("success", 0)) if item_count > 0 else candidates.size()
		states = ["%d imported" % imported_count, "%d solved" % ready_runs.size(), "%d needs attention" % maxi(failures.size(), int(latest_batch.get("counts", {}).get("failed", 0))), "%d reviewed" % reviewed, "%d accepted" % accepted]
	if active_owner_route == "SOLVE" and not selected_owner_candidate_id.is_empty():
		var current_pipeline := _latest_candidate_pipeline(selected_owner_candidate_id)
		states = [selected_owner_candidate_id, str(current_pipeline.get("request", {}).get("column_count", "3/4/5 columns")), str(current_pipeline.get("disposition", "Not run")), "Readiness", str(current_pipeline.get("disposition", "Not started"))]
	if active_owner_route == "PUBLISH":
		states[0] = "%d accepted" % owner_projection.get("release_entries", []).size()
		states[3] = "Preflight pending"
	if active_owner_route == "LIBRARY":
		states[0] = "%d sources" % owner_projection.get("sources", []).size()
		states[1] = "%d candidates" % candidates.size()
	if target_controls != null and target_controls.has_method("last_successful_core_evidence_snapshot"):
		var last_success: Dictionary = target_controls.call("last_successful_core_evidence_snapshot")
		if last_success.get("state", "") == "SUCCESS":
			states[0] = "Generated"
	for index in range(labels.size()):
		var status_label := owner_state_cards.find_child(str(labels[index]), true, false) as Label
		if status_label != null:
			status_label.text = str(states[index])


func _refresh_owner_projection() -> void:
	if core_gateway == null:
		owner_projection = {"state": "UNAVAILABLE", "reason": "Canonical local core is not connected."}
		return
	var result: Variant = core_gateway.call("run_studio_extension", "owner-pages", {})
	owner_projection = result.duplicate(true) if result is Dictionary else {"state": "ERROR", "reason": "Canonical owner projection returned no structured record."}


func _render_owner_route_details() -> void:
	if owner_live_details == null:
		return
	var candidates: Array = owner_projection.get("candidates", [])
	var sources: Array = owner_projection.get("sources", [])
	var batches: Array = owner_projection.get("batches", [])
	var failures: Array = owner_projection.get("failures", [])
	var lines := PackedStringArray()
	match active_owner_route:
		"HOME", "BATCH":
			if batches.is_empty() and candidates.is_empty():
				lines.append("No canonical batch or candidate evidence yet.")
			else:
				var batch: Dictionary = batches[0] if not batches.is_empty() else {}
				var items: Array = batch.get("items", [])
				var imported := int(batch.get("counts", {}).get("success", 0))
				var needs_attention := int(batch.get("counts", {}).get("failed", 0))
				var accepted := 0
				var reviewed := 0
				var solved_ids := {}
				for candidate in candidates:
					var disposition := str(candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW"))
					if disposition in ["ACCEPT", "REJECT"]: reviewed += 1
					if disposition == "ACCEPT": accepted += 1
				for pipeline in owner_projection.get("pipelines", []):
					if str(pipeline.get("disposition", "")) == "READY":
						var solved_id := str(pipeline.get("candidate_id", pipeline.get("source_id", pipeline.get("run_id", ""))))
						solved_ids[solved_id] = true
				needs_attention = maxi(needs_attention, failures.size())
				lines.append("Latest batch %s · %s" % [str(batch.get("batch_id", "No batch")), str(batch.get("created_at", ""))])
				lines.append("Imported %d  ·  Solved %d  ·  Needs attention %d  ·  Reviewed %d  ·  Accepted %d" % [imported if not items.is_empty() else candidates.size(), solved_ids.size(), needs_attention, reviewed, accepted])
				lines.append("Progress %d / %d" % [imported, items.size()] if not items.is_empty() else "Candidate items %d" % candidates.size())
				for item in items.slice(0, 5): lines.append("• %s  —  %s" % [str(item.get("display_path", item.get("source_id", "Artwork"))), _batch_item_status(item)])
				for candidate in candidates.slice(0, 4): lines.append("• %s  —  %s" % [str(candidate.get("candidate_id", "")), str(candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW"))])
			if active_owner_route == "BATCH":
				lines.append("Eligible retries: %d" % failures.filter(func(failure): return bool(failure.get("retryable", false))).size())
		"CREATE":
			lines.append("Choose one local PNG for immutable OWNER_UPLOAD, or select multiple PNGs for a canonical batch.")
			lines.append("Imported sources: %d  ·  Candidate records: %d" % [sources.size(), candidates.size()])
		"SOLVE":
			var candidate := _owner_candidate(selected_owner_candidate_id)
			lines.append("Artwork: %s" % (selected_owner_candidate_id if not selected_owner_candidate_id.is_empty() else "Select a canonical candidate in Review or the candidate tools."))
			lines.append("Supply columns: 3 / 4 / 5 · pipeline/solver/replay/Difficulty V1 evidence is shown only when recorded by the canonical pipeline.")
			if not candidate.is_empty():
				var readiness: Dictionary = core_gateway.call("run_studio_extension", "readiness", {"candidate_id": selected_owner_candidate_id}) if core_gateway != null else {}
				var pipeline := _latest_candidate_pipeline(selected_owner_candidate_id)
				var primary: Dictionary = pipeline.get("primary", {})
				var difficulty: Dictionary = primary.get("difficulty", {})
				lines.append("Supply %s columns · Solver %s · Replay %s · Difficulty V1 %s %s · Readiness %s" % [str(pipeline.get("request", {}).get("column_count", "NOT AVAILABLE")), str(readiness.get("gates", {}).get("SOLVER", {}).get("disposition", "NOT AVAILABLE")), str(readiness.get("gates", {}).get("QA", {}).get("disposition", "NOT AVAILABLE")), str(difficulty.get("score", "NOT AVAILABLE")), str(difficulty.get("class", "")), str(readiness.get("overall", "NOT AVAILABLE"))])
		"REVIEW":
			var candidate := _owner_candidate(selected_owner_candidate_id)
			if candidate.is_empty(): lines.append("Select a candidate to inspect canonical identity, supply, solver, Difficulty V1, readiness, and owner-review history.")
			else:
				var readiness: Dictionary = core_gateway.call("run_studio_extension", "readiness", {"candidate_id": selected_owner_candidate_id}) if core_gateway != null else {}
				lines.append("Candidate %s · %sx%s · %s" % [selected_owner_candidate_id, str(candidate.get("width", "?")), str(candidate.get("height", "?")), str(candidate.get("artwork_sha256", ""))])
				var pipeline := _latest_candidate_pipeline(selected_owner_candidate_id)
				var primary: Dictionary = pipeline.get("primary", {})
				var difficulty: Dictionary = primary.get("difficulty", {})
				lines.append("Supply %s columns · Solver %s · Replay %s · Difficulty V1 %s %s" % [str(pipeline.get("request", {}).get("column_count", "NOT AVAILABLE")), str(readiness.get("gates", {}).get("SOLVER", {}).get("disposition", "NOT AVAILABLE")), str(readiness.get("gates", {}).get("QA", {}).get("disposition", "NOT AVAILABLE")), str(difficulty.get("score", "NOT AVAILABLE")), str(difficulty.get("class", ""))])
				lines.append("Structural %s · Owner %s · Readiness %s · History %s" % [str(candidate.get("quality", {}).get("decision", "NOT AVAILABLE")), str(candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW")), str(readiness.get("overall", "NOT AVAILABLE")), str(candidate.get("owner_review_history", []))])
		"LIBRARY":
			var discovery: Dictionary = core_gateway.call("run_studio_extension", "discover", {"query": selected_owner_query, "collection": selected_owner_collection if selected_owner_collection != "ALL" else null}) if core_gateway != null else {}
			var records: Array = discovery.get("records", [])
			lines.append("Search: %s  ·  %d canonical results" % [selected_owner_query if not selected_owner_query.is_empty() else "All", records.size()])
			for record in records.slice(0, 8): lines.append("• %s  %s  —  %s" % [str(record.get("record_type", "")), str(record.get("record_id", "")), str(record.get("review", record.get("qa", "UNKNOWN")))])
		"PUBLISH":
			var entries: Array = owner_projection.get("release_entries", [])
			lines.append("Accepted Levels (%d)  →  Campaign Order  →  Preflight  →  STAGING  →  Production Approval" % entries.size())
			lines.append("Authoritative content version: shown by campaign preflight when available · STAGING: not started · Production approval: separate owner action")
			for index in range(mini(entries.size(), 5)):
				var entry: Dictionary = entries[index]
				lines.append("• Level %d  %s  ·  %s" % [index + 1, str(entry.get("candidate_id", "")), str(entry.get("disposition", "ACCEPTED"))])
			lines.append("Production promotion remains a separate owner-controlled step after STAGING.")
		"SETTINGS":
			lines.append("Provider: NOT AVAILABLE unless reported by a configured provider authority.")
			lines.append("Core/runtime: %s · %s" % [_system_state_name(), core_gateway.status_message() if core_gateway != null else "Local core is not connected."])
			var costs: Dictionary = core_gateway.call("run_studio_extension", "cost-center", {}) if core_gateway != null else {}
			lines.append("Cost/credits: %s" % str(costs.get("state", "NOT AVAILABLE")))
	owner_live_details.text = "\n".join(lines)
	for child in owner_interaction_row.get_children():
		child.queue_free()
	match active_owner_route:
		"CREATE":
			var one := Button.new(); one.text = "Choose one PNG"; one.pressed.connect(_open_tool.bind("Import")); owner_interaction_row.add_child(one)
			var many := Button.new(); many.text = "Choose multiple PNGs"; many.pressed.connect(_open_tool.bind("Batch Import")); owner_interaction_row.add_child(many)
			var validate := Button.new(); validate.text = "Validation and preparation"; validate.pressed.connect(_open_tool.bind("Import Validation")); owner_interaction_row.add_child(validate)
		"HOME", "BATCH":
			var continue_batch := Button.new(); continue_batch.text = "Continue Batch"; continue_batch.pressed.connect(_continue_owner_batch); owner_interaction_row.add_child(continue_batch)
			var resume := Button.new(); resume.text = "Resume / Recover"; resume.pressed.connect(_open_tool.bind("Session Recovery")); owner_interaction_row.add_child(resume)
			if active_owner_route == "BATCH":
				var retry := Button.new(); retry.text = "Retry eligible failures"; retry.pressed.connect(_retry_owner_failure); owner_interaction_row.add_child(retry)
		"SOLVE":
			var choose := OptionButton.new(); choose.name = "SolveCandidate"; _populate_candidate_choices(choose); owner_interaction_row.add_child(choose)
			var columns := OptionButton.new(); columns.name = "SolveColumnCount"; columns.add_item("3 columns"); columns.add_item("4 columns"); columns.add_item("5 columns"); owner_interaction_row.add_child(columns)
			var solve := Button.new(); solve.text = "Solve / Re-solve"; solve.pressed.connect(_run_owner_pipeline.bind(choose, columns)); owner_interaction_row.add_child(solve)
		"REVIEW":
			var choose := OptionButton.new(); choose.name = "ReviewCandidate"; _populate_candidate_choices(choose); owner_interaction_row.add_child(choose)
			var accept := Button.new(); accept.text = "ACCEPT"; accept.pressed.connect(_review_owner_candidate.bind(choose, "ACCEPT")); owner_interaction_row.add_child(accept)
			var reject := Button.new(); reject.text = "REJECT"; reject.pressed.connect(_review_owner_candidate.bind(choose, "REJECT")); owner_interaction_row.add_child(reject)
			var compare := Button.new(); compare.text = "Compare"; compare.pressed.connect(_open_tool.bind("Comparison")); owner_interaction_row.add_child(compare)
		"LIBRARY":
			var query := LineEdit.new(); query.name = "LibrarySearch"; query.placeholder_text = "Search artwork and candidates"; query.text = selected_owner_query; query.size_flags_horizontal = Control.SIZE_EXPAND_FILL; owner_interaction_row.add_child(query)
			var search := Button.new(); search.text = "Search"; search.pressed.connect(_search_owner_library.bind(query)); owner_interaction_row.add_child(search)
			var filter := OptionButton.new(); filter.name = "LibraryFilter"; filter.add_item("All records"); filter.add_item("Imported Sources"); filter.add_item("Needs Review"); filter.add_item("Owner Accepted"); filter.add_item("Owner Rejected"); filter.item_selected.connect(_select_owner_collection); filter.select(_owner_collection_index()); owner_interaction_row.add_child(filter)
		"PUBLISH":
			var release := Button.new(); release.text = "Campaign order / preflight / STAGING"; release.pressed.connect(_open_tool.bind("Release")); owner_interaction_row.add_child(release)
		"SETTINGS":
			for entry in [["Providers", "Providers"], ["Cost / credits", "Cost Center"], ["Recovery", "Session Recovery"], ["Diagnostics", "Diagnostics"]]:
				var button := Button.new(); button.text = entry[0]; button.pressed.connect(_open_tool.bind(entry[1])); owner_interaction_row.add_child(button)


func _populate_candidate_choices(control: OptionButton) -> void:
	control.add_item("Select candidate")
	for candidate in owner_projection.get("candidates", []):
		control.add_item(str(candidate.get("candidate_id", "")))
		if str(candidate.get("candidate_id", "")) == selected_owner_candidate_id:
			control.select(control.item_count - 1)
	control.item_selected.connect(_select_owner_candidate.bind(control))


func _select_owner_candidate(index: int, control: OptionButton) -> void:
	if index > 0:
		selected_owner_candidate_id = control.get_item_text(index)
		_refresh_owner_preview()
		_render_owner_route_details()


func _review_owner_candidate(control: OptionButton, disposition: String) -> void:
	if core_gateway == null or control.selected <= 0:
		return
	var candidate_id := control.get_item_text(control.selected)
	var result: Dictionary = core_gateway.call("run_studio_extension", "owner-review", {"candidate_id": candidate_id, "disposition": disposition})
	selected_owner_candidate_id = candidate_id
	_refresh_owner_projection()
	_render_owner_route_details()
	owner_live_details.text += "\nOwner review: %s · %s" % [disposition, str(result.get("review_id", result.get("state", "RECORDED")))]


func _run_owner_pipeline(control: OptionButton, columns: OptionButton) -> void:
	if core_gateway == null or control.selected <= 0:
		return
	selected_owner_candidate_id = control.get_item_text(control.selected)
	var column_count := 3 + columns.selected
	var result: Dictionary = core_gateway.call("run_studio_extension", "pipeline", {"candidate_id": selected_owner_candidate_id, "request": {"column_count": column_count}})
	_refresh_owner_projection()
	_render_owner_route_details()
	owner_live_details.text += "\nCanonical pipeline %s · %s columns" % [str(result.get("disposition", result.get("state", "UNKNOWN"))), column_count]


func _search_owner_library(control: LineEdit) -> void:
	selected_owner_query = control.text.strip_edges()
	_render_owner_route_details()


func _select_owner_collection(index: int) -> void:
	selected_owner_collection = ["ALL", "Imported Sources", "Needs Review", "Owner Accepted", "Owner Rejected"][index]
	_render_owner_route_details()


func _owner_collection_index() -> int:
	var values := ["ALL", "Imported Sources", "Needs Review", "Owner Accepted", "Owner Rejected"]
	return values.find(selected_owner_collection)


func _continue_owner_batch() -> void:
	var batches: Array = owner_projection.get("batches", [])
	if batches.is_empty():
		_open_tool("Batch Import")
		return
	var batch: Dictionary = batches[0]
	for item in batch.get("items", []):
		var source_id := str(item.get("source_id", ""))
		if not source_id.is_empty():
			var result: Dictionary = core_gateway.call("run_studio_extension", "pipeline", {"source_id": source_id}) if core_gateway != null else {}
			owner_live_details.text += "\nContinue %s · %s" % [source_id, str(result.get("disposition", result.get("state", "UNAVAILABLE")))]
			break


func _retry_owner_failure() -> void:
	if core_gateway == null:
		return
	for failure in owner_projection.get("failures", []):
		if bool(failure.get("retryable", false)):
			var result: Dictionary = core_gateway.call("run_studio_extension", "retry-failure", {"failure_id": failure.get("failure_id", "")})
			owner_live_details.text += "\nRetry %s · %s" % [str(failure.get("failure_id", "")), str(result.get("disposition", result.get("state", "UNKNOWN")))]
			return
	owner_live_details.text += "\nNo canonical failure is currently marked retryable."


func _owner_candidate(candidate_id: String) -> Dictionary:
	for candidate in owner_projection.get("candidates", []):
		if str(candidate.get("candidate_id", "")) == candidate_id:
			return candidate
	return {}


func _latest_candidate_pipeline(candidate_id: String) -> Dictionary:
	for pipeline in owner_projection.get("pipelines", []):
		if str(pipeline.get("candidate_id", "")) == candidate_id:
			return pipeline
	return {}


func _batch_item_status(item: Dictionary) -> String:
	var source_id := str(item.get("source_id", ""))
	for pipeline in owner_projection.get("pipelines", []):
		if not source_id.is_empty() and str(pipeline.get("source_id", "")) == source_id:
			var stages: Array = pipeline.get("stages", [])
			var last_stage: Dictionary = stages.back() if not stages.is_empty() else {}
			return "%s · %s" % [str(pipeline.get("disposition", "UNKNOWN")), str(last_stage.get("stage", "Pipeline"))]
	return str(item.get("disposition", "UNKNOWN"))


func _refresh_owner_preview() -> void:
	var image: Image = null
	if active_owner_route in ["SOLVE", "REVIEW"] and not selected_owner_candidate_id.is_empty():
		var candidate := _owner_candidate(selected_owner_candidate_id)
		var relative_artwork := str(candidate.get("artwork_path", ""))
		if not relative_artwork.is_empty():
			var repository_root := ProjectSettings.globalize_path("res://").get_base_dir()
			var candidate_image := Image.new()
			if candidate_image.call("load", repository_root.path_join(relative_artwork)) == OK:
				image = candidate_image
	if target_controls != null:
		if image == null:
			var preview := target_controls.get_node_or_null("ActionArea/CanonicalArtworkPreview")
			if preview != null and preview.has_method("displayed_image_snapshot"):
				image = preview.call("displayed_image_snapshot") as Image
	var empty_state := owner_page.find_child("PreviewEmptyState", true, false) as Label
	if image != null and not image.is_empty():
		owner_preview_texture.texture = ImageTexture.create_from_image(image)
		owner_preview_texture.visible = true
		empty_state.visible = false
		var snapshot: Dictionary = target_controls.call("action_result_snapshot") if target_controls.has_method("action_result_snapshot") else {}
		var candidate_caption := selected_owner_candidate_id if active_owner_route in ["SOLVE", "REVIEW"] and not selected_owner_candidate_id.is_empty() else str(snapshot.get("candidate_id", "candidate"))
		owner_preview_caption.text = "Canonical artwork · %s" % candidate_caption
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
		if active_tool_node.get_parent() == null:
			content.add_child(active_tool_node)
	_show_legacy_surface(surface_name)


func show_surface(surface_name: String) -> void:
	if OWNER_PAGES.has(surface_name):
		_show_owner_page(surface_name)
		return
	_open_tool(surface_name)


func set_visual_evidence_fixture(route: String) -> void:
	"""Harness-only display fixture. It never calls a core operation or writes evidence."""
	if not OWNER_PAGES.has(route):
		return
	active_owner_route = route
	var examples := {
		"HOME": "VISUAL FIXTURE — not canonical data\nImported 8 · Solved 5 · Needs attention 1 · Reviewed 4 · Accepted 3\nProgress 6 / 8\n• Coral Reef · READY   • Moon Garden · SOLVING   • Glass Harbor · NEEDS ATTENTION",
		"CREATE": "VISUAL FIXTURE — source entry controls\nChoose one strict PNG or a group. Original logical pixels remain unchanged.\nValidation: waiting for selected source.",
		"BATCH": "VISUAL FIXTURE — not canonical data\nProgress 6 / 8 · Imported 8 · Processing 1 · Success 5 · Needs attention 1\n• Coral Reef · READY   • Moon Garden · PROCESSING   • Glass Harbor · RETRY AVAILABLE",
		"SOLVE": "VISUAL FIXTURE — not solver evidence\nArtwork: Coral Reef · Supply columns: 4 · Supply plan: 24 entries\nSolver: SOLVED · Replay: WIN · Difficulty V1: 42 / STANDARD",
		"REVIEW": "VISUAL FIXTURE — no owner decision recorded\nCandidate: Coral Reef · Supply 4 columns · Solver SOLVED · Difficulty V1 42 / STANDARD\nReadiness: READY FOR OWNER REVIEW · ACCEPT / REJECT are available below.",
		"LIBRARY": "VISUAL FIXTURE — not canonical catalog data\n6 matching records\n• Coral Reef · ACCEPT · 32×32   • Moon Garden · NEEDS REVIEW · 24×24   • Glass Harbor · REJECT · 16×16",
		"PUBLISH": "VISUAL FIXTURE — no release occurred\nAccepted Levels → Campaign Order → Preflight → STAGING → Production Approval\nSTAGING: NOT STARTED · Production approval: PENDING OWNER ACTION",
		"SETTINGS": "VISUAL FIXTURE — example values only\nProvider: NOT CONFIGURED · Runtime: LOCAL CORE AVAILABLE\nCost / credits: UNKNOWN · Recovery: available · Diagnostics: available",
	}
	owner_live_details.text = str(examples[route])


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
	core_gateway = gateway
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
	_refresh_owner_projection()
	_render_owner_route_details()


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
