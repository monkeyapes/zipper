$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$addonDir = Join-Path $rootDir "addon"
$outputFile = Join-Path $rootDir "addon_encoded.b64"

if (-not (Test-Path $addonDir)) {
    Write-Host "Addon directory not found: $addonDir" -ForegroundColor Red
    exit 1
}

Write-Host "Encoding addon files..." -ForegroundColor Yellow

$files = @()
Get-ChildItem -Path $addonDir -Recurse -File | ForEach-Object {
    $relPath = $_.FullName.Substring($rootDir.Length + 1)
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    $b64 = [Convert]::ToBase64String($bytes)
    $files += @{ path = $relPath; data = $b64 }
}

$json = $files | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText($outputFile, $json)

Write-Host "Encoded $($files.Count) files -> $outputFile" -ForegroundColor Green
Write-Host "Total size: $($json.Length) bytes" -ForegroundColor Green
