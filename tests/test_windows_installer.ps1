# Run with Windows PowerShell 5.1. No Python, downloads or installation needed.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$launcher = Join-Path (Split-Path $PSScriptRoot -Parent) 'run_app.bat'
$text = [IO.File]::ReadAllText($launcher)
$marker = '# OMR_POWERSHELL_PAYLOAD'
$payload = $text.Substring($text.LastIndexOf($marker))
$tokens = $null
$errors = $null
$ast = [Management.Automation.Language.Parser]::ParseInput($payload, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }

function Assert-True($Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}
function Assert-Throws([scriptblock]$Operation, [string]$Message) {
    $thrown = $false
    try { & $Operation } catch { $thrown = $true }
    Assert-True $thrown $Message
}

# Load only function definitions, never the installer entry point.
foreach ($statement in $ast.EndBlock.Statements) {
    if ($statement -is [Management.Automation.Language.FunctionDefinitionAst]) {
        . ([scriptblock]::Create($statement.Extent.Text))
    }
}
$temp = Join-Path ([IO.Path]::GetTempPath()) ('OMR installer tests ' + [Guid]::NewGuid().ToString('N'))
$oldPath = $env:PATH
$oldData = $env:TESSDATA_PREFIX
$oldHome = $env:PYTHONHOME
$oldPythonPath = $env:PYTHONPATH
$oldUnbuffered = $env:PYTHONUNBUFFERED
$oldNoUserSite = $env:PYTHONNOUSERSITE
$oldPoppler = $env:OMR_POPPLER_BIN
try {
    New-Item -ItemType Directory -Path $temp | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zipPath = Join-Path $temp 'source.zip'
    $zip = [IO.Compression.ZipFile]::Open($zipPath, 'Create')
    try {
        $entry = $zip.CreateEntry('repo-commit/main.py')
        $writer = New-Object IO.StreamWriter($entry.Open())
        try { $writer.Write('test fixture') } finally { $writer.Dispose() }
    } finally { $zip.Dispose() }
    $destination = Join-Path $temp 'extracted with spaces'
    Expand-Source $zipPath $destination
    Assert-True (Test-Path -LiteralPath (Join-Path $destination 'repo-commit\main.py')) 'Valid source archive was not extracted.'

    foreach ($badName in @('../escape.txt', 'repo/../../escape.txt', 'repo/evil.txt:stream', 'C:/escape.txt', '..\escape.txt')) {
        $badZip = Join-Path $temp ('bad-' + [Guid]::NewGuid().ToString('N') + '.zip')
        $zip = [IO.Compression.ZipFile]::Open($badZip, 'Create')
        try { $null = $zip.CreateEntry($badName) } finally { $zip.Dispose() }
        Assert-Throws { Expand-Source $badZip (Join-Path $temp 'unsafe') } "Unsafe archive accepted: $badName"
    }
    $badZip = Join-Path $temp 'symlink.zip'
    $zip = [IO.Compression.ZipFile]::Open($badZip, 'Create')
    try {
        $entry = $zip.CreateEntry('repo/link')
        $entry.ExternalAttributes = -1577058304 # Unix symlink mode 0xA2000000
    } finally { $zip.Dispose() }
    Assert-Throws { Expand-Source $badZip (Join-Path $temp 'symlink') } 'Symlink archive accepted.'

    $EnvDir = Join-Path $temp 'environment with spaces'
    $dataDir = Join-Path $EnvDir 'Library\share\tessdata'
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    $env:TESSDATA_PREFIX = 'unrelated installation'
    Assert-Throws { Set-ToolEnvironment } 'Missing English language data accepted.'
    New-Item -ItemType File -Path (Join-Path $dataDir 'eng.traineddata') | Out-Null
    $env:PYTHONHOME = 'unrelated python'
    $env:PYTHONPATH = 'unrelated modules'
    Set-ToolEnvironment
    Assert-True ($env:TESSDATA_PREFIX -eq $dataDir) 'Incorrect tessdata path.'
    Assert-True ($env:OMR_POPPLER_BIN -eq "$EnvDir\Library\bin") 'Incorrect Poppler path.'
    Assert-True ($env:PATH.StartsWith("$EnvDir;$EnvDir\Scripts;$EnvDir\Library\bin;")) 'Tool PATH priority is incorrect.'
    Assert-True (-not $env:PYTHONHOME -and -not $env:PYTHONPATH) 'Inherited Python configuration was not cleared.'
    Assert-Throws { Test-Installation } 'Missing executables accepted.'
    Run-Checked $env:ComSpec @('/d', '/c', 'exit 0')
    Assert-Throws { Run-Checked $env:ComSpec @('/d', '/c', 'exit 7') } 'Native command failure was ignored.'

    # Exercise the actual CMD -> Windows PowerShell boundary, including paths
    # with spaces, without running setup or requiring an existing installation.
    $copy = Join-Path $temp 'shareable launcher.bat'
    Copy-Item -LiteralPath $launcher -Destination $copy
    & $env:ComSpec /d /c "echo. | call `"$copy`" --invalid-option"
    Assert-True ($LASTEXITCODE -eq 1) 'Invalid argument did not produce a failure exit code.'
    Write-Host 'PASS: PowerShell 5.1 parsing, safe extraction, tool environment, native failures, and standalone CMD bootstrap.'
} finally {
    $env:PATH = $oldPath
    $env:TESSDATA_PREFIX = $oldData
    $env:PYTHONHOME = $oldHome
    $env:PYTHONPATH = $oldPythonPath
    $env:PYTHONUNBUFFERED = $oldUnbuffered
    $env:PYTHONNOUSERSITE = $oldNoUserSite
    $env:OMR_POPPLER_BIN = $oldPoppler
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}