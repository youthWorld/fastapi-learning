param(
    [string]$ProjectName,
    [string]$FileName = "main.py"
)

if (-not $ProjectName) {
    Write-Host "Usage: .\start.ps1 <dir-name> [filename]" -ForegroundColor Yellow
    Write-Host "Example: .\start.ps1 second" -ForegroundColor Yellow
    Write-Host "Example: .\start.ps1 second main1.py" -ForegroundColor Yellow
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = Join-Path $ScriptDir $ProjectName

if (-not (Test-Path $TargetDir)) {
    Write-Host "Error: Directory '$TargetDir' not found" -ForegroundColor Red
    exit 1
}

$TargetFile = Join-Path $TargetDir $FileName
if (-not (Test-Path $TargetFile)) {
    Write-Host "Error: File '$FileName' not found in $TargetDir" -ForegroundColor Red
    Write-Host "Available Python files in this directory:" -ForegroundColor Yellow
    Get-ChildItem -Path $TargetDir -Filter "*.py" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    exit 1
}

$ModuleName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)

Write-Host ""
Write-Host "========================================"
Write-Host "  Starting: $ProjectName\$FileName"
Write-Host "  Module: $ModuleName"
Write-Host "  URL: http://127.0.0.1:8000"
Write-Host "  Docs: http://127.0.0.1:8000/docs"
Write-Host "========================================"
Write-Host ""

Push-Location $TargetDir

try {
    & uvicorn "${ModuleName}:app" --reload
}
finally {
    Pop-Location
    
    Write-Host ""
    Write-Host "Cleaning port 8000..." -ForegroundColor Yellow
    
    $listening = netstat -ano | Select-String ":8000.*LISTENING"
    $established = netstat -ano | Select-String ":8000.*ESTABLISHED"
    $connections = $listening + $established | Select-Object -Unique
    
    foreach ($conn in $connections) {
        $pidMatch = [regex]::Match($conn, '\s+(\d+)$')
        if ($pidMatch.Success) {
            $pid = $pidMatch.Groups[1].Value
            Write-Host "Killing process PID=$pid"
            taskkill /PID $pid /F 2>$null
        }
    }
    
    Write-Host "Cleanup done." -ForegroundColor Green
}