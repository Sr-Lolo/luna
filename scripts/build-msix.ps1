param(
    [string]$ProjectRoot = "C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55"
)

$Staging = Join-Path $ProjectRoot "msix-staging"
$PackageDir = Join-Path $ProjectRoot "msix-package"
$OutDir = Join-Path $ProjectRoot "dist"
$MakeAppx = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe"
$MakePri = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makepri.exe"

$Version = "1.8.0.0"
$PackageName = "SrLolo.LunaDeck"

Write-Host "=== LunaDeck MSIX Builder ===" -ForegroundColor Cyan
Write-Host ""

# Clean staging
if (Test-Path $Staging) { Remove-Item -Path $Staging -Recurse -Force }
New-Item -ItemType Directory -Path $Staging -Force | Out-Null
New-Item -ItemType Directory -Path "$Staging\assets" -Force | Out-Null
New-Item -ItemType Directory -Path "$Staging\web" -Force | Out-Null
New-Item -ItemType Directory -Path "$Staging\web_ad" -Force | Out-Null
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

Write-Host "[1/6] Copying Luna.exe..." -ForegroundColor Yellow
Copy-Item "$ProjectRoot\server\dist\Luna.exe" "$Staging\Luna.exe" -Force

Write-Host "[2/6] Copying web files..." -ForegroundColor Yellow
Copy-Item "$ProjectRoot\server\web\*" "$Staging\web\" -Recurse -Force

Write-Host "[3/6] Copying web_ad files..." -ForegroundColor Yellow
Copy-Item "$ProjectRoot\server\web_ad\*" "$Staging\web_ad\" -Recurse -Force

Write-Host "[4/6] Copying assets and manifest..." -ForegroundColor Yellow
Copy-Item "$PackageDir\AppxManifest.xml" "$Staging\AppxManifest.xml" -Force
Copy-Item "$PackageDir\assets\*" "$Staging\assets\" -Force
Copy-Item "$ProjectRoot\server\app.ico" "$Staging\" -Force

Write-Host "[5/6] Generating resources.pri..." -ForegroundColor Yellow
& $MakePri new /pr $Staging /cf "$PackageDir\priconfig.xml" /mn "$Staging\AppxManifest.xml" /of "$Staging\resources.pri" /o

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: makepri failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "$Staging\resources.pri")) {
    Write-Host "ERROR: resources.pri was not generated" -ForegroundColor Red
    exit 1
}
Write-Host "  resources.pri generated successfully" -ForegroundColor Green

Write-Host "[6/6] Building MSIX..." -ForegroundColor Yellow

$MsixPath = "$OutDir\LunaDeck_${Version}_x64.msix"

# Remove previous msix
if (Test-Path $MsixPath) { Remove-Item $MsixPath -Force }

# Verify all files exist
$requiredFiles = @(
    "$Staging\Luna.exe",
    "$Staging\AppxManifest.xml",
    "$Staging\resources.pri",
    "$Staging\assets\StoreLogo.png",
    "$Staging\assets\Square150x150Logo.png",
    "$Staging\assets\Square44x44Logo.png",
    "$Staging\assets\Square71x71Logo.png",
    "$Staging\assets\Square310x310Logo.png",
    "$Staging\assets\Wide310x150Logo.png",
    "$Staging\assets\SplashScreen.png"
)
$missing = $false
foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) {
        Write-Host "  MISSING: $f" -ForegroundColor Red
        $missing = $true
    }
}
if ($missing) {
    Write-Host "ERROR: Missing required files. Aborting." -ForegroundColor Red
    exit 1
}

# Run MakeAppx.exe
& $MakeAppx pack /p $MsixPath /d $Staging /l

if ($LASTEXITCODE -eq 0) {
    $sizeInMB = [math]::Round((Get-Item $MsixPath).Length / 1MB, 1)
    Write-Host ""
    Write-Host "SUCCESS: $MsixPath" -ForegroundColor Green
    Write-Host "Size: ${sizeInMB} MB" -ForegroundColor Green
} else {
    Write-Host "ERROR: MakeAppx failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Cleanup staging
Write-Host "Cleaning staging..." -ForegroundColor Yellow
Remove-Item -Path $Staging -Recurse -Force

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "Package ready: $MsixPath"
