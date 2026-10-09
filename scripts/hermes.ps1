[CmdletBinding()]
param(
    [ValidateSet('Initialize','Login','Model','Telegram','Start','Stop','Status','Logs','Chat','Shell','Check','Test')]
    [string]$Action = 'Status'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    function Invoke-Compose {
        param([string[]]$ComposeArgs)
        & docker compose @ComposeArgs
        if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed (exit $LASTEXITCODE)." }
    }
    function Assert-GatewayStopped {
        $running = @(& docker compose ps --status running -q hermes)
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the gateway.' }
        if ($running.Count -gt 0 -and $running[0]) {
            throw 'Stop the gateway before opening a maintenance session: .\scripts\hermes.ps1 -Action Stop'
        }
    }
    if ($Action -in @('Initialize','Login','Model','Telegram','Chat','Shell')) {
        Assert-GatewayStopped
    }
    switch ($Action) {
        'Initialize' {
            Invoke-Compose -ComposeArgs @('config','--quiet')
            Invoke-Compose -ComposeArgs @('pull','hermes')
            Invoke-Compose -ComposeArgs @('run','--rm','-T','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','initialize')
        }
        'Login' {
            Invoke-Compose -ComposeArgs @('run','--rm','hermes','auth','add','openai-codex','--no-browser')
        }
        'Model' {
            Invoke-Compose -ComposeArgs @('run','--rm','hermes','model')
        }
        'Telegram' {
            Invoke-Compose -ComposeArgs @('run','--rm','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','telegram')
        }
        'Start' {
            $running = @(& docker compose ps --status running -q hermes)
            if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the gateway.' }
            if ($running.Count -gt 0 -and $running[0]) {
                Write-Host 'Gateway is already running.'
            } else {
                Invoke-Compose -ComposeArgs @('run','--rm','-T','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','check')
                Invoke-Compose -ComposeArgs @('up','-d','hermes')
            }
        }
        'Stop' { Invoke-Compose -ComposeArgs @('stop','hermes') }
        'Status' {
            Invoke-Compose -ComposeArgs @('ps','--all')
            $running = @(& docker compose ps --status running -q hermes)
            if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the gateway.' }
            if ($running.Count -gt 0 -and $running[0]) {
                Invoke-Compose -ComposeArgs @('exec','-T','--user','hermes','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','status')
            } else {
                Invoke-Compose -ComposeArgs @('run','--rm','-T','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','status')
            }
        }
        'Check' {
            Invoke-Compose -ComposeArgs @('config','--quiet')
            Assert-GatewayStopped
            Invoke-Compose -ComposeArgs @('run','--rm','-T','hermes','/opt/hermes/.venv/bin/python','/deployment/runtime.py','check')
        }
        'Test' {
            Assert-GatewayStopped
            Invoke-Compose -ComposeArgs @('config','--quiet')
            Invoke-Compose -ComposeArgs @('run','--rm','-T','hermes','/opt/hermes/.venv/bin/python','/deployment/smoke_test.py')
        }
        'Logs' { Invoke-Compose -ComposeArgs @('logs','--tail','100','-f','hermes') }
        'Chat' { Invoke-Compose -ComposeArgs @('run','--rm','hermes','chat') }
        'Shell' { Invoke-Compose -ComposeArgs @('run','--rm','hermes','bash') }
    }
} finally {
    Pop-Location
}