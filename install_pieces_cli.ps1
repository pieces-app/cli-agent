# Pieces CLI Installation Script for PowerShell (Cross-Platform)
# This script installs the Pieces CLI tool in a virtual environment
# and optionally sets up shell completion.

Write-Host "Welcome to the Pieces CLI Installer!" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Blue

# Function to print colored output
function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if running on Windows
function Test-Windows {
    return $IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)
}

# Get the appropriate home directory
function Get-HomeDirectory {
    if (Test-Windows) {
        return $env:USERPROFILE
    } else {
        return $env:HOME
    }
}

# Get the appropriate path separator
function Get-PathSeparator {
    if (Test-Windows) {
        return ';'
    } else {
        return ':'
    }
}

# Check if a command exists
function Test-Command {
    param($CommandName)
    try {
        Get-Command $CommandName -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check if a Python version meets minimum requirements (3.11+)
function Test-PythonVersion {
    param($PythonCmd)
    try {
        $version = & $PythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($version) {
            $major, $minor = $version.Split('.')
            return ([int]$major -eq 3) -and ([int]$minor -ge 11)
        }
        return $false
    }
    catch {
        return $false
    }
}

# Find the best Python executable available
function Find-Python {
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            if (Test-PythonVersion $cmd) {
                return $cmd
            }
        }
    }
    
    # Try Python Launcher with version specifiers (Windows only)
    if (Test-Windows) {
        $pythonVersions = @("py -3.12", "py -3.11", "py -3")
        foreach ($cmd in $pythonVersions) {
            try {
                $cmdParts = $cmd.Split(' ')
                if (Test-PythonVersion $cmdParts) {
                    return $cmd
                }
            }
            catch {
                continue
            }
        }
    }
    
    return $null
}

# Setup completion for PowerShell
function Setup-PowerShellCompletion {
    param($InstallDir)
    
    # Check if PowerShell profile exists
    if (!(Test-Path $PROFILE)) {
        Write-Info "Creating PowerShell profile at $PROFILE"
        New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    }
    
    # Check if completion is already configured
    if (Get-Content $PROFILE -ErrorAction SilentlyContinue | Select-String "pieces completion") {
        Write-Info "Completion already configured in $PROFILE"
        return $true
    }
    
    # Add completion to profile
    $completionCmd = '$completionPiecesScript = pieces completion powershell | Out-String; Invoke-Expression $completionPiecesScript'
    Add-Content -Path $PROFILE -Value $completionCmd
    Write-Success "Added completion to $PROFILE"
    
    return $true
}

# Setup PATH for PowerShell
function Setup-PowerShellPath {
    param($InstallDir)
    
    $pathSeparator = Get-PathSeparator
    
    # Check if directory is already in PATH
    if ($env:PATH -split $pathSeparator | Where-Object { $_ -eq $InstallDir }) {
        Write-Info "Pieces CLI directory already in PATH"
        return $true
    }
    
    if (Test-Windows) {
        # Windows-specific PATH setup
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath) {
            $newPath = "$InstallDir;$currentPath"
        } else {
            $newPath = $InstallDir
        }
        
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Success "Added Pieces CLI to user PATH"
        
        # Update current session PATH
        $env:PATH = "$InstallDir;$env:PATH"
    } else {
        # Unix-like systems - add to shell profile
        $homeDir = Get-HomeDirectory
        $shellProfile = "$homeDir/.profile"
        
        # Check if PATH is already in profile
        if (Test-Path $shellProfile) {
            $profileContent = Get-Content $shellProfile -ErrorAction SilentlyContinue
            if ($profileContent | Select-String $InstallDir) {
                Write-Info "PATH already configured in $shellProfile"
                return $true
            }
        }
        
        # Add to profile
        $pathLine = "export PATH=`"$InstallDir`":`$PATH"
        Add-Content -Path $shellProfile -Value $pathLine
        Write-Success "Added PATH to $shellProfile"
        
        # Update current session PATH
        $env:PATH = "$InstallDir" + $pathSeparator + $env:PATH
    }
    
    return $true
}

