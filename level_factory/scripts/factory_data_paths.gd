class_name FactoryDataPaths
extends RefCounted

## Shared Godot-side resolver for mutable Factory data. Installed Release files
## are executable resources only; user data always lives under the canonical
## Desktop checkout's data directory.

static func repository_root(anchor: String = "res://") -> String:
	var current := ProjectSettings.globalize_path(anchor).simplify_path()
	while not current.is_empty():
		if FileAccess.file_exists(current.path_join("TASKS.md")) and (
			DirAccess.dir_exists_absolute(current.path_join(".git"))
			or FileAccess.file_exists(current.path_join(".git"))
		):
			return current
		var parent := current.get_base_dir()
		if parent == current:
			break
		current = parent
	# An installed Release is an executable shell, not a data checkout. Resolve
	# mutable Factory data to the single canonical Desktop repository instead.
	var profile := OS.get_environment("USERPROFILE")
	if not profile.is_empty():
		var canonical := profile.path_join("Desktop").path_join("Scrubbots - Pixel Art Generator").simplify_path()
		if FileAccess.file_exists(canonical.path_join("TASKS.md")) and (
			DirAccess.dir_exists_absolute(canonical.path_join(".git"))
			or FileAccess.file_exists(canonical.path_join(".git"))
		):
			return canonical
	return ""


static func data_path(relative_path: String, anchor: String = "res://") -> String:
	if relative_path.is_empty() or relative_path.is_absolute_path():
		return ""
	for component in relative_path.replace(char(92), "/").split("/"):
		if component in ["", ".", ".."]:
			return ""
	var root := repository_root(anchor)
	if root.is_empty():
		return ""
	return root.path_join("data").path_join(relative_path).simplify_path()


static func output_path(relative_path: String = "", anchor: String = "res://") -> String:
	var suffix := "output" if relative_path.is_empty() else "output/" + relative_path
	return data_path(suffix, anchor)


## True when an existing canonical bundle path sits in an approved Studio area:
## data/output (where the gateway writes Generate/Reproduce bundles) or
## data/Level Factory/Workspace (Candidates, Reproductions, Preset Runs).
static func is_studio_bundle_path(path: String, anchor: String = "res://") -> bool:
	if path.is_empty():
		return false
	var candidate := ProjectSettings.globalize_path(path) if path.begins_with("res://") or not path.is_absolute_path() else path
	candidate = candidate.simplify_path().replace(char(92), "/").to_lower()
	for root in [output_path("", anchor), data_path("Level Factory/Workspace", anchor)]:
		if root.is_empty():
			continue
		var normalized: String = root.simplify_path().replace(char(92), "/").to_lower()
		if candidate == normalized or candidate.begins_with(normalized + "/"):
			return true
	return false
