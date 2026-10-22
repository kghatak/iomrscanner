@echo off
setlocal DisableDelayedExpansion
REM Share this file alone. The pinned GitHub commit MUST be public.
set "OMR_INSTALLER_SELF=%~f0"
set "OMR_INSTALLER_ACTION=%~1"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$text = [IO.File]::ReadAllText($env:OMR_INSTALLER_SELF); $marker = '# OMR_POWERSHELL_PAYLOAD'; $offset = $text.LastIndexOf($marker); if ($offset -lt 0) { exit 1 }; & ([scriptblock]::Create($text.Substring($offset)))"
set "OMR_EXIT=%ERRORLEVEL%"
if not "%OMR_EXIT%"=="0" echo Installation or application failed. See the message above.
if /I not "%~1"=="--check" pause
exit /b %OMR_EXIT%

# OMR_POWERSHELL_PAYLOAD
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Publisher settings: advance SourceCommit only after testing the release.
$Repository = 'kghatak/iomrscanner'
$SourceCommit = 'bab3a6c63ef54c43c03a031a0aadad4656fba592'
$BootstrapUrl = 'https://api.anaconda.org/download/conda-forge/micromamba/2.9.0/win-64/micromamba-2.9.0-0.tar.bz2'
$BootstrapSha256 = '97a336f4ab794bd96a6a4da5e6ed63e75a1d31830414a182419b23d3b36f3fe0'
$SourceUrl = "https://codeload.github.com/$Repository/zip/$SourceCommit"
$Action = [string]$env:OMR_INSTALLER_ACTION
$InstallRoot = Join-Path $env:LOCALAPPDATA 'BignanManchaOMR'
$SourceDir = Join-Path $InstallRoot "app-$SourceCommit"
$EnvDir = Join-Path $InstallRoot 'environment'
$ManagerDir = Join-Path $InstallRoot 'manager'
$Manager = Join-Path $ManagerDir 'Library\bin\micromamba.exe'
$ReadyFile = Join-Path $InstallRoot 'ready.txt'
$OwnerFile = Join-Path $InstallRoot 'installation-owner.txt'
$OwnerId = 'BignanManchaOMR-managed-install-v1'
$Shortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Bignan Mancha OMR Reader.lnk'
$Work = $null
$Lock = $null
$TranscriptStarted = $false
$ExitCode = 1

function Download-File([string]$Url, [string]$Destination) {
    Write-Host "Downloading: $Url"
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Destination -TimeoutSec 180
            if ((Get-Item -LiteralPath $Destination).Length -eq 0) { throw 'Empty download.' }
            return
        } catch {
            Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
            if ($attempt -eq 3) {
                throw "Download failed: $Url. Check your connection. The repository and pinned commit must be public. $($_.Exception.Message)"
            }
            Write-Host "Download interrupted; retrying ($attempt/3)..."
        }
    }
}

function Run-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Expand-Source([string]$Archive, [string]$Destination) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        $root = [IO.Path]::GetFullPath($Destination).TrimEnd('\') + '\'
        $total = [long]0
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName.Replace('/', '\')
            $target = [IO.Path]::GetFullPath((Join-Path $root $name))
            if (-not $target.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -or
                $name.Contains(':') -or (($entry.ExternalAttributes -shr 16) -band 0xF000) -eq 0xA000) {
                throw "Unsafe archive entry: $name"
            }
            $total += $entry.Length
            if ($total -gt 2GB) { throw 'Source archive exceeds the 2 GB unpacked limit.' }
        }
    } finally { $zip.Dispose() }
    [IO.Compression.ZipFile]::ExtractToDirectory($Archive, $Destination)
}

function Set-ToolEnvironment {
    $env:PATH = "$EnvDir;$EnvDir\Scripts;$EnvDir\Library\bin;$env:PATH"
    # Ignore unrelated Python/tessdata settings from other installations.
    Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    $env:PYTHONUNBUFFERED = '1'
    $env:PYTHONNOUSERSITE = '1'
    $candidates = @("$EnvDir\Library\share\tessdata", "$EnvDir\share\tessdata", "$EnvDir\Library\bin\tessdata")
    $data = $candidates | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'eng.traineddata') } | Select-Object -First 1
    if (-not $data) { throw "Tesseract English data is missing in: $($candidates -join ', '). Run with --repair." }
    $env:TESSDATA_PREFIX = $data
    $env:OMR_POPPLER_BIN = "$EnvDir\Library\bin"
}

