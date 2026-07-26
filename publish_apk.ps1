param(
    [string]$Token = "",
    [string]$Repo = "",
    [string]$Tag = "v1.0.0",
    [string]$ApkPath = ""
)

if (-not $Token) { $Token = Read-Host "GitHub Token" }
if (-not $Repo)  { $Repo  = Read-Host "Repo (user/repo)" }
if (-not $ApkPath) { $ApkPath = "build\Zipper.apk" }

$ApkPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) $ApkPath
$apkName = Split-Path $ApkPath -Leaf

if (-not (Test-Path $ApkPath)) {
    Write-Host "APK not found at $ApkPath. Build it first." -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "token $Token"
    Accept = "application/vnd.github.v3+json"
}

Write-Host "Creating release $Tag ..." -ForegroundColor Yellow
$body = @{
    tag_name = $Tag
    name = "Zipper $Tag"
    body = "Zipper APK release"
    draft = $false
    prerelease = $false
} | ConvertTo-Json

try {
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases" `
        -Method Post -Headers $headers -Body $body -ContentType "application/json"
} catch {
    Write-Host "Release creation failed: $_" -ForegroundColor Red
    exit 1
}

$uploadUrl = $release.upload_url -replace '\{.*\}', "?name=$apkName"
Write-Host "Uploading $apkName ..." -ForegroundColor Yellow

try {
    $upload = Invoke-RestMethod -Uri $uploadUrl -Method Post `
        -Headers @{ Authorization = "token $Token"; "Content-Type" = "application/vnd.android.package-archive" } `
        -InFile $ApkPath
    Write-Host "Done! Download at:" -ForegroundColor Green
    Write-Host "https://github.com/$Repo/releases/latest/download/$apkName" -ForegroundColor Cyan
} catch {
    Write-Host "Upload failed: $_" -ForegroundColor Red
    exit 1
}
