# PD-CORPUS-001 — Retrospective Unseal Summary

## Boundary

The historical files for sequences 01–03 were opened only after the prospective 04–05 response alignment had been frozen.

The old files are **not participant event logs**. They are structural `song_lens` notes containing approximate durations, frequency-layer descriptions, selected inflection points, repetition/resonance descriptions, and high-level cognitive-field descriptions. Therefore they cannot serve as retrospective physiological ground truth comparable to the timestamped `P(t)` captured for 04–05.

This comparison asks only whether current v3 structural analysis rediscovers selected historical **structural landmarks**.

## 01 — Clubbed to Death

Historical inflection landmarks:

- 42 s — introduction of percussion
- 88 s — full string swell / melodic expansion
- 145 s — crescendo / rhythmic density peak

Nearest current-v3 motif peaks:

| Historical | nearest motif | absolute difference |
|---:|---:|---:|
| 42 s | 28.91 s | 13.09 s |
| 88 s | 97.13 s | 9.13 s |
| 145 s | 138.53 s | 6.47 s |

The current global strongest-transition list does not recover these landmarks well. Its top-12 ranking is dominated by a highly active late-track region around 355–378 s plus the ending.

**Result:** weak correspondence under the current global ranking. This is evidence that a fixed top-N global transition list is not an adequate representation of distributed landmarks in a long-form track.

## 02 — Paris

Historical inflection landmarks:

- 0 s — establish main piano theme
- 90 s — introduction of atmospheric textures
- 165 s — climactic melodic motif

Current-v3 correspondence:

| Historical | nearest major transition | difference | nearest motif | difference |
|---:|---:|---:|---:|---:|
| 0 s | 37.38 s | 37.38 s | 1.86 s | 1.86 s |
| 90 s | 89.88 s | 0.12 s | 88.33 s | 1.67 s |
| 165 s | 165.60 s | 0.60 s | 165.51 s | 0.51 s |

**Result:** strong structural correspondence for the two non-boundary historical landmarks. The opening is represented much better by a motif candidate than by the strongest-transition detector, which is expected because track start is a boundary rather than an interior peak.

## 03 — Right This Second

Historical landmarks:

- 0 s — establishes deep bass synths
- 90 s — minimalist melodic elements introduced
- 180 s — sparse percussion begins to emerge
- 300 s — melodic elements evolve
- 470 s — track conclusion

Current-v3 correspondence:

| Historical | nearest major transition | difference | nearest motif | difference |
|---:|---:|---:|---:|---:|
| 0 s | 5.09 s | 5.09 s | 5.67 s | 5.67 s |
| 90 s | 163.07 s | 73.07 s | 26.77 s | 63.23 s |
| 180 s | 163.07 s | 16.93 s | 178.05 s | 1.95 s |
| 300 s | 163.07 s | 136.93 s | 178.05 s | 121.95 s |
| 470 s | 468.74 s | 1.26 s | 454.58 s | 15.42 s |

The top-12 transition set is again dominated by one late-track region (roughly 442–474 s), demonstrating the same global-ranking bias seen in sequence 01.

**Result:** partial correspondence. The ~180 s landmark is recovered well by a motif candidate and the ending by a major transition; the 90 s and 300 s historical claims are not supported by the current top-candidate representation.

## Engineering conclusion

The retrospective unseal does **not** support treating historical notes as ground truth. It does support three engineering conclusions:

1. Motif candidates and major transitions capture different classes of structural landmark; neither should substitute for the other.
2. A fixed global top-N transition ranking can be monopolized by a locally intense region in a long track.
3. The transition layer needs a distributed/local-landmark representation in addition to the existing global-strength ranking.

A next detector revision should retain the existing global strongest-transition list for compatibility while adding time-distributed candidates (for example, segment-balanced or multi-scale local maxima). This change should be evaluated against the historical anchor set without tuning directly to individual timestamps.

## Epistemic status

- 01–03 historical files: retrospective structural annotations, not response ground truth.
- 04–05 response files: prospective timestamped participant observations.
- Current prospective findings: temporal/structural association only.
- Causal/physiological evidence remains unestablished until perturbation/reconstruction trials are performed.
