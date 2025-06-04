$ErrorActionPreference = 'Stop'

$packageName = $env:ChocolateyPackageName
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# The pieces directory should already be in tools from the package
$piecesDir = Join-Path $toolsDir 'pieces'
$exePath = Join-Path $piecesDir 'pieces.exe'

# Verify the executable exists
if (!(Test-Path $exePath)) {
    throw "pieces.exe not found at $exePath"
}

Write-Host "Pieces CLI found at $exePath"

# Create a shim so the executable is available in PATH
Install-BinFile -Name 'pieces' -Path $exePath

Write-Host "Pieces CLI is now available. Try running 'pieces --version' to verify the installation."
