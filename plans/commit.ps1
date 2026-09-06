#!/usr/bin/env pwsh
# commit.ps1 — auto-commit with a SAM-formatted message.
# Reads plans/state.json and runs `git add -A; git commit -m "<message>"`.
#
# Message format:
#   --AUTO-{build_id}-{milestone_id}-{phase_id}-{Role.Task}: {last_action.summary}
# When phase_id is null (pre-phase actions like ProductVision), the phase
# segment is omitted: --AUTO-{build_id}-{milestone_id}-{Role.Task}: ...
#
# The --AUTO- prefix marks SAM automated commits so they remain
# distinguishable from organic commits authored during implementation.
# Action templates that produce organic commits (e.g.,
# Staff.ImplementationExecution) instruct the AI NOT to use the --AUTO-
# prefix in those manual messages.

$ErrorActionPreference = 'Stop'

$statePath = Join-Path $PSScriptRoot 'state.json'
if (-not (Test-Path $statePath)) {
    Write-Error "state.json not found at $statePath"
    exit 1
}

$state = Get-Content $statePath -Raw | ConvertFrom-Json

$last = $state.last_action
if (-not $last -or -not $last.action_id -or -not $last.summary) {
    Write-Error "state.json is missing last_action.action_id or last_action.summary; cannot build commit message."
    exit 1
}

$segments = @($state.build_id, $state.milestone_id)
if ($state.phase_id) { $segments += $state.phase_id }
$position = ($segments -join '-')

$message = "--AUTO-$position-$($last.action_id): $($last.summary)"

Write-Output "Commit message:"
Write-Output "  $message"
Write-Output ""

git add -A
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git commit -m $message
exit $LASTEXITCODE
