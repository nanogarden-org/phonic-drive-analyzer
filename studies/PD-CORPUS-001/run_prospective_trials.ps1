param(
    [Parameter(Mandatory=$true)]
    [string]$CorpusRoot,

    [string]$OutputRoot = ".\runs\PD-CORPUS-001\prospective",

    [string]$Participant = "P001"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command phonic-drive-trial -ErrorAction SilentlyContinue)) {
    throw "phonic-drive-trial is not installed/on PATH. Install the current v3 branch first."
}
if (-not (Get-Command ffplay -ErrorAction SilentlyContinue)) {
    throw "ffplay is not on PATH. Install FFmpeg or use the trial runner with an externally synchronized player."
}

$CorpusRoot = (Resolve-Path $CorpusRoot).Path
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$OutputRoot = (Resolve-Path $OutputRoot).Path

$trials = @(
    @{
        Sequence = "04"
        TrialId = "PD-CORPUS-001-T04"
        StimulusId = "PD-CORPUS-001-S04"
        Audio = "04 LED Spirals\Le Castle Vania - LED Spirals [Extended Full Length Version] from the movie John Wick (Official).mp3"
        Output = "04_LED_Spirals_response_events.json"
    },
    @{
        Sequence = "05"
        TrialId = "PD-CORPUS-001-T05"
        StimulusId = "PD-CORPUS-001-S05"
        Audio = "05 Retribution\Blue Stahli  - Retribution.mp3"
        Output = "05_Retribution_response_events.json"
    }
)

Write-Host "PD-CORPUS-001 prospective response capture"
Write-Host "Keys: 1 piloerection | 2 movement | 3 tension | 4 release | 5 emotional peak | 6 spatial change | 7 other"
Write-Host "Press q only if you need to end a trial early. Otherwise playback ends the trial automatically."
Write-Host "Do not inspect Phonic Drive motif/transition outputs for 04 or 05 before completing both trials."

foreach ($trial in $trials) {
    $audio = Join-Path $CorpusRoot $trial.Audio
    if (-not (Test-Path -LiteralPath $audio)) {
        throw "Missing stimulus: $audio"
    }
    $output = Join-Path $OutputRoot $trial.Output

    Write-Host ""
    Write-Host "Starting prospective trial $($trial.Sequence)."
    Write-Host "Use response keys when an event occurs; do not try to explain it during playback."
    Read-Host "Press Enter when ready"

    & phonic-drive-trial $audio `
        --output $output `
        --trial-id $trial.TrialId `
        --stimulus-id $trial.StimulusId `
        --participant $Participant

    if ($LASTEXITCODE -ne 0) {
        throw "Trial $($trial.Sequence) failed with exit code $LASTEXITCODE"
    }
    if (-not (Test-Path -LiteralPath $output)) {
        throw "Trial output was not created: $output"
    }
    Write-Host "Saved: $output"
}

Write-Host ""
Write-Host "Both prospective trials are complete."
Write-Host "Return the two *_response_events.json files for sealed alignment against the precomputed A(t)/M(t) results."
