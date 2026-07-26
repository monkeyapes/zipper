$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputDir = Join-Path (Split-Path $projectDir) "build"

Write-Host "=== LocalName Control Center Builder ===" -ForegroundColor Cyan
Write-Host ""

Set-Location $projectDir

Write-Host "Restoring packages..." -ForegroundColor Yellow
dotnet restore

Write-Host "Publishing framework-dependent EXE..." -ForegroundColor Yellow
dotnet publish -c Release -r win-x64 --self-contained false -o $outputDir

if ($LASTEXITCODE -eq 0)
{
    Write-Host "" -ForegroundColor Green
    Write-Host "=== Build Complete ===" -ForegroundColor Cyan
    $exePath = Join-Path $outputDir "LocalName.exe"
    $size = (Get-Item $exePath).Length
    Write-Host "EXE: $exePath ($([math]::Round($size/1KB)) KB)" -ForegroundColor Green
    Write-Host "Note: Requires .NET 8 Runtime" -ForegroundColor Yellow
    Write-Host "      Install from: https://dotnet.microsoft.com/download/dotnet/8.0" -ForegroundColor Yellow
}
else
{
    Write-Host "Build failed!" -ForegroundColor Red
}

Set-Location $projectDir
