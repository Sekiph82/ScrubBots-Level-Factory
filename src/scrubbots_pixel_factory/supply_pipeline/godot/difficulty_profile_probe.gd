extends SceneTree

const Analyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		push_error("Expected one JSON object containing the stored official Difficulty V1 vector.")
		quit(2)
		return
	var vector: Variant = JSON.parse_string(args[0])
	if not vector is Dictionary:
		push_error("Stored official Difficulty V1 vector must be a JSON object.")
		quit(2)
		return
	for axis in ["W", "C", "A", "U", "B", "R", "S"]:
		if not vector.has(axis) or not (vector[axis] is int or vector[axis] is float) or is_nan(float(vector[axis])) or is_inf(float(vector[axis])):
			push_error("Stored official Difficulty V1 vector is incomplete or non-finite.")
			quit(2)
			return
	var profile: Dictionary = Analyzer.profile(vector)
	print("AUTHENTIC_V1_PROFILE:" + JSON.stringify(profile))
	quit(0)
