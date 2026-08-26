# Phonic Drive Desktop Component Map

Status: draft v0.1

This document maps the proposed desktop UI to the existing Phonic Drive v3 codebase and identifies the new application-layer components required to make the GUI the normal user interface.

## 1. Architectural intent

The desktop application should not duplicate analysis logic. It should orchestrate existing Phonic Drive services through stable Python APIs.

Target layering:

```text
Desktop UI
    ↓
Application controllers / state
    ↓
Domain services
    ↓
Existing Phonic Drive analysis/trial/reconstruction modules
    ↓
Artifacts + provenance
```

The CLI should call the same domain services where practical rather than owning unique business logic.

## 2. Proposed package additions

Suggested new package boundary:

```text
phonic_drive/
    desktop/
        __init__.py
        app.py
        state.py
        config.py
        theme.py
        diagnostics.py
        controllers/
            study_controller.py
            analysis_controller.py
            trial_controller.py
            compare_controller.py
            reconstruction_controller.py
        views/
            shell.py
            home_view.py
            study_view.py
            analyze_view.py
            trial_view.py
            compare_view.py
            reconstruct_view.py
            outputs_view.py
            settings_view.py
        widgets/
            context_bar.py
            transport.py
            response_pad.py
            artifact_browser.py
            timeline_lanes.py
            mesh_view.py
            status_panel.py
```

A root launcher may remain:

```text
PhonicDrive.pyw
```

until packaging produces a native executable.

## 3. UI framework recommendation

For the current alpha, prefer the Python standard-library `tkinter`/`ttk` stack or a similarly lightweight already-available desktop layer before adding a large framework dependency.

Reasons:

- Windows-first usability
- no browser/runtime dependency
- easy file/folder dialogs
- straightforward buttons/hotkeys
- can call existing Python APIs directly
- suitable for the first functional shell and trial UI

The advanced mesh visualization may later justify a dedicated GPU/web rendering surface, but that should not block the basic desktop application.

## 4. Application state

### New: `phonic_drive.desktop.state.AppState`

Responsibilities:

- active study
- active track
- participant pseudonym
- active mode
- current analysis result references
- current trial state
- current output root
- recent studies
- selected visualization mode

This is in-memory UI/application state, distinct from persisted configuration.

Suggested fields:

```python
@dataclass
class AppState:
    study_root: Path | None
    study_manifest: dict | None
    active_track_sequence: int | None
    participant: str
    output_root: Path
    mode: str
    current_analysis_dir: Path | None
    current_trial_output: Path | None
```

## 5. Configuration service

### New or existing central config layer

Responsibilities:

- load/save `%LOCALAPPDATA%/PhonicDrive/config.json`
- environment-variable overrides
- remember last study/output root
- remember participant ID
- remember window geometry and visualization preference

Suggested API:

```python
load_config() -> DesktopConfig
save_config(config: DesktopConfig) -> Path
resolve_study_root(config) -> Path | None
resolve_output_root(config) -> Path
```

The UI should never assemble absolute paths by string concatenation when a resolved path object is available.

## 6. Shell / navigation

### `views.shell.DesktopShell`

Owns:

- root window
- navigation rail
- context bar
- central view host
- bottom transport region
- mode switching

It should not perform analysis itself.

### `widgets.context_bar.ContextBar`

Reads `AppState` and shows:

- study
- active track
- participant
- output alias
- current mode

### `widgets.transport.TransportBar`

Provides shared playback controls outside restricted trial modes.

## 7. Study workflow mapping

### UI: `views.study_view.StudyView`

Uses:

- `phonic_drive.study.scan_study`
- study manifest read/write functions
- central config service

### Controller: `controllers.study_controller.StudyController`

Responsibilities:

- choose/import study folder
- validate numbered folders
- populate study table
- preserve retrospective/prospective study role
- update active track
- enforce note sealing policy

Do not allow the view to directly open historical note content before the controller says the study is unsealed.

## 8. Analysis workflow mapping

### Existing analysis services

Use:

- `phonic_drive.track.analyze_track`
- `phonic_drive.exports.write_v3_bundle`
- `phonic_drive.validation.*` when corpus validation is requested

