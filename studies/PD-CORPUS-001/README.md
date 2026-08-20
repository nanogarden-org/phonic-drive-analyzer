# PD-CORPUS-001

First anchored Phonic Drive retrospective/prospective study corpus.

## Study split

| Sequence | Track folder | Role |
|---:|---|---|
| 01 | Clubbed to Death | retrospective_known |
| 02 | Paris - Else | retrospective_known |
| 03 | Right This Second | retrospective_known |
| 04 | LED Spirals | prospective_untested |
| 05 | Retribution | prospective_untested |

The repository stores **provenance only** in `manifest.json`: filenames, sizes,
SHA-256 hashes, study roles, and blinding policy. Audio and historical note
contents are not committed.

## Blinding rule

Before prospective response capture is complete:

1. Scan/hash all five folders without reading note contents.
2. Analyze audio for all five tracks and generate A(t) and M(t).
3. Do not feed the 01-03 historical notes into motif discovery or ranking.
4. Keep 04-05 marked prospective/untested.
5. Capture fresh P(t) for 04 and 05.
6. Only then unseal 01-03 for retrospective comparison.

This order prevents the historical descriptions from steering motif discovery
and preserves 04-05 as genuinely prospective observations.

## Reproduce the scan

```powershell
phonic-drive-study scan ".\PD-CORPUS-001" `
  --corpus-id PD-CORPUS-001 `
  --output ".\runs\PD-CORPUS-001\study_manifest.json"
```

## Run the blind acoustic/structural pass

```powershell
phonic-drive-study analyze ".\PD-CORPUS-001" `
  --corpus-id PD-CORPUS-001 `
  --output ".\runs\PD-CORPUS-001"
```

This invokes the retained v2 and native v3 paths against audio only and writes
`study_manifest.json`, `study_run.json`, v2/v3 artifacts, and migration
comparison reports.

## Human gate

When the blind analysis is complete, the next human contribution is fresh
response capture on 04 and 05 using `phonic-drive-trial`. Do not pre-annotate
those tracks before that trial.
