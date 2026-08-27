extends Node3D

@export var visual_state_path: String = "user://visual_state.json"
@export var poll_interval_s: float = 0.05

@onready var mesh_instance: MeshInstance3D = $Mesh
@onready var status_label: Label = $HUD/Panel/VBox/Status
@onready var metrics_label: Label = $HUD/Panel/VBox/Metrics

var _elapsed := 0.0
var _last_modified := 0
var _material: ShaderMaterial

func _ready() -> void:
    _material = mesh_instance.get_active_material(0) as ShaderMaterial
    status_label.text = "Waiting for Python visual state…"

func _process(delta: float) -> void:
    _elapsed += delta
    if _elapsed < poll_interval_s:
        return
    _elapsed = 0.0
    _poll_visual_state()

func _poll_visual_state() -> void:
    if not FileAccess.file_exists(visual_state_path):
        return

    var modified := FileAccess.get_modified_time(visual_state_path)
    if modified == _last_modified:
        return
    _last_modified = modified

    var file := FileAccess.open(visual_state_path, FileAccess.READ)
    if file == null:
        status_label.text = "Visual-state file could not be opened"
        return

    var parsed = JSON.parse_string(file.get_as_text())
    if typeof(parsed) != TYPE_DICTIONARY:
        status_label.text = "Visual-state JSON is invalid"
        return

    _apply_state(parsed)

func _apply_state(state: Dictionary) -> void:
    var energy := float(state.get("energy", 0.0))
    var brightness := float(state.get("brightness", 0.0))
    var width := float(state.get("stereo_width", 0.0))
    var transition := float(state.get("transition_strength", 0.0))
    var compression := float(state.get("compression", 0.0))
    var coherence := float(state.get("coherence", 0.0))
    var motif := float(state.get("motif_activity", 0.0))
    var recurrence := float(state.get("recurrence", 0.0))
    var time_s := float(state.get("time_s", 0.0))

    if _material:
        _material.set_shader_parameter("drive_time", time_s)
        _material.set_shader_parameter("energy", energy)
        _material.set_shader_parameter("brightness", brightness)
        _material.set_shader_parameter("stereo_width", width)
        _material.set_shader_parameter("transition_strength", transition)
        _material.set_shader_parameter("compression", compression)
        _material.set_shader_parameter("coherence", coherence)
        _material.set_shader_parameter("motif_activity", motif)
        _material.set_shader_parameter("recurrence", recurrence)

    status_label.text = "Python visual state connected"
    metrics_label.text = "t %.2fs   energy %.2f   transition %.2f   motif %.2f   recurrence %.2f" % [time_s, energy, transition, motif, recurrence]
