@tool
extends VBoxContainer

var _gateway: RefCounted
var _projection: Dictionary = {}
var _locks: Dictionary = {}
var _pool_label: Label
var _k: SpinBox
var _order: SpinBox
var _candidate: LineEdit
var _rows: RichTextLabel
var _status: Label
var _publish_candidates: LineEdit
var _publish_pack_id: LineEdit
var _publish_version: SpinBox
var _publish_game_sha: LineEdit


func _ready() -> void:
	if get_child_count() > 0: return
	var title := Label.new(); title.text = "Campaign Release"; title.add_theme_font_size_override("font_size", 22); add_child(title)
	_pool_label = Label.new(); add_child(_pool_label)
	var controls := HBoxContainer.new(); add_child(controls)
	_k = SpinBox.new(); _k.min_value = 1; _k.max_value = 1000; _k.value = 100; _k.prefix = "K "; controls.add_child(_k)
	var build := Button.new(); build.text = "Build / Refresh Plan"; build.pressed.connect(refresh_plan); controls.add_child(build)
	_order = SpinBox.new(); _order.min_value = 1; _order.max_value = 100000; _order.prefix = "Catalog order "; controls.add_child(_order)
	_candidate = LineEdit.new(); _candidate.placeholder_text = "Accepted candidate ID"; controls.add_child(_candidate)
	var lock := Button.new(); lock.text = "Lock / Swap"; lock.pressed.connect(_lock_candidate); controls.add_child(lock)
	_rows = RichTextLabel.new(); _rows.fit_content = true; _rows.scroll_active = true; _rows.custom_minimum_size.y = 340; add_child(_rows)
	var public_warning := Label.new(); public_warning.text = "PUBLIC REPOSITORY: unreleased levels become publicly visible when the release branch is pushed."; public_warning.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; public_warning.add_theme_color_override("font_color", Color(1.0, 0.72, 0.3)); add_child(public_warning)
	_status = Label.new(); _status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_status)
	var approve := Button.new(); approve.text = "APPROVE and Open Release PR"; approve.pressed.connect(_approve); add_child(approve)
	var publish_title := Label.new(); publish_title.text = "ScrubBots Content Pipeline"; publish_title.add_theme_font_size_override("font_size", 18); add_child(publish_title)
	_publish_candidates = LineEdit.new(); _publish_candidates.placeholder_text = "Comma-separated owner-accepted Release Pool candidate IDs"; add_child(_publish_candidates)
	_publish_pack_id = LineEdit.new(); _publish_pack_id.placeholder_text = "Deterministic pack ID"; add_child(_publish_pack_id)
	_publish_version = SpinBox.new(); _publish_version.min_value = 1; _publish_version.max_value = 2147483647; _publish_version.prefix = "Content version "; add_child(_publish_version)
	_publish_game_sha = LineEdit.new(); _publish_game_sha.placeholder_text = "Verified game main commit SHA"; add_child(_publish_game_sha)
	var preflight := Button.new(); preflight.text = "Preflight Publish to ScrubBots"; preflight.pressed.connect(_publish_preflight); add_child(preflight)
	refresh_pool()


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func show_release() -> void:
	refresh_pool()


func refresh_pool() -> void:
	if _gateway == null: return
	var result: Dictionary = _gateway.call("run_studio_extension", "release-pool", {})
	_pool_label.text = "Release Pool: %s accepted READY levels | requested batch K: %d" % [str(result.get("pool_size", 0)), int(_k.value)]
	_status.text = str(result.get("reason", result.get("error", "Owner ACCEPT enters a READY level in the pool; publication requires this batch plan's APPROVE.")))


func refresh_plan() -> void:
	if _gateway == null: return
	_projection = _gateway.call("run_studio_extension", "campaign-build", {"k": int(_k.value), "locks": _locks})
	_render_plan()


func _lock_candidate() -> void:
	var identity := _candidate.text.strip_edges()
	var order := int(_order.value)
	if identity.is_empty(): _status.text = "Enter a Release Pool candidate ID and catalog order."; return
	_locks[order] = identity
	refresh_plan()


func _approve() -> void:
	if _projection.is_empty() or str(_projection.get("plan_hash", "")).is_empty(): _status.text = "Build a valid plan before approval."; return
	var result: Dictionary = _gateway.call("run_studio_extension", "campaign-approve", {"plan_hash": _projection["plan_hash"]})
	var receipt: Dictionary = result.get("receipt", {})
	if not receipt.is_empty():
		_status.text = "Release PR opened: %s\nBranch: %s | commit: %s\nReceipt saved: %s\nPUBLIC: unreleased levels are visible on GitHub." % [str(receipt.get("pr_url", "")), str(receipt.get("branch", "")), str(receipt.get("game_commit_sha", "")), str(result.get("receipt_path", ""))]
	else:
		_status.text = "%s — %s" % [str(result.get("disposition", result.get("state", "ERROR"))), str(result.get("reason", result.get("error", result.get("orders", []))))]
	refresh_pool()


func _publish_preflight() -> void:
	if _gateway == null: return
	var candidate_ids := PackedStringArray()
	for raw_id in _publish_candidates.text.split(","):
		var candidate_id := raw_id.strip_edges()
		if not candidate_id.is_empty(): candidate_ids.append(candidate_id)
	var created_at := Time.get_datetime_string_from_system(true, false)
	var result: Dictionary = _gateway.call("run_studio_extension", "scrubbots-publish", {
		"action": "preflight", "candidate_ids": Array(candidate_ids),
		"pack_id": _publish_pack_id.text.strip_edges(), "content_version": int(_publish_version.value),
		"scrubbots_main_sha": _publish_game_sha.text.strip_edges(), "created_at_utc": created_at,
	})
	_status.text = JSON.stringify(result, "  ")


func _render_plan() -> void:
	var slots: Array = _projection.get("slots", [])
	var lines := PackedStringArray(["ORDER  SLOT  CLASS / ROLE       TARGET    ACTUAL   DELTA  TIER  CHECKS"])
	for row in slots:
		var checks: Dictionary = row.get("checks", {})
		var warnings := "" if checks.get("recovery_guard", true) and checks.get("profile", true) and checks.get("similarity_ok", true) and checks.get("novelty_ok", true) else "WARNING"
		lines.append("%5s  %4s  %-16s  %7.2f  %7s  %5s  %4s  %s" % [str(row.get("n", "")), str(row.get("slot", "")), str(row.get("class", "")) + " / " + str(row.get("role", "")), float(row.get("target", 0.0)), str(row.get("D", "EMPTY")), str(row.get("delta", "—")), str(row.get("tier", "—")), warnings])
	_rows.text = "\n".join(lines)
	_status.text = "Plan %s | prefix %d | shortages %d\n%s" % [str(_projection.get("plan_hash", "INVALID")), ( _projection.get("publishable_prefix", []) as Array).size(), (_projection.get("shortages", []) as Array).size(), "\n".join(_projection.get("warnings", []))]
