#!/usr/bin/env pwsh
# status.ps1 — formatted summary of the current SAM project state.
# Reads plans/state.json (always current — routing source of truth) and
# plans/config.json (compared against schema defaults to surface non-default
# values). Does NOT read plans/STATUS.md: STATUS is human prose, and under
# the default `status_updates=pm_only` it intentionally lags by one phase.

$ErrorActionPreference = 'Stop'

$statePath  = Join-Path $PSScriptRoot 'state.json'
$configPath = Join-Path $PSScriptRoot 'config.json'
$schemaPath = Join-Path $PSScriptRoot 'config.schema.json'

if (-not (Test-Path $statePath)) {
    Write-Error "state.json not found at $statePath"
    exit 1
}

$state = Get-Content $statePath -Raw | ConvertFrom-Json

# Position: B1[-M2[-P3[-S2]]]
$segments = @($state.build_id, $state.milestone_id)
if ($state.phase_id) { $segments += $state.phase_id }
if ($state.step_id)  { $segments += $state.step_id  }
$position = ($segments -join '-')

Write-Output ("Position:  {0}     pause: {1}" -f $position, $state.pause_type)

# Last action
$last = $state.last_action
Write-Output ("Last:      {0} -> {1}" -f $last.action_id, $last.result)
foreach ($line in ($last.summary -split "`n")) {
    Write-Output ("           `"{0}`"" -f $line)
}

Write-Output ""
Write-Output ("Next:      {0}" -f $state.next_action_id)

# Blockers
Write-Output ""
if ($state.blockers -and $state.blockers.Count -gt 0) {
    Write-Output "Blockers:"
    foreach ($b in $state.blockers) {
        Write-Output ("  {0}: {1}" -f $b.id, $b.summary)
    }
} else {
    Write-Output "Blockers:  none"
}

# Git: branch + ahead/behind upstream + working-tree counts. Degrades gracefully
# when there's no upstream, the HEAD is detached, or the parent dir isn't a git repo.
$repoRoot = Split-Path $PSScriptRoot -Parent
$ErrorActionPreference = 'Continue'
$branch = & git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null
if ($LASTEXITCODE -eq 0 -and $branch) {
    Write-Output ""
    if ($branch -eq 'HEAD') {
        $sha = & git -C $repoRoot rev-parse --short HEAD 2>$null
        Write-Output ("Git:       detached at {0}" -f $sha)
    } else {
        $counts = & git -C $repoRoot rev-list --left-right --count "@{u}...HEAD" 2>$null
        if ($LASTEXITCODE -eq 0 -and $counts) {
            $parts  = $counts -split '\s+'
            $behind = [int]$parts[0]
            $ahead  = [int]$parts[1]
            Write-Output ("Git:       {0}  (ahead {1}, behind {2})" -f $branch, $ahead, $behind)
        } else {
            Write-Output ("Git:       {0}  (no upstream)" -f $branch)
        }
    }

    # Working-tree pulse: counts only (not filenames) to keep the one-screen contract.
    # Porcelain v1 XY codes: X = index (staged), Y = worktree (unstaged), "??" = untracked.
    $porcelain = & git -C $repoRoot status --porcelain 2>$null
    if ($LASTEXITCODE -eq 0) {
        $staged = 0; $unstaged = 0; $untracked = 0
        foreach ($line in $porcelain) {
            if (-not $line -or $line.Length -lt 2) { continue }
            $x = $line[0]; $y = $line[1]
            if ($x -eq '?' -and $y -eq '?') { $untracked++; continue }
            if ($x -ne ' ' -and $x -ne '?') { $staged++ }
            if ($y -ne ' ' -and $y -ne '?') { $unstaged++ }
        }
        Write-Output ("Tree:      {0} staged, {1} unstaged, {2} untracked" -f $staged, $unstaged, $untracked)
    }
}

# Config (non-default only) — diff against schema defaults. Reference material, so
# it sits at the bottom below the action surface (position / next / blockers / git).
if ((Test-Path $configPath) -and (Test-Path $schemaPath)) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
    $schema = Get-Content $schemaPath -Raw | ConvertFrom-Json

    $nonDefault = @()
    foreach ($prop in $schema.properties.PSObject.Properties) {
        $key = $prop.Name
        if ($key -eq '$schema' -or $key -eq 'workspace') { continue }
        $defaultValue = $prop.Value.default
        if ($null -eq $defaultValue) { continue }

        $configValue = $config.$key
        if ($null -ne $configValue -and $configValue -ne $defaultValue) {
            $nonDefault += [pscustomobject]@{
                Key     = $key
                Value   = $configValue
                Default = $defaultValue
            }
        }
    }

    Write-Output ""
    if ($nonDefault.Count -eq 0) {
        Write-Output "Config:    all defaults"
    } else {
        Write-Output "Config (non-default):"
        $keyWidth = ($nonDefault.Key | Measure-Object -Maximum -Property Length).Maximum
        $valWidth = ($nonDefault.Value | ForEach-Object { "$_".Length } | Measure-Object -Maximum).Maximum
        foreach ($n in $nonDefault) {
            $fmt = "  {0,-$keyWidth} = {1,-$valWidth}   (default: {2})"
            Write-Output ($fmt -f $n.Key, $n.Value, $n.Default)
        }
    }
}
