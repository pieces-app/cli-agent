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
        # Handle both string and array inputs
        if ($PythonCmd -is [array]) {
            $result = & $PythonCmd[0] $PythonCmd[1..($PythonCmd.Length-1)] -c "import sys; print('true' if sys.version_info >= (3, 11) else 'false')" 2>$null
        } else {
            $result = & $PythonCmd -c "import sys; print('true' if sys.version_info >= (3, 11) else 'false')" 2>$null
        }
        return $result -eq 'true'
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
    # Validate InstallDir existence
    if (!(Test-Path $InstallDir)) {
        Write-Error "Installation directory does not exist: $InstallDir"
        return $false
    }

    # Check PATH length limit (Windows-specific)
    if (Test-Windows) {
        $maxPathLength = 2048  # Typical safe maximum for PATH
        if (($env:PATH.Length + $InstallDir.Length + 1) -ge $maxPathLength) {
            Write-Error "Adding the installation directory would exceed the PATH length limit."
            return $false
        }
    }

    if ($env:PATH -split $pathSeparator | Where-Object { $_ -eq $InstallDir }) {
        Write-Info "Pieces CLI directory already in PATH"
        return $true
    }

    if (Test-Windows) {
        # Validate InstallDir existence
        if (!(Test-Path $InstallDir)) {
            Write-Error "Installation directory does not exist: $InstallDir"
            return $false
        }

        # Windows-specific PATH setup
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

        # Check PATH length limit
        $maxPathLength = 2048
        if ($currentPath -and ($currentPath.Length + $InstallDir.Length + 1) -ge $maxPathLength) {
            Write-Error "Adding the installation directory would exceed the PATH length limit."
            return $false
        }

        try {
            if ($currentPath) {
                $newPath = "$InstallDir;$currentPath"
            } else {
                $newPath = $InstallDir
            }

            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Success "Added Pieces CLI to user PATH"

            # Update current session PATH
            $env:PATH = "$InstallDir;$env:PATH"
        }
        catch {
            Write-Error "Failed to update PATH: $_"
            return $false
        }
    } else {
        # Unix-like systems - add to shell profile
        $homeDir = Get-HomeDirectory
        $shellProfile = "$homeDir/.profile"

        # Validate InstallDir existence
        if (!(Test-Path $InstallDir)) {
            Write-Error "Installation directory does not exist: $InstallDir"
            return $false
        }

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

# Verify SHA256 checksum of a file
function Test-FileChecksum {
    param(
        [string]$FilePath,
        [string]$ExpectedChecksum
    )

    if (!(Test-Path $FilePath)) {
        Write-Error "File not found: $FilePath"
        return $false
    }

    try {
        $actualChecksum = (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash.ToLower()
        $expectedLower = $ExpectedChecksum.ToLower()

        if ($actualChecksum -eq $expectedLower) {
            return $true
        } else {
            Write-Error "Checksum verification failed for $FilePath"
            Write-Error "Expected: $expectedLower"
            Write-Error "Actual:   $actualChecksum"
            return $false
        }
    }
    catch {
        Write-Error "Failed to calculate checksum for $FilePath : $_"
        return $false
    }
}

# Download a file with Invoke-WebRequest and verify its checksum
function Invoke-SecureDownload {
    param(
        [string]$Url,
        [string]$OutputPath,
        [string]$ExpectedChecksum
    )

    Write-Info "Downloading $(Split-Path $OutputPath -Leaf)..."

    try {
        # Download with Invoke-WebRequest
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing

        # Verify checksum
        if (Test-FileChecksum -FilePath $OutputPath -ExpectedChecksum $ExpectedChecksum) {
            Write-Success "Downloaded and verified $(Split-Path $OutputPath -Leaf)"
            return $true
        } else {
            Remove-Item -Path $OutputPath -Force -ErrorAction SilentlyContinue
            return $false
        }
    }
    catch {
        Write-Error "Failed to download $Url : $_"
        Remove-Item -Path $OutputPath -Force -ErrorAction SilentlyContinue
        return $false
    }
}

# Get dependency information
function Get-Dependencies {
    return @"
https://storage.googleapis.com/app-releases-production/pieces_cli/release/pieces_cli-1.17.1.tar.gz 97b0a61106d632c2d7e0a53f1e57babe29982135687e1b6476897a81369a6b8f
https://files.pythonhosted.org/packages/e3/52/6ad8f63ec8da1bf40f96996d25d5b650fdd38f5975f8c813732c47388f18/aenum-3.1.16-py3-none-any.whl 9035092855a98e41b66e3d0998bd7b96280e85ceb3a04cc035636138a1943eaf
https://files.pythonhosted.org/packages/ee/67/531ea369ba64dcff5ec9c3402f9f51bf748cec26dde048a2f973a4eea7f5/annotated_types-0.7.0.tar.gz aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89
https://files.pythonhosted.org/packages/f1/b4/636b3b65173d3ce9a38ef5f0522789614e590dab6a8d505340a4efe4c567/anyio-4.10.0.tar.gz 3f3fae35c96039744587aa5b8371e7e8e603c0702999535961dd336026973ba6
https://files.pythonhosted.org/packages/5a/b0/1367933a8532ee6ff8d63537de4f1177af4bff9f3e829baf7331f595bb24/attrs-25.3.0.tar.gz 75d7cefc7fb576747b2c81b4442d4d4a1ce0900973527c011d1030fd3bf4af1b
https://files.pythonhosted.org/packages/60/6c/8ca2efa64cf75a977a0d7fac081354553ebe483345c734fb6b6515d96bbc/click-8.2.1.tar.gz 27c491cc05d968d271d5a1db13e3b5a184636d9d930f148c50b038f0d0646202
https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz 4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1
https://files.pythonhosted.org/packages/06/94/82699a10bca87a5556c9c59b5963f2d039dbd239f25bc2a63907a05a14cb/httpcore-1.0.9.tar.gz 6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8
https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01324ee087459e112ebb7224f646c0b5023f5e79e9956/httpx-0.28.1.tar.gz 75e98c5f16b0f35b567856f597f06ff2270a374470a5c2392242528e3e3e42fc
https://files.pythonhosted.org/packages/6e/fa/66bd985dd0b7c109a3bcb89272ee0bfb7e2b4d06309ad7b38ff866734b2a/httpx_sse-0.4.1.tar.gz 8f44d34414bc7b21bf3602713005c5df4917884f76072479b21f68befa4ea26e
https://files.pythonhosted.org/packages/f1/70/7703c29685631f5a7590aa73f1f1d3fa9a380e654b86af429e0934a32f7d/idna-3.10.tar.gz 12f65c9b470abda6dc35cf8e63cc574b1c52b11df2c86030af0ac09b01b13ea9
https://files.pythonhosted.org/packages/d5/00/a297a868e9d0784450faa7365c2172a7d6110c763e30ba861867c32ae6a9/jsonschema-4.25.0.tar.gz e63acf5c11762c0e6672ffb61482bdf57f0876684d8d249c0fe2d730d48bc55f
https://files.pythonhosted.org/packages/bf/ce/46fbd9c8119cfc3581ee5643ea49464d168028cfb5caff5fc0596d0cf914/jsonschema_specifications-2025.4.1.tar.gz 630159c9f4dbea161a6a2205c3011cc4f18ff381b189fff48bb39b9bf26ae608
https://files.pythonhosted.org/packages/5b/f5/4ec618ed16cc4f8fb3b701563655a69816155e79e24a17b651541804721d/markdown_it_py-4.0.0.tar.gz cb0a2b4aa34f932c007117b194e945bd74e0ec24133ceb5bac59009cda1cb9f3
https://files.pythonhosted.org/packages/3a/f5/9506eb5578d5bbe9819ee8ba3198d0ad0e2fbe3bab8b257e4131ceb7dfb6/mcp-1.11.0.tar.gz 49a213df56bb9472ff83b3132a4825f5c8f5b120a90246f08b0dac6bedac44c8
https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba
https://files.pythonhosted.org/packages/fe/8b/3c73abc9c759ecd3f1f7ceff6685840859e8070c4d947c93fae71f6a0bf2/platformdirs-4.3.8.tar.gz 3d512d96e16bcb959a814c9f348431070822a6496326a4be0911c40b5a74c2bc
https://files.pythonhosted.org/packages/bb/6e/9d084c929dfe9e3bfe0c6a47e31f78a25c54627d64a66e884a8bf5474f1c/prompt_toolkit-3.0.51.tar.gz 931a162e3b27fc90c86f1b48bb1fb2c528c2761475e57c9c06de13311c7b54ed
https://files.pythonhosted.org/packages/00/dd/4325abf92c39ba8623b5af936ddb36ffcfe0beae70405d456ab1fb2f5b8c/pydantic-2.11.7.tar.gz d989c3c6cb79469287b1569f7447a17848c998458d49ebe294e975b9baf0f0db
https://files.pythonhosted.org/packages/ad/88/5f2260bdfae97aabf98f1778d43f69574390ad787afb646292a638c923d4/pydantic_core-2.33.2.tar.gz 7cb8bc3605c29176e1b105350d2e6474142d7c1bd1d9327c4a9bdb46bf827acc
https://files.pythonhosted.org/packages/68/85/1ea668bbab3c50071ca613c6ab30047fb36ab0da1b92fa8f17bbc38fd36c/pydantic_settings-2.10.1.tar.gz 06f0062169818d0f5524420a360d632d5857b83cffd4d42fe29597807a1614ee
https://files.pythonhosted.org/packages/b0/77/a5b8c569bf593b0140bde72ea885a803b82086995367bf2037de0159d924/pygments-2.19.2.tar.gz 636cb2477cec7f8952536970bc533bc43743542f70392ae026374600add5b887
https://files.pythonhosted.org/packages/30/23/2f0a3efc4d6a32f3b63cdff36cd398d9701d26cda58e3ab97ac79fb5e60d/pyperclip-1.9.0.tar.gz b7de0142ddc81bfc5c7507eea19da920b92252b548b96186caf94a5e2527d310
https://files.pythonhosted.org/packages/66/c0/0c8b6ad9f17a802ee498c46e004a0eb49bc148f2fd230864601a86dcf6db/python-dateutil-2.9.0.post0.tar.gz 37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3
https://files.pythonhosted.org/packages/f6/b0/4bc07ccd3572a2f9df7e6782f52b0c6c90dcbb803ac4a167702d7d0dfe1e/python_dotenv-1.1.1.tar.gz a8a6399716257f45be6a007360200409fce5cda2661e3dec71d23dc15f6189ab
https://files.pythonhosted.org/packages/f3/87/f44d7c9f274c7ee665a29b885ec97089ec5dc034c7f3fafa03da9e39a09e/python_multipart-0.0.20.tar.gz 8dd0cab45b8e23064ae09147625994d090fa46f5b0d1e13af944c331a7fa9d13
https://files.pythonhosted.org/packages/54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e
https://files.pythonhosted.org/packages/2f/db/98b5c277be99dd18bfd91dd04e1b759cad18d1a338188c936e92f921c7e2/referencing-0.36.2.tar.gz df2e89862cd09deabbdba16944cc3f10feb6b3e6f18e902f7cc25609a34775aa
https://files.pythonhosted.org/packages/ab/3a/0316b28d0761c6734d6bc14e770d85506c986c85ffb239e688eeaab2c2bc/rich-13.9.4.tar.gz 439594978a49a09530cff7ebc4b5c7103ef57baf48d5ea3184f21d9a2befa098
https://files.pythonhosted.org/packages/1e/d9/991a0dee12d9fc53ed027e26a26a64b151d77252ac477e22666b9688bc16/rpds_py-0.27.0.tar.gz 8b23cf252f180cda89220b378d917180f29d313cd6a07b2431c0d3b776aae86f
https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81
https://files.pythonhosted.org/packages/a2/87/a6771e1546d97e7e041b6ae58d80074f81b7d5121207425c964ddf5cfdbd/sniffio-1.3.1.tar.gz f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc
https://files.pythonhosted.org/packages/42/6f/22ed6e33f8a9e76ca0a412405f31abb844b779d52c5f96660766edcd737c/sse_starlette-3.0.2.tar.gz ccd60b5765ebb3584d0de2d7a6e4f745672581de4f5005ab31c3a25d10b52b3a
https://files.pythonhosted.org/packages/04/57/d062573f391d062710d4088fa1369428c38d51460ab6fedff920efef932e/starlette-0.47.2.tar.gz 6ae9aa5db235e4846decc1e7b79c4f346adf41e9777aebeb49dfd09bbd7023d8
https://files.pythonhosted.org/packages/98/5a/da40306b885cc8c09109dc2e1abd358d5684b1425678151cdaed4731c822/typing_extensions-4.14.1.tar.gz 38b39f4aeeab64884ce9f74c94263ef78f3c22467c8724005483154c26648d36
https://files.pythonhosted.org/packages/f8/b1/0c11f5058406b3af7609f121aaa6b609744687f1d158b3c3a5bf4cc94238/typing_inspection-0.4.1.tar.gz 6ae134cc0203c33377d43188d4064e9b357dba58cff3185f22924610e70a9d28
https://files.pythonhosted.org/packages/15/22/9ee70a2574a4f4599c47dd506532914ce044817c7752a79b6a51286319bc/urllib3-2.5.0.tar.gz 3fc47733c7e419d4bc3f6b3dc2b4f890bb743906a30d56ba4a5bfa4bbff92760
https://files.pythonhosted.org/packages/5e/42/e0e305207bb88c6b8d3061399c6a961ffe5fbb7e2aa63c9234df7259e9cd/uvicorn-0.35.0.tar.gz bc662f087f7cf2ce11a1d7fd70b90c9f98ef2e2831556dd078d131b96cc94a01
https://files.pythonhosted.org/packages/6c/63/53559446a878410fc5a5974feb13d31d78d752eb18aeba59c7fef1af7598/wcwidth-0.2.13.tar.gz 72ea0c06399eb286d978fdedb6923a9eb47e1c486ce63e9b4e64fc18303972b5
https://files.pythonhosted.org/packages/e6/30/fba0d96b4b5fbf5948ed3f4681f7da2f9f64512e1d303f94b4cc174c24a5/websocket_client-1.8.0.tar.gz 3239df9f44da632f96012472805d40a23281a991027ce11d2f45a6f24ac4c3da
"@
}

# Download and verify all dependencies
function Invoke-DownloadDependencies {
    param([string]$DownloadDir)

    Write-Info "Creating download directory: $DownloadDir"
    New-Item -Path $DownloadDir -ItemType Directory -Force | Out-Null

    # Parse and download each dependency
    $dependencies = Get-Dependencies
    $lines = $dependencies -split "`n" | Where-Object { $_.Trim() -ne "" }

    foreach ($line in $lines) {
        $parts = $line.Trim() -split " "
        if ($parts.Length -ge 2) {
            $url = $parts[0]
            $checksum = $parts[1]

            $filename = Split-Path $url -Leaf
            $outputPath = Join-Path $DownloadDir $filename

            # Skip if already downloaded and verified
            if ((Test-Path $outputPath) -and (Test-FileChecksum -FilePath $outputPath -ExpectedChecksum $checksum)) {
                Write-Info "Already have verified $filename"
                continue
            }

            # Download and verify
            if (!(Invoke-SecureDownload -Url $url -OutputPath $outputPath -ExpectedChecksum $checksum)) {
                Write-Error "Failed to download and verify $filename"
                return $false
            }
        }
    }

    Write-Success "All dependencies downloaded and verified!"
    return $true
}

# Install packages offline using pip with no-deps and local files
function Install-PackagesOffline {
    param(
        [string]$DownloadDir,
        [string]$PipPath
    )

    Write-Info "Installing packages from verified downloads..."

    # Parse and install each dependency
    $dependencies = Get-Dependencies
    $lines = $dependencies -split "`n" | Where-Object { $_.Trim() -ne "" }

    foreach ($line in $lines) {
        $parts = $line.Trim() -split " "
        if ($parts.Length -ge 2) {
            $url = $parts[0]
            $filename = Split-Path $url -Leaf
            $packagePath = Join-Path $DownloadDir $filename

            if (!(Test-Path $packagePath)) {
                Write-Error "Package file not found: $packagePath"
                return $false
            }

            Write-Info "Installing $filename..."

            # Install with no dependencies flag to prevent pip from accessing PyPI
            try {
                & $PipPath install $packagePath --no-deps --force-reinstall --quiet
                if ($LASTEXITCODE -ne 0) { 
                    throw "pip install failed with exit code $LASTEXITCODE" 
                }
            }
            catch {
                Write-Error "Failed to install $filename : $_"
                return $false
            }
        }
    }

    Write-Success "All packages installed successfully!"
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

    # Step 1: Check system requirements
    Write-Info "Checking system requirements..."

    # PowerShell should have Invoke-WebRequest and Get-FileHash built-in
    # These are required for secure downloads and checksum verification
    try {
        Get-Command Invoke-WebRequest -ErrorAction Stop | Out-Null
        Get-Command Get-FileHash -ErrorAction Stop | Out-Null
    }
    catch {
        Write-Error "Required PowerShell cmdlets not available (Invoke-WebRequest, Get-FileHash)"
        Write-Error "Please ensure you're running PowerShell 3.0 or later"
        return
    }

    # Step 2: Check if running as Administrator/root
    if (Test-Administrator) {
        Write-Warning "You appear to be running this script as Administrator/root."
        Write-Warning "This may cause the installation to be inaccessible to non-admin users."
        $continue = Read-Host "Continue anyway? [y/N]"
        if ($continue -notmatch '^[yY]([eE][sS])?$') {
            Write-Info "Installation cancelled."
            return
        }
    }

    # Step 3: Find Python executable
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

    # Step 4: Set installation directory
    $homeDir = Get-HomeDirectory
    $installDir = Join-Path $homeDir ".pieces-cli"
    $venvDir = Join-Path $installDir "venv"

    Write-Info "Installation directory: $installDir"

    # Create installation directory
    if (!(Test-Path $installDir)) {
        New-Item -Path $installDir -ItemType Directory | Out-Null
    }

    # Step 5: Create virtual environment
    Write-Info "Creating virtual environment..."
    if (Test-Path $venvDir) {
        Write-Warning "Virtual environment already exists. Removing old environment..."
        Remove-Item -Path $venvDir -Recurse -Force
    }

    # Handle python command properly (could be "python" or "py -3.11")
    try {
        if ($pythonCmd -contains ' ') {
            $cmdParts = $pythonCmd.Split(' ')
            & $cmdParts[0] $cmdParts[1..($cmdParts.Length-1)] -m venv $venvDir
        } else {
            & $pythonCmd -m venv $venvDir
        }
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed with exit code $LASTEXITCODE" }
    }
    catch {
        if (Test-Path $venvDir) { 
            try { Remove-Item -Path $venvDir -Recurse -Force -ErrorAction SilentlyContinue } catch { }
        }
        Write-Error "Failed to create virtual environment: $_"
        return
    }

    Write-Success "Virtual environment created successfully."

    # Use venv's pip - different paths for Windows vs Unix
    if (Test-Windows) {
        $venvPip = Join-Path $venvDir "Scripts\pip.exe"
    } else {
        $venvPip = Join-Path $venvDir "bin/pip"
    }

    # Verify pip exists
    if (!(Test-Path $venvPip)) {
        Write-Error "Pip executable not found at: $venvPip"
        Write-Error "Virtual environment may be corrupted. Please try again."
        return
    }

    # Step 6a: Download all dependencies securely
    $downloadDir = Join-Path $installDir "downloads"
    Write-Info "Downloading and verifying all dependencies"

    if (!(Invoke-DownloadDependencies -DownloadDir $downloadDir)) {
        Write-Error "Failed to download dependencies."
        Write-Error "Please check your internet connection and try again."
        return
    }

    if (!(Install-PackagesOffline -DownloadDir $downloadDir -PipPath $venvPip)) {
        Write-Error "Failed to install packages offline."
        Write-Error "Installation may be corrupted, please try again."
        return
    }

    Write-Success "Pieces CLI installed successfully!"

    # Clean up downloads after successful installation
    Write-Info "Cleaning up download cache..."
    Remove-Item -Path $downloadDir -Recurse -Force -ErrorAction SilentlyContinue

    # Step 7: Create wrapper script
    Write-Info "Creating wrapper script..."

    if (Test-Windows) {
        $wrapperScript = Join-Path $installDir "pieces.cmd"
        $wrapperContent = @"
@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "PIECES_EXE=%VENV_DIR%\Scripts\pieces.exe"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Error: Pieces CLI virtual environment not found at "%VENV_DIR%" >&2
    echo Please reinstall Pieces CLI. >&2
    exit /b 1
)

REM Check if pieces executable exists
if not exist "%PIECES_EXE%" (
    echo Error: Pieces CLI executable not found at "%PIECES_EXE%" >&2
    echo Please reinstall Pieces CLI. >&2
    exit /b 1
)

REM Execute pieces.exe and preserve exit code
"%PIECES_EXE%" %*
exit /b %ERRORLEVEL%
"@
    } else {
        $wrapperScript = Join-Path $installDir "pieces"
        $wrapperContent = @"
#!/bin/sh
# Pieces CLI Wrapper Script
set -e  # Exit on error

# Get the real path of the script (handle symlinks)
# Note: readlink -f doesn't work on macOS, so we try multiple methods
if [ -L "`$0" ]; then
    if command -v realpath >/dev/null 2>&1; then
        SCRIPT_PATH="`$(realpath "`$0")"
    elif command -v readlink >/dev/null 2>&1; then
        # Try GNU readlink -f first, fall back to basic readlink
        SCRIPT_PATH="`$(readlink -f "`$0" 2>/dev/null || readlink "`$0")"
    else
        # Fallback: just use the symlink as-is
        SCRIPT_PATH="`$0"
    fi
else
    SCRIPT_PATH="`$0"
fi

# Get script directory - handle spaces and special characters
SCRIPT_DIR="`$(cd "`$(dirname "`$SCRIPT_PATH")" && pwd)"
VENV_DIR="`$SCRIPT_DIR/venv"
PIECES_EXECUTABLE="`$VENV_DIR/bin/pieces"

# Check if virtual environment exists
if [ ! -d "`$VENV_DIR" ]; then
    echo "Error: Pieces CLI virtual environment not found at '`$VENV_DIR'" >&2
    echo "Please reinstall Pieces CLI." >&2
    exit 1
fi

# Check if pieces executable exists
if [ ! -f "`$PIECES_EXECUTABLE" ]; then
    echo "Error: Pieces CLI executable not found at '`$PIECES_EXECUTABLE'" >&2
    echo "Please reinstall Pieces CLI." >&2
    exit 1
fi

# Run pieces directly from venv without activation
# exec replaces the shell process with pieces, preserving signals and exit codes
exec "`$PIECES_EXECUTABLE" "`$@"
"@
    }

    Set-Content -Path $wrapperScript -Value $wrapperContent

    # Make executable on Unix-like systems
    if (!(Test-Windows)) {
        chmod +x $wrapperScript
    }

    Write-Success "Wrapper script created at: $wrapperScript"

    # Step 8: Configure PowerShell
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

    # Step 9: Final instructions
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
