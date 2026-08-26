# Phonic Drive Desktop UI/UX Specification

Status: draft v0.1

## 1. Purpose

Phonic Drive Desktop is the normal human-facing interface for Phonic Drive v3. The command-line tools remain available for automation, debugging, CI, batch execution, and reproducibility, but they are not the primary interaction model.

The desktop application exists to remove user responsibility for shell syntax, absolute paths, artifact discovery, manual JSON handling, and output-folder bookkeeping while preserving the existing provenance and experimental boundaries of the Phonic Drive architecture.

The interface should feel like a structure-first music visualization environment with a research spine underneath it.

## 2. Product principles

### 2.1 Human state belongs in the application

The application must remember or visibly expose the active study, active track, participant pseudonym, output root, current analysis state, and current trial state. Users should not need to remember where files were generated or reconstruct context from filenames.

### 2.2 Structure first

The primary visual metaphor is an evolving structural field rather than a generic equalizer. Meshes, ribbons, contour bodies, recurrence maps, and trajectory views should represent descriptive acoustic structure without implying physiological causation.

### 2.3 Scientific boundaries remain visible

The UI must preserve the distinction among:

- A(t): measured acoustic state
- M(t): descriptive motif/relationship structure
- P(t): participant-reported response events
- K(t): observable behavioral/workflow telemetry
- T: trial conditions and randomization
- R: reconstruction/perturbation transforms

The UI may align these streams in time but must not collapse them into one inferred latent variable by default.

### 2.4 No hidden interpretation during prospective trials

Prospective trial mode must not reveal motif timestamps, transition peaks, or prior structural interpretations that could prime the participant before response capture.

### 2.5 The CLI is substrate, not interface

All normal user tasks must be available without requiring PowerShell, shell quoting, path typing, environment-variable editing, or manual JSON creation.

## 3. Top-level navigation

The desktop shell contains the following primary modes:

1. Home
2. Study
3. Analyze
4. Trial
5. Compare
6. Reconstruct
7. Outputs
8. Settings

The first release may implement Home, Study, Analyze, Trial, Outputs, and Settings before Compare and Reconstruct reach full functionality.

## 4. Application shell

### 4.1 Persistent left navigation

A compact navigation rail contains icons and labels for each major mode. Labels may collapse in narrow layouts but must remain available through hover/tooltips.

### 4.2 Persistent context bar

The context bar must always expose:

- active study ID/name
- active track
- study role when applicable
- participant pseudonym
- current mode
- current output destination as a human-readable alias or folder name

It should include context-sensitive primary actions such as Analyze, Start Trial, Compare, or Open Output.

### 4.3 Persistent transport strip

When audio is loaded, a bottom transport strip should display:

- play/pause
- track title
- elapsed / total time
- scrubber
- volume
- optional loop control
- current mode/status badge

In Trial mode the transport should avoid exposing structural annotations that could prime the participant.

## 5. Home screen

The Home screen is a resume surface, not a dashboard dump.

It should show:

- Resume last study
- Recent studies
- Recent tracks
- Incomplete trials
- Last analysis status
- Quick actions: Open Study, Analyze Track, Run Trial

The user should be able to return to the previous working context with one click.

## 6. Study screen

### 6.1 Study list

A study contains ordered tracks and explicit study roles.

Example:

- 01 Clubbed to Death — retrospective_known
- 02 Paris — retrospective_known
- 03 Right This Second — retrospective_known
- 04 LED Spirals — prospective_untested
- 05 Retribution — prospective_untested

Each row should show concise state indicators such as:

- source present
- analyzed
- trial captured
- retrospective notes sealed/unsealed
- compare-ready

### 6.2 Study actions

Required actions:

- Create Study
- Import Study Folder
- Resume Study
- Open Study Folder
- Analyze Selected Track
- Analyze Study
- Start Prospective Trial

### 6.3 Blinding behavior

For prospective_untested tracks, the Study screen must not reveal motif or transition details before the response trial is complete.

For retrospective_known tracks, note contents may remain sealed until the prospective analysis phase is frozen.

## 7. Analyze screen

### 7.1 Primary purpose

Analyze mode runs native v3 analysis and presents completion state without requiring knowledge of the seven underlying artifacts.

### 7.2 Controls

- Choose track
- Analyze Track
- Analyze Study
- Cancel
- Re-run with parameters
- Open Analysis Outputs

### 7.3 Status surface

Display a compact progress model:

- Decode
- A(t) extraction
- M(t) extraction
- transition detection
- motif detection
- recurrence analysis
- artifact save

### 7.4 Analysis summary

After completion, display:

- duration
- frame count
- transition candidate count
- motif candidate count
- recurrence count
- schema/version
- output location alias

Do not require users to inspect raw JSON to confirm success.

## 8. Visualization workspace

### 8.1 Primary visualization modes

The center-stage visualization supports switchable modes:

- Mesh
- Ribbon
- Waveform
- Timeline
- Recurrence

Mesh is the preferred default when implemented.

### 8.2 Mesh design intent

The mesh should make time-varying acoustic structure intuitively visible through deformation rather than merely reacting to loudness.

Candidate visual inputs include:

- band-energy distribution
- cross-band relationship structure
- transition intensity
- motif-window activity
- stereo-space dimension

The mesh is a visualization of descriptive acoustic structure, not a rendering of physiology.

### 8.3 Overlay controls

Outside prospective Trial mode, optional overlays may include:

- transitions
- motif windows
- recurrence markers
- response markers
- section boundaries
- reconstruction condition

## 9. Trial screen

### 9.1 Primary purpose

Trial mode captures P(t) while audio plays, without requiring command-line entry or manual JSON authoring.

### 9.2 Trial layout