# Check if running as admin/root
function Test-Administrator {
    if (Test-Windows) {
        try {
            $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
            return $isAdmin
        }
        catch {
            return $false
        }
    } else {
        # Unix-like systems - check if running as root
        return (id -u) -eq 0
    }
}

# Main installation function
function Install-PiecesCLI {
    Write-Info "Starting Pieces CLI installation..."
    
    # Step 1: Check if running as Administrator/root
    if (Test-Administrator) {
        Write-Warning "You appear to be running this script as Administrator/root."
        Write-Warning "This may cause the installation to be inaccessible to non-admin users."
        $continue = Read-Host "Continue anyway? [y/N]"
        if ($continue -notmatch '^[yY]([eE][sS])?$') {
            Write-Info "Installation cancelled."
            return
        }
    }
    
    # Step 2: Find Python executable
    Write-Info "Locating Python executable..."
    $pythonCmd = Find-Python
    
    if (!$pythonCmd) {
        Write-Error "Python 3.11+ is required but not found on your system."
        Write-Error "Please install Python 3.11 or higher from: https://www.python.org/downloads/"
        if (Test-Windows) {
            Write-Error "Make sure to check 'Add Python to PATH' during installation."
        }
        return
    }
    
    # Get Python version for display
    $pythonVersion = & $pythonCmd.Split(' ') --version 2>&1
    Write-Success "Found Python: $pythonCmd ($pythonVersion)"
    
    # Step 3: Set installation directory
    $homeDir = Get-HomeDirectory
    $installDir = Join-Path $homeDir ".pieces-cli"
    $venvDir = Join-Path $installDir "venv"
    
    Write-Info "Installation directory: $installDir"
    
    # Create installation directory
    if (!(Test-Path $installDir)) {
        New-Item -Path $installDir -ItemType Directory | Out-Null
    }
    
    # Step 4: Create virtual environment
    Write-Info "Creating virtual environment..."
    if (Test-Path $venvDir) {
        Write-Warning "Virtual environment already exists. Removing old environment..."
        Remove-Item -Path $venvDir -Recurse -Force
    }
    
    $createVenvCmd = $pythonCmd.Split(' ') + @("-m", "venv", $venvDir)
    & $createVenvCmd[0] $createVenvCmd[1..($createVenvCmd.Length-1)]
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        Write-Error "Please ensure you have the 'venv' module available."
        return
    }
    
    Write-Success "Virtual environment created successfully."
    
    # Step 5: Install pieces-cli
    Write-Info "Installing Pieces CLI..."
    
    # Use venv's pip - different paths for Windows vs Unix
    if (Test-Windows) {
        $venvPip = Join-Path $venvDir "Scripts\pip.exe"
    } else {
        $venvPip = Join-Path $venvDir "bin/pip"
    }
    
    # Upgrade pip first
    & $venvPip install --upgrade pip
    
    # Install pieces-cli
    & $venvPip install pieces-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install pieces-cli."
        Write-Error "Please check your internet connection and try again."
        return
    }
    
    Write-Success "Pieces CLI installed successfully!"
    
    # Step 6: Create wrapper script
    Write-Info "Creating wrapper script..."
    
    if (Test-Windows) {
        $wrapperScript = Join-Path $installDir "pieces.cmd"
        $wrapperContent = @"
@echo off
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "PIECES_EXECUTABLE=%VENV_DIR%\Scripts\pieces.exe"

if not exist "%VENV_DIR%" (
    echo Error: Pieces CLI virtual environment not found at %VENV_DIR%
    echo Please reinstall Pieces CLI.
    exit /b 1
)

if not exist "%PIECES_EXECUTABLE%" (
    echo Error: Pieces CLI executable not found at %PIECES_EXECUTABLE%
    echo Please reinstall Pieces CLI.
    exit /b 1
)

"%PIECES_EXECUTABLE%" %*
"@
    } else {
        $wrapperScript = Join-Path $installDir "pieces"
        $wrapperContent = @"
#!/bin/sh
# Pieces CLI Wrapper Script
SCRIPT_DIR="`$(cd "`$(dirname "`$0")" && pwd)"
VENV_DIR="`$SCRIPT_DIR/venv"
PIECES_EXECUTABLE="`$VENV_DIR/bin/pieces"

