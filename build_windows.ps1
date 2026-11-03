# Local Windows release builder. OutputDirectory holds the installer and portable
# archive; Version is embedded in the Inno Setup metadata.
param(
    [string]$OutputDirectory = "releases",
    [string]$Version = "0.0.0"
)

# Treat every failing command as a build failure and run relative to this script.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Reuse the isolated build environment when present. Otherwise locate a system
# Python installation and create it, keeping build tools out of the user runtime.
$Python = ".venv-windows\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Candidate = $null
    foreach ($Command in @("py", "python")) {
        try {
            & $Command --version 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { $Candidate = $Command; break }
        } catch { }
    }
    if ($null -eq $Candidate) {
        throw "Python 3.10 or newer is required to build the application."
    }
    & $Candidate -m venv .venv-windows
}

# Install both runtime and packaging dependencies into the build environment.
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-build.txt

# Start from clean staging directories so stale binaries cannot enter a release.
$WorkPath = Join-Path $PSScriptRoot ".build\windows"
$DistPath = Join-Path $PSScriptRoot "dist"
Remove-Item -LiteralPath $WorkPath, $DistPath -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $WorkPath, $DistPath, $OutputDirectory | Out-Null

# Produce the onedir application described by the shared PyInstaller spec.
& $Python -m PyInstaller --noconfirm --clean --workpath $WorkPath --distpath $DistPath LEDD_Calculator.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE." }

# Inno Setup wraps the onedir output in a per-user Windows installer.
$InnoSetup = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path -LiteralPath $InnoSetup)) {
    throw "Inno Setup 6 is required to create the installer: https://jrsoftware.org/isdl.php"
}

& $InnoSetup "/DMyAppVersion=$Version" "/O$OutputDirectory" LEDD_Calculator.iss
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed with exit code $LASTEXITCODE." }

# Also publish a no-install archive for users who cannot run an installer.
Compress-Archive -LiteralPath (Join-Path $DistPath "LEDD Calculator") -DestinationPath (Join-Path $OutputDirectory "LEDD-Calculator-Windows-x64-Portable.zip") -CompressionLevel Optimal -Force
Write-Host "Created $OutputDirectory\LEDD-Calculator-Windows-x64-Setup.exe"
Write-Host "Created $OutputDirectory\LEDD-Calculator-Windows-x64-Portable.zip"
