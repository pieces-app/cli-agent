$ErrorActionPreference = 'Stop'

$packageName = $env:ChocolateyPackageName
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# Remove the shim
Uninstall-BinFile -Name 'pieces'

Write-Host "Pieces CLI has been uninstalled successfully."