# Check if virtual environment exists
if [ ! -d "`$VENV_DIR" ]; then
    echo "Error: Pieces CLI virtual environment not found at `$VENV_DIR"
    echo "Please reinstall Pieces CLI."
    exit 1
fi

# Check if pieces executable exists
if [ ! -f "`$PIECES_EXECUTABLE" ]; then
    echo "Error: Pieces CLI executable not found at `$PIECES_EXECUTABLE"
    echo "Please reinstall Pieces CLI."
    exit 1
fi

# Run pieces directly from venv without activation
exec "`$PIECES_EXECUTABLE" "`$@"
"@
    }
    
    Set-Content -Path $wrapperScript -Value $wrapperContent
    
    # Make executable on Unix-like systems
    if (!(Test-Windows)) {
        chmod +x $wrapperScript
    }
    
    Write-Success "Wrapper script created at: $wrapperScript"
    
    # Step 7: Configure PowerShell
    Write-Info "Configuring PowerShell integration..."
    
    if (Test-Command "pwsh") {
        Write-Info "Found PowerShell Core (pwsh)"
        $shells = @("PowerShell", "PowerShell Core")
    } else {
        Write-Info "Found Windows PowerShell"
        $shells = @("PowerShell")
    }
    
    Write-Host ""
    foreach ($shell in $shells) {
        Write-Host "--- $shell configuration ---" -ForegroundColor Magenta
        
        # Ask about PATH setup
        $addPath = Read-Host "Add Pieces CLI to PATH in $shell? [Y/n]"
        if ($addPath -notmatch '^[nN]([oO])?$') {
            Write-Info "Setting up PATH for $shell..."
            Setup-PowerShellPath $installDir
        } else {
            Write-Info "Skipping PATH setup for $shell"
        }
        
        # Ask about completion setup
        $enableCompletion = Read-Host "Enable shell completion for $shell? [Y/n]"
        if ($enableCompletion -notmatch '^[nN]([oO])?$') {
            Write-Info "Setting up completion for $shell..."
            Setup-PowerShellCompletion $installDir
        } else {
            Write-Info "Skipping completion setup for $shell"
        }
        
        Write-Host ""
    }
    
    # Step 8: Final instructions
    Write-Host ""
    Write-Success "Installation completed successfully!"
    Write-Host ""
    Write-Info "To start using Pieces CLI:"
    if (Test-Windows) {
        Write-Info "  1. Restart your PowerShell session to load new PATH"
        Write-Info "  2. Or reload your profile: . `$PROFILE"
    } else {
        Write-Info "  1. Restart your terminal or reload your shell configuration"
        Write-Info "  2. Or reload your profile: source ~/.profile"
    }
    Write-Info "  3. Verify installation: pieces version"
    Write-Info "  4. Get help: pieces help"
    Write-Host ""
    Write-Info "Alternative: You can always run the CLI directly:"
    Write-Info "  $wrapperScript"
    Write-Host ""
    Write-Info "Make sure PiecesOS is installed and running:"
    Write-Info "  Download from: https://pieces.app/"
    Write-Info "  Documentation: https://docs.pieces.app/"
    Write-Host ""
    Write-Info "Shell completion can be enabled later with:"
    Write-Info "  pieces completion powershell"
    Write-Host ""
    Write-Info "If you encounter any issues, visit:"
    Write-Info "  https://github.com/pieces-app/cli-agent"
    Write-Host ""
}

# Run the installation
Install-PiecesCLI 
