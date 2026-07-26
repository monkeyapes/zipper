$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$inputFile = Join-Path $rootDir "addon_encoded.b64"
$addonDir = Join-Path $rootDir "addon"

if (-not (Test-Path $inputFile)) {
    Write-Host "Encoded addon not found: $inputFile" -ForegroundColor Red
    exit 1
}

Write-Host "Decoding addon files..." -ForegroundColor Yellow

$json = [System.IO.File]::ReadAllText($inputFile)
$files = $json | ConvertFrom-Json

$count = 0
foreach ($f in $files) {
    $filePath = Join-Path $rootDir $f.path
    $dir = Split-Path -Parent $filePath
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $bytes = [Convert]::FromBase64String($f.data)
    [System.IO.File]::WriteAllBytes($filePath, $bytes)
    $count++
}

Write-Host "Decoded $count files to $addonDir" -ForegroundColor Green