### New: `controllers.analysis_controller.AnalysisController`

Responsibilities:

- receive selected source track
- run analysis off the UI thread
- emit progress/status events
- write v3 bundle
- update `AppState.current_analysis_dir`
- surface errors in human-readable form

The controller should call Python functions directly, not spawn `phonic-drive-v3` as a subprocess.

### Threading

Long analysis must not freeze the UI.

Use a worker thread/process abstraction with UI-safe callbacks:

```text
UI click
  ↓
AnalysisController.start()
  ↓
worker thread
  ↓
analyze_track()
  ↓
write_v3_bundle()
  ↓
UI completion callback
```

## 9. Trial workflow mapping

### Existing trial model

Reuse:

- `phonic_drive.trials.events.ResponseEvent`
- response schema fields
- monotonic timing semantics

### Refactor target

`phonic_drive.trials.runner.run_trial` currently combines playback, console keyboard capture, and persistence. The desktop application should split those responsibilities.

Proposed services:

```text
TrialSession
PlaybackService
ResponseRecorder
TrialPersistence
```

### New: `controllers.trial_controller.TrialController`

Responsibilities:

- prepare trial identity
- start playback
- start monotonic clock
- expose `mark_response(response_type)`
- update event count
- detect playback completion
- auto-save response events
- end/cancel trial
- journal temporary events during capture

Suggested API:

```python
controller.start_trial(track, trial_id, stimulus_id, participant)
controller.mark_response("piloerection")
controller.pause()
controller.resume()
controller.end_trial()
```

### UI: `widgets.response_pad.ResponsePad`

Seven large buttons:

- piloerection
- perceived movement
- pressure/tension
- release
- emotional peak
- spatial change
- other

Optional keyboard shortcuts remain mapped to the same controller method.

### Playback abstraction

Current FFplay integration can remain the first backend.

Create:

`phonic_drive.playback.FFplayPlaybackService`

Responsibilities:

- discover ffplay
- start process
- expose running/completed state
- stop/pause when supported
- report playback errors

This prevents FFplay process details from leaking into views.

## 10. Compare workflow mapping

### Existing services

Use:

- `phonic_drive.trials.events.nearest_motifs`
- `phonic_drive.interpreter.alignment`
- `phonic_drive.interpreter.aggregate`
- `phonic_drive.visualization.timeline`

### New: `controllers.compare_controller.CompareController`

Responsibilities:

- load A(t), M(t), P(t), K(t)
- resolve time alignment
- expose event-centric inspection records
- calculate descriptive proximity
- invoke circular-shift/null control analysis when requested
- return presentation-safe result models

Suggested presentation model:

```python
@dataclass
class EventInspection:
    event_time_s: float
    response_type: str
    nearest_motif: dict | None
    nearest_transition: dict | None
    motif_lag_s: float | None
    transition_lag_s: float | None
    evidence_label: str
```

## 11. Shared timeline widget

### `widgets.timeline_lanes.SharedTimeline`

Consumes normalized presentation models rather than raw files.

Four semantic lanes:

- A(t)
- M(t)
- P(t)
- K(t)

Requirements:

- shared x-axis
- independent y semantics
- selectable event markers
- zoom/pan later
- never imply one combined scalar state

The existing matplotlib implementation can back the first version before a richer interactive canvas is introduced.

## 12. Mesh visualization component

### `widgets.mesh_view.MeshView`

This is a separate visualization surface, not the analytical source of truth.

Input should be a derived visualization model such as:

```python
@dataclass
class MeshFrame:
    time_s: float
    band_state: np.ndarray
    relationship_matrix: np.ndarray | None
    transition_strength: float
    stereo_width: float
```

Potential visual mappings:

- longitudinal mesh axis → time/history window
- mesh radius → normalized band-energy distribution
- twist → cross-band relationship orientation
- local constriction → selected structural concentration metric
- line brightness → transition intensity

All mappings must be documented as visualization choices rather than scientific claims.

First implementation may be deferred while the shell/trial UI becomes functional.

## 13. Reconstruction workflow mapping

### Existing services

Use:

