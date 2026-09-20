@tool
class_name FactoryStudioSimilarity
extends VBoxContainer

var _gateway: RefCounted

func _ready() -> void:
	if get_child_count() == 0:
		var heading := Label.new(); heading.text = "Advisory Visual Similarity — exact identity remains stronger"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
		var notice := Label.new(); notice.text = "LOGICAL_CELL_HAMMING_V1 is offline, identity-bound, deterministic, and advisory. POSSIBLE_SIMILAR never auto-rejects, accepts, ranks, or mutates review."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)

func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway
func show_similarity() -> void: pass
func snapshot() -> Dictionary: return {"state": "AVAILABLE", "advisory_only": true}
