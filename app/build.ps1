$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputDir = Join-Path (Split-Path $projectDir) "build"

Write-Host "=== LocalName Control Center Builder ===" -ForegroundColor Cyan
Write-Host ""

# Restore and publish
Set-Location $projectDir

Write-Host "Restoring packages..." -ForegroundColor Yellow
dotnet restore

Write-Host "Building EXE..." -ForegroundColor Yellow
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o $outputDir

if ($LASTEXITCODE -eq 0) {
    $exePath = Join-Path $outputDir "LocalName.exe"
    Write-Host "" -ForegroundColor Green
    Write-Host "=== Build Complete ===" -ForegroundColor Cyan
    Write-Host "EXE: $exePath" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}

Set-Location $projectDir
