#!/bin/sh
#
# Pieces CLI Installation Script
# This script installs the Pieces CLI tool in a virtual environment
# and optionally sets up shell completion.
#
# POSIX compliant shell script - works with sh, bash, zsh, dash, etc.
#

echo "Welcome to the Pieces CLI Installer!"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
  echo "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
  echo "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo "${RED}[ERROR]${NC} $1"
}

# Check if a Python version meets minimum requirements (3.11+)
check_python_version() {
  python_cmd="$1"
  if "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Verify SHA256 checksum of a file
verify_checksum() {
  file_path="$1"
  expected_checksum="$2"

  if [ ! -f "$file_path" ]; then
    print_error "File not found: $file_path"
    return 1
  fi

  # Try different SHA256 commands based on availability
  if command -v sha256sum >/dev/null; then
    actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)
  elif command -v shasum >/dev/null; then
    actual_checksum=$(shasum -a 256 "$file_path" | cut -d' ' -f1)
  elif command -v openssl >/dev/null; then
    actual_checksum=$(openssl dgst -sha256 "$file_path" | cut -d' ' -f2)
  else
    print_error "No SHA256 utility found (sha256sum, shasum, or openssl required)"
    return 1
  fi

  if [ "$actual_checksum" = "$expected_checksum" ]; then
    return 0
  else
    print_error "Checksum verification failed for $file_path"
    print_error "Expected: $expected_checksum"
    print_error "Actual:   $actual_checksum"
    return 1
  fi
}

# Download a file with curl and verify its checksum
secure_download() {
  url="$1"
  output_path="$2"
  expected_checksum="$3"

  print_info "Downloading $(basename "$output_path")..."

  # Download with curl
  if ! curl -fsSL "$url" -o "$output_path"; then
    print_error "Failed to download $url"
    return 1
  fi

  # Verify checksum
  if ! verify_checksum "$output_path" "$expected_checksum"; then
    rm -f "$output_path"
    return 1
  fi

  print_success "Downloaded and verified $(basename "$output_path")"
  return 0
}

# Parse dependency information from embedded data
get_dependencies() {
  # Dependencies with URLs and checksums
  cat <<'EOF'
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
EOF
}

# Download and verify all dependencies
download_dependencies() {
  download_dir="$1"

  print_info "Creating download directory: $download_dir"
  mkdir -p "$download_dir"

  # Download each dependency
  get_dependencies | while read -r url checksum; do
    if [ -z "$url" ] || [ -z "$checksum" ]; then
      continue
    fi

    filename=$(basename "$url")
    output_path="$download_dir/$filename"

    # Skip if already downloaded and verified
    if [ -f "$output_path" ] && verify_checksum "$output_path" "$checksum" >/dev/null 2>&1; then
      print_info "Already have verified $(basename "$output_path")"
      continue
    fi

    # Download and verify
    if ! secure_download "$url" "$output_path" "$checksum"; then
      print_error "Failed to download and verify $filename"
      return 1
    fi
  done

  print_success "All dependencies downloaded and verified!"
  return 0
}

# Install packages offline using pip with no-deps and local files
install_packages_offline() {
  download_dir="$1"

  print_info "Installing packages from verified downloads..."

  # Install in dependency order (dependencies first, then main package)
  get_dependencies | while read -r url checksum; do
    if [ -z "$url" ] || [ -z "$checksum" ]; then
      continue
    fi

    filename=$(basename "$url")
    package_path="$download_dir/$filename"

    if [ ! -f "$package_path" ]; then
      print_error "Package file not found: $package_path"
      return 1
    fi

    print_info "Installing $(basename "$package_path")..."

    # Install with no dependencies flag to prevent pip from accessing PyPI
    if ! pip install "$package_path" --no-deps --force-reinstall --quiet; then
      print_error "Failed to install $filename"
      return 1
    fi
  done

  print_success "All packages installed successfully!"
  return 0
}

# Find the best Python executable available
find_python() {
  # Try to find Python in order of preference
  for python_version in python3.12 python3.11 python3 python; do
    if command -v "$python_version" >/dev/null; then
      if check_python_version "$python_version"; then
        echo "$python_version"
        return 0
      fi
    fi
  done
  return 1
}

# Detect user's shell
detect_shell() {
  if [ -n "$ZSH_VERSION" ]; then
    echo "zsh"
  elif [ -n "$BASH_VERSION" ]; then
    echo "bash"
  elif [ -n "$FISH_VERSION" ]; then
    echo "fish"
  else
    # Fallback to checking $SHELL
    case "$SHELL" in
    */zsh) echo "zsh" ;;
    */bash) echo "bash" ;;
    */fish) echo "fish" ;;
    *) echo "unknown" ;;
    esac
  fi
}

