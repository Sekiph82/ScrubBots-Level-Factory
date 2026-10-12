extends SceneTree

const MAIN_SCENE := "res://scenes/factory_studio.tscn"


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var packed := load(MAIN_SCENE) as PackedScene
	if packed == null:
		push_error("R09-R02 activity test: Factory Studio scene did not load")
		quit(1)
		return
	var instance := packed.instantiate()
	root.add_child(instance)
	await process_frame
	var studio := instance.get_node_or_null("MasterUI")
	var panel := studio.get_node_or_null("PipelineActivityPanel") as Panel if studio != null else null
	var label := studio.get_node_or_null("PipelineActivityText") as Label if studio != null else null
	if panel == null or label == null:
		push_error("R09-R02 activity test: approved panel controls are missing")
		instance.queue_free()
		quit(1)
		return
	studio.size = Vector2(1536, 1024)
	studio.call("_apply_responsive_layout")
	if panel.position != Vector2(27, 540) or panel.size != Vector2(334, 250):
		push_error("R09-R02 activity test: panel geometry changed from owner-approved rectangle")
		instance.queue_free()
		quit(1)
		return
	if panel.visible or label.visible:
		push_error("R09-R02 activity test: panel leaked into PIXEL ART")
		instance.queue_free()
		quit(1)
		return
	studio.call("_show_screen", "LEVEL FACTORY")
	await process_frame
	if not panel.visible or not label.visible or not label.text.begins_with("PIPELINE ACTIVITY"):
		push_error("R09-R02 activity test: panel did not appear inside LEVEL FACTORY")
		instance.queue_free()
		quit(1)
		return
	if bool(studio.get("_operation_running")) or studio.get("_pipeline_thread") != null:
		push_error("R09-R02 activity test: screen selection automatically executed the pipeline")
		instance.queue_free()
		quit(1)
		return
	for screen in ["PIXEL ART", "RELEASE POOL"]:
		studio.call("_show_screen", screen)
		await process_frame
		if panel.visible or label.visible:
			push_error("R09-R02 activity test: panel leaked outside LEVEL FACTORY")
			instance.queue_free()
			quit(1)
			return
	if OS.get_environment("SB_LFX_R09_R02_CAPTURE_RELEASE_UI") == "1":
		studio.call("_show_screen", "LEVEL FACTORY")
		await process_frame
		await process_frame
		var image := root.get_viewport().get_texture().get_image()
		var evidence_path := ProjectSettings.globalize_path("res://../owner-visual-evidence/SB-LFX-018-C001-R02-R05-R09-R02-release-level-factory-viewport.png")
		if image == null or image.is_empty() or FileAccess.file_exists(evidence_path) or image.save_png(evidence_path) != OK:
			push_error("R09-R02 activity test: installed Release viewport screenshot could not be captured safely")
			instance.queue_free()
			quit(1)
			return
	instance.queue_free()
	print("R09-R02 Studio activity UI test: PASS")
	quit(0)
