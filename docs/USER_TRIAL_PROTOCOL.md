# Phonic Drive User Trial Protocol

## Purpose

This protocol turns subjective Phonic Drive observations into timestamped, provenance-preserving trial records that can be compared with measured acoustic structure without treating subjective reports as acoustic measurements or causal proof.

## Principle

Record the participant event first. Interpret it later.

A participant should not need to explain an event while listening. The primary action should be a low-friction timestamp marker.

## Event vocabulary

A starter vocabulary may include:

1. piloerection / hair-raising response
2. perceived motion
3. pressure / tension
4. release
5. emotional peak
6. perceived spatial change
7. other / free marker

The vocabulary is configurable. These labels describe participant reports, not inferred mechanisms.

## Minimum event record

```yaml
response_event:
  time_s: 142.381
  response_type: piloerection
  intensity: 0.7
  body_region: forearm_left
  confidence: 0.9
  note: null
```

Only `time_s` and `response_type` are required in the first implementation. Additional fields may be collected after playback so event capture itself stays fast.

## Trial record

```yaml
phonic_drive_trial:
  trial_id: PDT-000184
  session_id: PDS-000031

  stimulus:
    stimulus_id: TRACK-091
    transform_id: original

  randomization:
    index: 3
    blinded_label: X

  analysis:
    analyzer_version: 0.3.0-dev
    schema_version: "1.0"

  responses:
    - time_s: 142.381
      response_type: piloerection
      intensity: 0.7
```

## Analysis windows

For every event at `t_e`, the analysis layer should be able to extract acoustic and motif context at multiple scales:

```text
250 ms
500 ms
1 s
2 s
5 s
10 s
```

The default broad context can be represented as:

```text
[t_e - 10 s, t_e + 3 s]
```

The post-event portion is retained because participant marking can have motor/reaction delay.

## Lag analysis

Do not require an acoustic candidate to occur at exactly the response timestamp.

Test associations over a defined lag range:

```text
A(t - tau) <-> P(t)
M(t - tau) <-> P(t)
A(t - tau) <-> K(t)
M(t - tau) <-> K(t)
```

The tested lag range and step size must be recorded in the analysis output.

## Trial progression

### Stage 1 — observational

Listen normally and capture event markers. Use these sessions to discover candidate motifs and estimate useful latency windows.

### Stage 2 — repeatability

Repeat the same stimulus on different sessions. Compare whether candidate events recur and how timing/intensity varies.

### Stage 3 — cross-stimulus

Compare structurally similar motifs across unrelated tracks or stimuli.

### Stage 4 — controlled perturbation

Create variants where one structural property changes while obvious confounds are held as constant as practical.

Examples:

- timing preserved vs timing scrambled
- band trajectory preserved vs inverted
- spectral structure retained with altered timbre
- original vs RMS-matched control

### Stage 5 — reconstruction

Synthesize a minimal stimulus containing a candidate temporal/spectral motif without the original composition, where technically and legally appropriate.

## A/B/X trial structure

A future blinded trial can use:

```text
A = candidate structure preserved
B = candidate structure altered
X = control
```

The participant-facing interface should show neutral identifiers rather than reveal the hypothesis.

Randomization order must be saved in T (trial conditions), not inferred afterward.

## Evidence outputs

The interpreter should report evidence at distinguishable levels:

- observation
- temporal proximity
- within-session recurrence
- cross-session recurrence
- cross-stimulus recurrence
- perturbation sensitivity
- reconstruction response

It should also report negative results and contradictory events. Absence of an expected response is data.

## Safety and scope

Phonic Drive trials are exploratory research tooling, not diagnosis or treatment. The system should avoid unsafe playback levels and should record playback conditions when possible. Any future physiological sensing should remain a separately identified measurement stream with its own device limitations and consent requirements.
