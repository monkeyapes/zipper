$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = $scriptPath
$rootDir = Split-Path -Parent $appDir
$outputDir = Join-Path $rootDir "build"

Write-Host "=== LocalName App Builder ===" -ForegroundColor Cyan
Write-Host ""

$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

$distDir = Join-Path $appDir "dist"
$buildDir = Join-Path $appDir "build"
if (Test-Path $distDir) { Remove-Item -Recurse -Force $distDir }
if (Test-Path $buildDir) { Remove-Item -Recurse -Force $buildDir }

Write-Host "Building addon .mcaddon..." -ForegroundColor Yellow
$addonScript = Join-Path $rootDir "addon\build_addon.py"
if (Test-Path $addonScript) {
    python $addonScript
}

Write-Host "Building main EXE..." -ForegroundColor Yellow
$iconPath = Join-Path $appDir "icon.ico"
$iconArg = ""
if (Test-Path $iconPath) { $iconArg = "--icon=`"$iconPath`"" }
$mainScript = Join-Path $appDir "main.py"
$cmd = "pyinstaller --onefile --windowed --name LocalName --add-data `"$rootDir\addon;addon`" --add-data `"$rootDir\settings.json;.`" --distpath `"$outputDir`" --workpath `"$appDir\build`" --specpath `"$appDir`" $iconArg `"$mainScript`""
Write-Host "Running: $cmd" -ForegroundColor Gray
Invoke-Expression $cmd

if (Test-Path $distDir) { Remove-Item -Recurse -Force $distDir }
if (Test-Path $buildDir) { Remove-Item -Recurse -Force $buildDir }
$specFile = Join-Path $appDir "main.spec"
if (Test-Path $specFile) { Remove-Item -Force $specFile }

Write-Host ""
Write-Host "Building watchdog EXE (hidden/no console)..." -ForegroundColor Yellow
$watchdogScript = Join-Path $appDir "watchdog.py"
$watchdogCmd = "pyinstaller --onefile --windowed --name LocalNameWatchdog --distpath `"$outputDir`" --workpath `"$appDir\build_watchdog`" --specpath `"$appDir`" `"$watchdogScript`""
Write-Host "Running: $watchdogCmd" -ForegroundColor Gray
Invoke-Expression $watchdogCmd

$watchdogDist = Join-Path $appDir "dist"
$watchdogBuild = Join-Path $appDir "build_watchdog"
if (Test-Path $watchdogDist) { Remove-Item -Recurse -Force $watchdogDist }
if (Test-Path $watchdogBuild) { Remove-Item -Recurse -Force $watchdogBuild }
$watchdogSpec = Join-Path $appDir "LocalNameWatchdog.spec"
if (Test-Path $watchdogSpec) { Remove-Item -Force $watchdogSpec }

$exePath = Join-Path $outputDir "LocalName.exe"
$watchdogExePath = Join-Path $outputDir "LocalNameWatchdog.exe"
if (Test-Path $exePath) {
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Main EXE:       $exePath" -ForegroundColor Green
    Write-Host "Watchdog EXE:   $watchdogExePath" -ForegroundColor Green
    Write-Host "Addon:          $(Join-Path $outputDir 'LocalName.mcaddon')" -ForegroundColor Green
    Write-Host "Test Addon:     $(Join-Path $outputDir 'LocalName_Test.mcaddon')" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}
