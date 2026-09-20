@tool
class_name FactoryStudioWorkspacePage
extends PanelContainer

@onready var target_controls: Node = $Padding/Content/TargetControls
@onready var content: VBoxContainer = $Padding/Content

const DASHBOARD_SCRIPT_PATH := "res://scripts/factory_studio_dashboard.gd"
var dashboard: Node


func _ready() -> void:
	_ensure_dashboard()


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


func configure_gateway(gateway: RefCounted) -> void:
	if target_controls != null and target_controls.has_method("configure_gateway"):
		target_controls.call("configure_gateway", gateway)
	if dashboard != null and dashboard.has_method("configure_gateway"):
		dashboard.call("configure_gateway", gateway)
	if dashboard != null and dashboard.has_method("configure_action_source"):
		dashboard.call("configure_action_source", target_controls)


func show_surface(surface_name: String) -> void:
	var title: Label = $Padding/Content/Title
	var state: Label = $Padding/Content/State
	var detail: Label = $Padding/Content/Detail
	target_controls.visible = surface_name == "Generate"
	if dashboard != null:
		dashboard.visible = surface_name == "Dashboard"
	title.text = "Factory Studio — " + surface_name
	if surface_name == "Dashboard":
		state.text = "READ-ONLY DERIVED VIEW — canonical batch evidence (NOT AVAILABLE until a canonical manifest is selected)"
		detail.text = "No generated data is loaded until Dashboard refresh reads a validated batch-manifest.json under res://output/. It does not mutate canonical records or imply owner acceptance, solver evidence, measured difficulty, timing, or provider cost."
		if dashboard != null and dashboard.has_method("show_dashboard"):
			dashboard.call("show_dashboard")
	elif surface_name == "Generate":
		state.text = "DRAFT — CORE VALIDATION: UNAVAILABLE"
		detail.text = "Editable presentation draft; canonical execution evidence is shown separately in Action result."
	else:
		state.text = "NOT IMPLEMENTED: " + surface_name + " is an inert migration placeholder."
		detail.text = "No provider, import, library, solver, QA, review, batch, or output operation is performed here."
