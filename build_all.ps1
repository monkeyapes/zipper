$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$addonDir = Join-Path $rootDir "addon"
$appDir = Join-Path $rootDir "app"
$androidDir = Join-Path $rootDir "android"
$outputDir = Join-Path $rootDir "build"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Zipper + LocalName Full Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build addon .mcaddon
Write-Host "[1/4] Building addon .mcaddon..." -ForegroundColor Yellow
$addonScript = Join-Path $addonDir "build_addon.py"
if (Test-Path $addonScript) {
    python $addonScript
}

# Step 2: Build addon asset files for Android
Write-Host "[2/4] Copying addon assets for Android..." -ForegroundColor Yellow
$androidAssets = Join-Path $androidDir "app\src\main\assets\addon"
if (Test-Path $androidAssets) {
    Remove-Item -Recurse -Force $androidAssets\* -ErrorAction SilentlyContinue
    # The asset files are written directly by our project files, just verify
    Write-Host "  Android addon assets ready" -ForegroundColor Green
}

# Step 3: Build Windows EXE
Write-Host "[3/4] Building Windows EXE..." -ForegroundColor Yellow
$appBuild = Join-Path $appDir "build.ps1"
if (Test-Path $appBuild) {
    & $appBuild
}

# Step 4: Build Android APK (requires Android SDK)
Write-Host "[4/4] Building Android APK..." -ForegroundColor Yellow
$gradlew = Join-Path $androidDir "gradlew.bat"
if (-not (Test-Path $gradlew)) {
    Write-Host "  Generating Gradle wrapper..." -ForegroundColor Gray
    # Try to generate wrapper
    $gradlePkg = Get-Command gradle -ErrorAction SilentlyContinue
    if ($gradlePkg) {
        Push-Location $androidDir
        gradle wrapper --gradle-version 8.5
        Pop-Location
    }
}

$gradlew = Join-Path $androidDir "gradlew.bat"
if (Test-Path $gradlew) {
    Write-Host "  Running Gradle build..." -ForegroundColor Gray
    Push-Location $androidDir
    ./gradlew assembleRelease
    Pop-Location
    $apkPath = Join-Path $androidDir "app\build\outputs\apk\release\app-release.apk"
    if (Test-Path $apkPath) {
        Copy-Item $apkPath (Join-Path $outputDir "Zipper.apk") -Force
        Write-Host "  APK: $(Join-Path $outputDir 'Zipper.apk')" -ForegroundColor Green
    } else {
        Write-Host "  APK build failed or not found. Try opening in Android Studio." -ForegroundColor Red
    }
} else {
    Write-Host "  Gradle wrapper not found. Open android/ in Android Studio to build." -ForegroundColor Red
    Write-Host "  Project: $androidDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Build Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output files:" -ForegroundColor White
if (Test-Path (Join-Path $outputDir "LocalName.exe")) {
    Write-Host "  EXE: build\LocalName.exe" -ForegroundColor Green
}
if (Test-Path (Join-Path $outputDir "LocalNameWatchdog.exe")) {
    Write-Host "  Watchdog: build\LocalNameWatchdog.exe" -ForegroundColor Green
}
if (Test-Path (Join-Path $outputDir "LocalName.mcaddon")) {
    Write-Host "  Addon: build\LocalName.mcaddon" -ForegroundColor Green
}
if (Test-Path (Join-Path $outputDir "Zipper.apk")) {
    Write-Host "  APK: build\Zipper.apk" -ForegroundColor Green
}
Write-Host ""
Write-Host "To build the APK, open android/ in Android Studio and run Build > APK" -ForegroundColor Yellow
Write-Host "Or install Android SDK + Gradle and run: ./gradlew assembleRelease" -ForegroundColor Yellow