function Test-Installation {
    foreach ($file in @("$EnvDir\python.exe", "$EnvDir\Library\bin\tesseract.exe", "$EnvDir\Library\bin\pdfinfo.exe", "$EnvDir\Library\bin\pdftoppm.exe")) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing component: $file. Run with --repair." }
    }
    Set-ToolEnvironment
    Run-Checked "$EnvDir\python.exe" @('-m', 'pip', 'check')
    # Verify real OCR and PDF conversion, not merely executable existence.
    $probe = @'
import os, tempfile
from pathlib import Path
import cv2, flask, numpy, pandas, PyQt5, pytesseract, requests, torch, torchvision
import openpyxl, matplotlib, sklearn, qrcode
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_path
pytesseract.image_to_string(Image.new('RGB', (300, 100), 'white'), lang='eng')
with tempfile.TemporaryDirectory() as folder:
    path = str(Path(folder) / 'probe.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(40, 10, 'Installation check')
    pdf.output(path)
    images = convert_from_path(path, dpi=30, poppler_path=os.environ['OMR_POPPLER_BIN'])
    assert images, 'PDF conversion returned no images'
print('Python packages, OCR engine, English language data, and PDF conversion verified.')
'@
    Run-Checked "$EnvDir\python.exe" @('-c', $probe)
}

