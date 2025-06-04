# This runs before upgrade or uninstall.
# Use this file to do things like stop services prior to upgrade or uninstall.
# NOTE: It is an anti-pattern to call chocolateyUninstall.ps1 from here. If you
#  need to uninstall an MSI prior to upgrade, put the functionality in this
#  file without calling the uninstall script. Make it idempotent in the
#  uninstall script so that it doesn't fail when it is already uninstalled.
# NOTE: For upgrades - like the uninstall script, this script always runs from
#  the currently installed version, not from the new upgraded package version.

$ErrorActionPreference = 'Stop'

# Stop any running instances of the CLI tool
Get-Process -Name "pieces-cli" -ErrorAction SilentlyContinue | Stop-Process -Force

# Ensure we have write access to the data directory
$dataDir = "$env:LOCALAPPDATA\pieces\cli-agent"
if (Test-Path $dataDir) {
    # Remove any read-only attributes that might prevent deletion
    Get-ChildItem -Path $dataDir -Recurse | ForEach-Object {
        if ($_.IsReadOnly) {
            $_.IsReadOnly = $false
        }
    }
}