# Setup completion for a specific shell
setup_completion() {
  shell_type="$1"

  case "$shell_type" in
  "bash")
    config_file="$HOME/.bashrc"
    completion_cmd='eval "$(pieces completion bash)"'
    ;;
  "zsh")
    config_file="$HOME/.zshrc"
    completion_cmd='eval "$(pieces completion zsh)"'
    ;;
  "fish")
    config_file="$HOME/.config/fish/config.fish"
    completion_cmd='pieces completion fish | source'
    # Create fish config directory if it doesn't exist
    mkdir -p "$(dirname "$config_file")"
    ;;
  *)
    print_warning "Unknown shell type: $shell_type. Skipping completion setup."
    return 1
    ;;
  esac

  # Check if completion is already configured
  if [ -f "$config_file" ] && grep -q "pieces completion" "$config_file"; then
    print_info "Completion already configured in $config_file"
    return 0
  fi

  # Add completion to config file
  echo "$completion_cmd" >>"$config_file"
  print_success "Added completion to $config_file"

  return 0
}

# Setup PATH for a specific shell
setup_path() {
  shell_type="$1"
  install_dir="$2"

  case "$shell_type" in
  "bash")
    config_file="$HOME/.bashrc"
    path_cmd="export PATH=\"$install_dir:\$PATH\""
    ;;
  "zsh")
    config_file="$HOME/.zshrc"
    path_cmd="export PATH=\"$install_dir:\$PATH\""
    ;;
  "fish")
    config_file="$HOME/.config/fish/config.fish"
    path_cmd="set -gx PATH $install_dir \$PATH"
    # Create fish config directory if it doesn't exist
    mkdir -p "$(dirname "$config_file")"
    ;;
  *)
    print_warning "Unknown shell type: $shell_type. Skipping PATH setup."
    return 1
    ;;
  esac

  # Check if PATH is already configured
  if [ -f "$config_file" ] && grep -q "$install_dir" "$config_file"; then
    print_info "PATH already configured in $config_file"
    return 0
  fi

  # Add PATH to config file
  echo "$path_cmd" >>"$config_file"
  print_success "Added PATH to $config_file"

  return 0
}

# Check if a shell is available on the system
check_shell_available() {
  shell_type="$1"

  case "$shell_type" in
  "bash")
    command -v bash >/dev/null && [ -f "$HOME/.bashrc" -o ! -f "$HOME/.bash_profile" ]
    ;;
  "zsh")
    command -v zsh >/dev/null
    ;;
  "fish")
    command -v fish >/dev/null
    ;;
  *)
    return 1
    ;;
  esac
}

# Cleanup function for trap
cleanup() {
  # Deactivate virtual environment if active
  deactivate 2>/dev/null || true

  # Remove partial installations on failure
  if [ -n "$CLEANUP_ON_EXIT" ] && [ -d "$INSTALL_DIR" ]; then
    print_warning "Cleaning up partial installation..."
    rm -rf "$INSTALL_DIR"
  fi
}