The screen contains:

- track identity
- trial identity
- recording status
- optional neutral visualization or intentionally reduced display
- large response buttons
- event counter
- playback status
- Pause / Resume / End Trial controls

### 9.3 Response buttons

Required response types:

- Piloerection
- Perceived Movement
- Pressure / Tension
- Release
- Emotional Peak
- Spatial Change
- Other

Buttons must be large enough for immediate use while listening.

Keyboard shortcuts 1–7 may remain enabled for expert use but are supplemental.

### 9.4 Trial behavior

When playback begins:

- start a monotonic session clock
- begin accepting response events immediately
- save each event in memory and optionally journal incrementally
- update event count without revealing structural analysis

When playback ends:

- end the trial automatically
- save response_events.json
- show success status
- provide Open Output and Continue buttons

No extra key press should be required to finish the trial.

### 9.5 Safety against data loss

A trial should journal events to a temporary session file during capture so an application crash does not discard the full session.

## 10. Compare screen

### 10.1 Shared-time lanes

Compare mode aligns but visually separates:

- A(t)
- M(t)
- P(t)
- K(t)

The common horizontal axis is time.

### 10.2 Event inspector

Selecting a participant event should show:

- response type
- event timestamp
- nearest motif(s)
- nearest transition(s)
- lag(s)
- current evidence level
- whether the statistic is descriptive or control-tested

### 10.3 Statistical controls

Where implemented, the UI should surface circular-shift/null-control results without implying statistical significance is causation.

Example labels:

- descriptive proximity
- exploratory association
- perturbation-supported
- reconstruction-supported

## 11. Reconstruct screen

Reconstruct mode is the controlled perturbation workspace.

It should support named recipes such as:

- time reverse
- timing scramble
- band ablation
- envelope-preserved control
- phase/timing control

Each recipe must display what it intends to preserve and disrupt.

The UI should generate a ReconstructionManifest automatically.

Later versions may allow randomized A/B/X trial creation directly from selected structural regions.

## 12. Outputs screen

### 12.1 Purpose

Users should never need to guess where generated artifacts were written.

### 12.2 Artifact presentation

Group artifacts by human task rather than filename alone:

Measured acoustics:
- acoustic_summary.json
- acoustic_timeline.csv
- transitions.json

Structural analysis:
- structural_analysis.json
- structural_timeline.csv
- motifs.json
- relationships.npz

Trials:
- response_events.json
- behavior_events.json
- trial manifest

Study/provenance:
- session manifest
- study manifest
- comparison summaries
- reconstruction manifests

### 12.3 Actions

- Preview
- Open File
- Open Folder
- Copy Path
- Export Package

JSON previews should be rendered as readable structured summaries, not raw text by default.

## 13. Settings and remembered state

### 13.1 Persisted configuration

Use one central config layer stored under the platform-appropriate user-data directory, for example:

`%LOCALAPPDATA%\PhonicDrive\config.json`

Configuration may include:

- last study root
- default study root
- output root
- participant pseudonym
- audio backend
- ffmpeg/ffplay discovery state
- default visualization mode
- window geometry
- recent studies
- keyboard shortcuts

### 13.2 Environment-variable overrides

Automation may override configuration with variables such as:

- PHONIC_DRIVE_STUDY_ROOT
- PHONIC_DRIVE_OUTPUT_ROOT
- PHONIC_DRIVE_PARTICIPANT
- PHONIC_DRIVE_DATA_ROOT

Environment variables are an automation surface, not a requirement for normal desktop use.

## 14. Error handling

Errors should be actionable and expressed in user language.

Bad:

`FileNotFoundError: C:\...`

Preferred:

`The selected track could not be found. Choose the source file again or relink the study folder.`

For dependency problems, Settings should include a Diagnostics panel showing:

- Python/package version
- FFmpeg detected
- ffprobe detected
- ffplay detected
- writable output directory
- config location

## 15. Visual style

Direction:

- dark neutral background
- luminous wireframe/mesh center stage
- restrained accent color
- high-contrast controls
- minimal chrome
- wide bottom transport
- clear mode/state badges

Avoid turning the application into either a generic media player or a wall of scientific plots.

## 16. Accessibility and ergonomics

- response buttons must be large and keyboard accessible
- all color-coded information needs a non-color cue
- text and labels remain readable under Windows scaling
- Trial mode should support full-screen or distraction-reduced presentation
- the application should remember window position/size

## 17. Desktop launch model

Normal launch target:

- double-clickable Windows launcher or packaged executable
- no visible console window

Development launch target may remain a `.pyw`/Python entry point while packaging matures.

## 18. Release slices

### Slice A — usable shell

- desktop window
- navigation
- config persistence
- file/folder pickers
- Study view
- Outputs view

### Slice B — trial UI

- playback
- response buttons
- automatic JSON save
- incremental event journal
- automatic playback completion

### Slice C — analysis UI

- invoke native v3 analysis
- progress/status
- artifact summaries

### Slice D — compare UI

- A/M/P/K shared-time lanes
- event inspector
- proximity/control summaries

### Slice E — structural visualization

- mesh
- ribbon
- recurrence overlays

### Slice F — reconstruction UI

- recipe builder
- randomized conditions
- perturbation/reconstruction trial workflow

## 19. Acceptance criteria for replacing CLI as the front door

A normal user must be able to complete the following without opening a terminal:

1. launch Phonic Drive
2. open or create a study
3. select a track
4. analyze the track
5. see analysis completion
6. run a prospective response trial
7. save the response record automatically
8. inspect where the output went
9. compare response events against analysis after the trial
10. resume the same study after restarting the application

When all ten are possible, the CLI can be considered an expert/automation interface rather than the default workflow.