- `phonic_drive.reconstruction.recipes`
- `phonic_drive.reconstruction.protocol`
- `phonic_drive.reconstruction.render`
- `phonic_drive.reconstruction.transforms`

### New: `controllers.reconstruction_controller.ReconstructionController`

Responsibilities:

- list recipes
- validate parameters
- show preserves/disrupts contract
- build ReconstructionManifest
- render transformed stimulus
- link result to hypothesis/trial IDs
- prepare randomized trial conditions

The view should never implement DSP directly.

## 14. Outputs browser

### New: `widgets.artifact_browser.ArtifactBrowser`

Responsibilities:

- group artifacts by semantic role
- preview JSON summaries
- preview CSV tables
- open containing folder
- copy path
- export package

It should derive artifact locations from manifests and `AppState`, not from user-entered paths.

## 15. Diagnostics component

### New: `desktop.diagnostics`

Checks:

- Python version
- package version
- ffmpeg
- ffprobe
- ffplay
- config path
- output root writable
- active study source files present

Returns structured diagnostics:

```python
@dataclass
class DiagnosticItem:
    name: str
    status: str
    detail: str
    fix_hint: str | None
```

The Settings screen renders these without exposing stack traces unless Advanced Details is opened.

## 16. Error boundary

Create a desktop-level exception translator.

Example:

```python
translate_exception(exc) -> UserFacingError
```

Mapping examples:

- `FileNotFoundError` → selected source missing / relink
- ffplay absent → playback component missing
- output permission error → choose writable output folder
- malformed study → show exact folder violating convention

Stack traces should be logged for debugging but not be the default UI experience.

## 17. Provenance and artifact ownership

The desktop layer must preserve existing provenance rules.

Every user-visible operation should know:

- source stimulus
- study ID
- track sequence
- participant pseudonym when relevant
- schema version
- analysis/trial/reconstruction IDs
- output location

The UI should not rename or rewrite scientific artifacts simply for presentation.

## 18. Suggested event bus / callback model

A lightweight internal event model can decouple controllers from views.

Events might include:

```text
study_loaded
track_selected
analysis_started
analysis_progress
analysis_completed
trial_started
response_recorded
trial_completed
output_created
error_raised
```

The first implementation can use direct callbacks rather than introducing a framework-heavy event bus.

## 19. Implementation phases

### Phase A — desktop shell

Add:

- `desktop/app.py`
- `desktop/state.py`
- persistent config
- navigation
- Study screen
- Outputs screen
- Diagnostics

### Phase B — native trial UI

Refactor trial logic into reusable services and add:

- TrialController
- ResponsePad
- playback lifecycle
- automatic save
- temporary journal

This is the highest-priority usability phase because it removes the worst current CLI friction.

### Phase C — analysis UI

Add:

- AnalysisController
- worker execution
- progress/status
- native v3 artifact summary

### Phase D — compare UI

Add:

- CompareController
- SharedTimeline
- event inspector
- circular-shift result presentation

### Phase E — mesh visualization

Add:

- MeshFrame presentation model
- MeshView renderer
- visualization-mode switching
- optional motif/transition overlays outside prospective trials

### Phase F — reconstruction UI

Add:

- ReconstructionController
- recipe builder
- randomized condition builder
- reconstruction-to-trial handoff

## 20. CLI consolidation

As desktop controllers mature, existing CLI commands should increasingly become thin adapters over the same service functions.

Desired relationship:

```text
                  ┌─ Desktop UI
Domain services ──┤
                  └─ CLI adapters
```

Avoid:

```text
Desktop UI → shell command → CLI parser → domain logic
```

The desktop application should not need to quote paths or parse command-line text to use Phonic Drive internally.

## 21. Definition of done for desktop v0.1

Desktop v0.1 is usable when a Windows user can:

- launch without a console window
- select a study folder using a dialog
- see ordered study tracks
- select one track
- run native v3 analysis
- see completion and output summary
- start a prospective trial
- click response buttons during playback
- have playback end the trial automatically
- save response JSON automatically
- reopen the output from the app
- restart the application and resume the last study

Advanced mesh rendering and reconstruction are not required for v0.1 acceptance, but the architecture must leave explicit component boundaries for both.