try {
    if ($Action -notin @('', '--repair', '--check', '--uninstall', '-u')) {
        throw 'Usage: run_app.bat [--repair | --check | --uninstall]'
    }
    if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') {
        throw 'This installer supports x64 Windows only (not ARM64 or 32-bit Windows).'
    }
    if ([Environment]::OSVersion.Version.Major -lt 10) { throw 'Windows 10 or later is required.' }
    if ($Action -eq '--check') {
        if (-not (Test-Path -LiteralPath $ReadyFile)) { throw 'Installation is not complete. Run without --check first.' }
        Test-Installation
        exit 0
    }
    if ($Action -in @('--uninstall', '-u')) {
        if (-not (Test-Path -LiteralPath $InstallRoot)) { Write-Host 'No managed installation found.'; exit 0 }
        if (-not (Test-Path -LiteralPath $OwnerFile) -or (Get-Content -LiteralPath $OwnerFile -Raw).Trim() -ne $OwnerId) {
            throw "Refusing to remove an unrecognized installation folder: $InstallRoot"
        }
        try {
            $uninstallLock = [IO.File]::Open((Join-Path $InstallRoot 'installer.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
        } catch { throw 'Close the application and other installers before uninstalling.' }
        Write-Host "This removes the managed application and environment at $InstallRoot."
        Write-Host 'WARNING: all files inside that folder, including results and source backups, will be removed.'
        Write-Host 'It does not remove system Python/Tesseract/Poppler or scans outside that folder.'
        try { $confirmation = Read-Host 'Type REMOVE to confirm' } finally { $uninstallLock.Dispose() }
        if ($confirmation -cne 'REMOVE') { exit 0 }
        if (Test-Path -LiteralPath $InstallRoot) { Remove-Item -LiteralPath $InstallRoot -Recurse -Force }
        if (Test-Path -LiteralPath $Shortcut) { Remove-Item -LiteralPath $Shortcut -Force }
        Write-Host 'Uninstalled.'
        exit 0
    }
    if (Test-Path -LiteralPath $InstallRoot) {
        if (-not (Test-Path -LiteralPath $OwnerFile) -or (Get-Content -LiteralPath $OwnerFile -Raw).Trim() -ne $OwnerId) {
            throw "Install folder already exists but is not owned by this installer: $InstallRoot. Move it aside before retrying."
        }
    } else {
        New-Item -ItemType Directory -Path $InstallRoot | Out-Null
        Set-Content -LiteralPath $OwnerFile -Value $OwnerId -Encoding ASCII
    }
    try { $Lock = [IO.File]::Open((Join-Path $InstallRoot 'installer.lock'), 'OpenOrCreate', 'ReadWrite', 'None') }
    catch { throw 'Another installer or application launched by this installer is running. Close it first.' }
    $LogPath = Join-Path $InstallRoot ('setup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
    Start-Transcript -Path $LogPath | Out-Null
    $TranscriptStarted = $true
    Write-Host "Installation folder: $InstallRoot"
    Write-Host 'First setup needs internet and several GB of free disk space. No administrator access is requested.'
    $Work = Join-Path $InstallRoot ('staging-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Work | Out-Null
    $env:MAMBA_ROOT_PREFIX = Join-Path $InstallRoot 'package-cache'
    $needsSetup = $Action -eq '--repair' -or -not (Test-Path -LiteralPath $ReadyFile)
    if (-not $needsSetup) { $needsSetup = (Get-Content -LiteralPath $ReadyFile -Raw).Trim() -ne $SourceCommit }
    if (-not (Test-Path -LiteralPath (Join-Path $SourceDir 'main.py'))) { $needsSetup = $true }

    if ($needsSetup) {
        Remove-Item -LiteralPath $ReadyFile -Force -ErrorAction SilentlyContinue
        # Fail on a private/missing repository before installing dependencies.
        $archive = Join-Path $Work 'source.zip'
        Download-File $SourceUrl $archive
        $extracted = Join-Path $Work 'source'
        Expand-Source $archive $extracted
        $folders = @(Get-ChildItem -LiteralPath $extracted -Directory)
        if ($folders.Count -ne 1) { throw 'Unexpected source archive structure.' }
        foreach ($required in @('main.py', 'requirements.txt', 'ui', 'pipeline')) {
            if (-not (Test-Path -LiteralPath (Join-Path $folders[0].FullName $required))) { throw "Source archive is missing $required." }
        }
        # Re-download on repair to recover from a damaged manager executable.
        if ($Action -eq '--repair' -or -not (Test-Path -LiteralPath $Manager)) {
            if (-not (Get-Command tar.exe -ErrorAction SilentlyContinue)) { throw 'Windows tar.exe was not found. Install Windows updates and check your Windows system PATH.' }
            $bootstrap = Join-Path $Work 'micromamba.tar.bz2'
            Download-File $BootstrapUrl $bootstrap
            if ((Get-FileHash -LiteralPath $bootstrap -Algorithm SHA256).Hash -ne $BootstrapSha256) { throw 'Bootstrap checksum verification failed. Nothing will be executed.' }
            New-Item -ItemType Directory -Path $ManagerDir -Force | Out-Null
            Run-Checked 'tar.exe' @('-xjf', $bootstrap, '-C', $ManagerDir, 'Library/bin/micromamba.exe')
        }
        Write-Host 'Installing isolated Python 3.12, Tesseract, language data, and Poppler...'
        # --no-rc prevents unrelated conda/mamba configuration from affecting setup.
        if (Test-Path -LiteralPath (Join-Path $EnvDir 'conda-meta')) {
            Run-Checked $Manager @('--no-rc', 'install', '--yes', '--override-channels', '--channel', 'conda-forge', '--prefix', $EnvDir, 'python=3.12', 'pip', 'tesseract', 'poppler')
        } else {
            if (Test-Path -LiteralPath $EnvDir) { Remove-Item -LiteralPath $EnvDir -Recurse -Force }
            Run-Checked $Manager @('--no-rc', 'create', '--yes', '--override-channels', '--channel', 'conda-forge', '--prefix', $EnvDir, 'python=3.12', 'pip', 'tesseract', 'poppler')
        }
        Set-ToolEnvironment
        Run-Checked "$EnvDir\python.exe" @('-m', 'pip', 'install', '--disable-pip-version-check', '-r', (Join-Path $folders[0].FullName 'requirements.txt'))
        Test-Installation
        if (Test-Path -LiteralPath $SourceDir) {
            $backup = "$SourceDir-backup-$([Guid]::NewGuid().ToString('N'))"
            Move-Item -LiteralPath $SourceDir -Destination $backup
            Write-Host "Previous source and any results inside it were preserved at: $backup"
        }
        Move-Item -LiteralPath $folders[0].FullName -Destination $SourceDir
        $installedLauncher = Join-Path $InstallRoot 'run_app.bat'
        if ([IO.Path]::GetFullPath($env:OMR_INSTALLER_SELF) -ne $installedLauncher) {
            Copy-Item -LiteralPath $env:OMR_INSTALLER_SELF -Destination $installedLauncher -Force
        }
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($Shortcut)
        $link.TargetPath = $installedLauncher
        $link.WorkingDirectory = $InstallRoot
        $link.Description = 'Launch Bignan Mancha OMR Reader'
        $link.Save()
        Set-Content -LiteralPath $ReadyFile -Value $SourceCommit -Encoding ASCII
        Write-Host 'Installation complete. A desktop shortcut has been created.'
    } else {
        Set-ToolEnvironment
        if (-not (Test-Path -LiteralPath "$EnvDir\python.exe")) { throw 'Python is missing. Run with --repair.' }
    }
    Write-Host 'Starting application. Keep this console open until you close the application.'
    Push-Location $SourceDir
    try { & "$EnvDir\python.exe" 'main.py'; $ExitCode = $LASTEXITCODE }
    finally { Pop-Location }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($TranscriptStarted) { Write-Host "Installation log: $LogPath" }
    $ExitCode = 1
} finally {
    if ($Work -and (Test-Path -LiteralPath $Work)) { Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue }
    if ($TranscriptStarted) { Stop-Transcript | Out-Null }
    if ($Lock) { $Lock.Dispose() }
}
exit $ExitCode