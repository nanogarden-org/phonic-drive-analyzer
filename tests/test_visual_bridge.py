import json

from phonic_drive.visual_bridge import VisualState, visual_state_from_frame, write_visual_state


def test_visual_state_clips_presentation_values():
    state = visual_state_from_frame(
        time_s=12.5,
        energy=1.7,
        brightness=-0.2,
        stereo_width=0.4,
        transition_strength=0.8,
        motif_activity=0.6,
        response_type="piloerection",
    )
    assert state.energy == 1.0
    assert state.brightness == 0.0
    assert state.response_active is True
    assert state.response_type == "piloerection"
    assert state.schema == "phonic-drive-visual-state-v1"


def test_visual_state_atomic_json_write(tmp_path):
    path = tmp_path / "visual_state.json"
    state = VisualState(time_s=3.25, energy=0.5, coherence=0.7)
    write_visual_state(path, state)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "phonic-drive-visual-state-v1"
    assert payload["time_s"] == 3.25
    assert payload["energy"] == 0.5
    assert payload["coherence"] == 0.7