# Main installation function
main() {
  # Set up trap for cleanup on exit
  trap cleanup EXIT INT TERM

  print_info "Starting Pieces CLI installation..."

  # Step 1: Check for required tools
  print_info "Checking system requirements..."

  # Check for curl
  if ! command -v curl >/dev/null; then
    print_error "curl is required for package downloads but not found."
    print_error "Please install curl and try again:"
    print_error "  Ubuntu/Debian: sudo apt-get install curl"
    print_error "  RHEL/CentOS/Fedora: sudo yum install curl"
    print_error "  macOS: curl should be pre-installed, or use 'brew install curl'"
    exit 1
  fi

  # Check for SHA256 utilities
  if ! command -v sha256sum >/dev/null && ! command -v shasum >/dev/null && ! command -v openssl >/dev/null; then
    print_error "No SHA256 utility found for checksum verification."
    print_error "Please install one of: sha256sum, shasum, or openssl"
    exit 1
  fi

  # Step 2: Find Python executable
  print_info "Locating Python executable..."
  PYTHON_CMD=$(find_python)

  if [ $? -ne 0 ] || [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3.11+ is required but not found on your system."
    print_error "Please install Python 3.11 or higher and ensure it's in your PATH."
    print_error "You can download Python from: https://www.python.org/downloads/"
    exit 1
  fi

  # Get Python version for display
  PYTHON_VERSION=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
  print_success "Found Python: $PYTHON_CMD ($PYTHON_VERSION)"

  # Step 3: Set installation directory
  INSTALL_DIR="$HOME/.pieces-cli"
  VENV_DIR="$INSTALL_DIR/venv"
  CLEANUP_ON_EXIT="true" # Enable cleanup on failure

  print_info "Installation directory: $INSTALL_DIR"

  # Create installation directory
  if ! mkdir -p "$INSTALL_DIR"; then
    print_error "Failed to create installation directory: $INSTALL_DIR"
    print_error "Please check permissions and try again."
    exit 1
  fi

  # Step 4: Create virtual environment
  print_info "Creating virtual environment..."
  if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf "$VENV_DIR"
  fi

  if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
    print_error "Failed to create virtual environment."
    print_error "Please ensure you have the 'venv' module available."
    print_error "On some systems, you may need to install python3-venv package:"
    print_error "  Ubuntu/Debian: sudo apt-get install python3-venv"
    print_error "  Fedora: sudo dnf install python3-venv"
    # Clean up partial venv if it exists
    [ -d "$VENV_DIR" ] && rm -rf "$VENV_DIR"
    exit 1
  fi

  print_success "Virtual environment created successfully."

  print_info "Preparing installation of Pieces CLI..."

  # Activate virtual environment with security checks
  ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
  if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    print_error "Failed to find activation script at $ACTIVATE_SCRIPT"
    print_error "Virtual environment may be corrupted."
    exit 1
  fi

  # Verify the activation script contains expected content for safety
  if ! grep -q "VIRTUAL_ENV" "$ACTIVATE_SCRIPT" || ! grep -q "deactivate" "$ACTIVATE_SCRIPT"; then
    print_error "Activation script appears to be corrupted or malicious."
    print_error "Expected virtual environment activation script not found."
    exit 1
  fi

  # Source the activation script using absolute path
  . "$ACTIVATE_SCRIPT"

  # Upgrade pip first (basic upgrade only, no network access for packages)
  print_info "Upgrading pip..."
  if ! pip install --upgrade pip --quiet; then
    print_warning "Failed to upgrade pip, continuing with existing version..."
  fi

  # Step 5a: Download all dependencies
  DOWNLOAD_DIR="$INSTALL_DIR/downloads"
  print_info "Downloading and verifying all dependencies with checksum validation..."

  if ! download_dependencies "$DOWNLOAD_DIR"; then
    print_error "Failed to download dependencies."
    print_error "Please check your internet connection and try again."
    deactivate 2>/dev/null || true
    exit 1
  fi

  # Step 5b: Install packages offline
  print_info "Installing packages offline from verified downloads..."

  if ! install_packages_offline "$DOWNLOAD_DIR"; then
    print_error "Failed to install packages offline."
    print_error "Installation may be corrupted, please try again."
    deactivate 2>/dev/null || true
    exit 1
  fi

  print_success "Pieces CLI installed successfully with verified packages!"

  # Clean up downloads after successful installation
  print_info "Cleaning up download cache..."
  rm -rf "$DOWNLOAD_DIR"

  # Disable cleanup on exit since installation succeeded
  CLEANUP_ON_EXIT=""

  # Step 6: Create wrapper script
  # Used to run pieces-cli from the command line without activating the virtual environment
  print_info "Creating wrapper script..."
  WRAPPER_SCRIPT="$INSTALL_DIR/pieces"

  cat >"$WRAPPER_SCRIPT" <<'EOF'
#!/bin/sh
# Pieces CLI Wrapper Script
set -e  # Exit on error

# Get the real path of the script (handle symlinks)
# Note: readlink -f doesn't work on macOS, so we try multiple methods
if [ -L "$0" ]; then
    if command -v realpath >/dev/null 2>&1; then
        SCRIPT_PATH="$(realpath "$0")"
    elif command -v readlink >/dev/null 2>&1; then
        # Try GNU readlink -f first, fall back to basic readlink
        SCRIPT_PATH="$(readlink -f "$0" 2>/dev/null || readlink "$0")"
    else
        # Fallback: just use the symlink as-is
        SCRIPT_PATH="$0"
    fi
else
    SCRIPT_PATH="$0"
fi

# Get script directory - handle spaces and special characters
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PIECES_EXECUTABLE="$VENV_DIR/bin/pieces"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Pieces CLI virtual environment not found at '$VENV_DIR'" >&2
    echo "Please reinstall Pieces CLI." >&2
    exit 1
fi

# Check if pieces executable exists
if [ ! -f "$PIECES_EXECUTABLE" ]; then
    echo "Error: Pieces CLI executable not found at '$PIECES_EXECUTABLE'" >&2
    echo "Please reinstall Pieces CLI." >&2
    exit 1
fi

# Run pieces directly from venv without activation
# exec replaces the shell process with pieces, preserving signals and exit codes
exec "$PIECES_EXECUTABLE" "$@"
EOF

  chmod +x "$WRAPPER_SCRIPT"
  print_success "Wrapper script created at: $WRAPPER_SCRIPT"

  # Step 7: Configure shells
  print_info "Configuring shell integration..."

  # Check if already in PATH
  if echo "$PATH" | grep -q "$INSTALL_DIR"; then
    print_info "Pieces CLI directory already in PATH."
  fi

  # Available shells to configure
  available_shells=""
  for shell in bash zsh fish; do
    if check_shell_available "$shell"; then
      available_shells="$available_shells $shell"
    fi
  done

  if [ -z "$available_shells" ]; then
    print_warning "No supported shells found. You can manually add to PATH later."
    print_info "Add this to your shell config: export PATH=\"$INSTALL_DIR:\$PATH\""
  else
    echo ""
    print_info "Found the following shells: $available_shells"
    echo ""

    # Ask for each shell individually
    for shell in $available_shells; do
      echo "--- $shell configuration ---"

      # Ask about PATH setup
      printf "Add Pieces CLI to PATH in $shell? [Y/n]: "
      read -r add_path
      case "$add_path" in
      [nN] | [nN][oO])
        print_info "Skipping PATH setup for $shell"
        ;;
      *)
        print_info "Setting up PATH for $shell..."
        setup_path "$shell" "$INSTALL_DIR"
        ;;
      esac

      # Ask about completion setup
      printf "Enable shell completion for $shell? [Y/n]: "
      read -r enable_completion
      case "$enable_completion" in
      [nN] | [nN][oO])
        print_info "Skipping completion setup for $shell"
        ;;
      *)
        print_info "Setting up completion for $shell..."
        setup_completion "$shell"
        ;;
      esac

      echo ""
    done
  fi

  # Step 8: Final instructions
  echo ""
  print_success "Installation completed successfully!"
  echo ""
  print_info "To start using Pieces CLI:"

  # Check if any shells were configured
  if [ -n "$available_shells" ]; then
    print_info "  1. Restart your terminal or reload your shell configuration:"
    for shell in $available_shells; do
      case "$shell" in
      "bash")
        print_info "     For bash: source ~/.bashrc"
        ;;
      "zsh")
        print_info "     For zsh: source ~/.zshrc"
        ;;
      "fish")
        print_info "     For fish: source ~/.config/fish/config.fish"
        ;;
      esac
    done
  else
    print_info "  1. Add Pieces CLI to your PATH manually:"
    print_info "     export PATH=\"$INSTALL_DIR:\$PATH\""
  fi

  print_info "  2. Verify installation: pieces version"
  print_info "  3. Get help: pieces help"
  echo ""
  print_info "Alternative: You can always run the CLI directly:"
  print_info "  $INSTALL_DIR/pieces version"
  echo ""
  print_info "Make sure PiecesOS is installed and running:"
  print_info "  Download from: https://pieces.app/"
  print_info "  Documentation: https://docs.pieces.app/"
  echo ""
  print_success "Security Features Enabled:"
  print_info "  ✓ All packages downloaded with checksum verification"
  print_info "  ✓ No direct PyPI access during installation"
  print_info "  ✓ Offline package installation from verified sources"
  print_info "  ✓ SHA256 integrity verification for all dependencies"
  echo ""
  print_info "Shell completion can be enabled later with:"
  print_info "  pieces completion [bash|zsh|fish]"
  echo ""
  print_info "If you encounter any issues, visit:"
  print_info "  https://github.com/pieces-app/cli-agent"
  echo ""
}

# Check if running as root
if [ "$(id -u)" = "0" ]; then
  print_warning "You appear to be running this script as root."
  print_warning "This may cause the installation to be inaccessible to other users."
  printf "Continue anyway? [y/N]: "
  read -r continue_as_root
  case "$continue_as_root" in
  [yY] | [yY][eE][sS]) ;;
  *)
    print_info "Installation cancelled."
    exit 1
    ;;
  esac
fi

# Run main installation
main "$@"
