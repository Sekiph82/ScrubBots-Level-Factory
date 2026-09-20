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


func show_surface(surface_name: String) -> void:
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
		validation_surface.visible = surface_name == "Import Validation"
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
	elif surface_name == "Import Validation":
		state.text = "CANONICAL IMPORT ANALYSIS — IMMUTABLE SOURCE"
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
		detail.text = "ACCEPT and REJECT append identity-bound evidence. Review history is retained and independent from QA."
		if candidates_surface != null and candidates_surface.has_method("show_candidates"):
			candidates_surface.call("show_candidates")
	elif surface_name == "Comparison":
		state.text = "READ-ONLY SIDE-BY-SIDE COMPARISON"
		detail.text = "Evidence is shown only when bound to the selected candidate/artwork identity; missing solver, difficulty, and cost evidence stays unavailable."
		if comparison_surface != null and comparison_surface.has_method("show_comparison"):
			comparison_surface.call("show_comparison")
	elif surface_name == "Presets":
		state.text = "VERSIONED OPERATOR PRESETS — EXPANDED CANONICAL REQUESTS"
		detail.text = "Presets are convenience records; execution history binds full resolved controls and does not depend on preset survival."
		if presets_surface != null and presets_surface.has_method("show_presets"):
			presets_surface.call("show_presets")
	elif surface_name == "Search":
		state.text = "DERIVED SEARCH / FILTER / SMART COLLECTIONS"
		detail.text = "Queries are deterministic views over canonical records. Unavailable domains remain unavailable and no membership list is persisted."
		if search_surface != null and search_surface.has_method("show_search"):
			search_surface.call("show_search")
	elif surface_name == "Readiness":
		state.text = "IDENTITY-BOUND PRODUCTION READINESS GATES"
		detail.text = "Overall READY is impossible while solver, difficulty, QA, owner, or export authority is missing."
		if readiness_surface != null and readiness_surface.has_method("show_readiness"):
			readiness_surface.call("show_readiness")
	else:
		state.text = "NOT IMPLEMENTED: " + surface_name + " is an inert migration placeholder."
		detail.text = "No provider, import, library, solver, QA, review, batch, or output operation is performed here."
