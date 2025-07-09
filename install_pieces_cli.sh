#!/bin/sh
#
# Pieces CLI Installation Script
# This script installs the Pieces CLI tool in a virtual environment
# and optionally sets up shell completion.
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

# Wrapper around 'which' and 'command -v', tries which first, then falls back to command -v
_pieces_which() {
  which "$1" 2>/dev/null || command -v "$1" 2>/dev/null
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

# Find the best Python executable available
find_python() {
  # Try to find Python in order of preference
  for python_version in python3.12 python3.11 python3 python; do
    if _pieces_which "$python_version" >/dev/null; then
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
    _pieces_which bash >/dev/null && [ -f "$HOME/.bashrc" -o ! -f "$HOME/.bash_profile" ]
    ;;
  "zsh")
    _pieces_which zsh >/dev/null
    ;;
  "fish")
    _pieces_which fish >/dev/null
    ;;
  *)
    return 1
    ;;
  esac
}

# Main installation function
main() {
  print_info "Starting Pieces CLI installation..."

  # Step 1: Find Python executable
  print_info "Locating Python executable..."
  PYTHON_CMD=$(find_python)

  if [ $? -ne 0 ] || [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3.11+ is required but not found on your system."
    print_error "Please install Python 3.11 or higher and ensure it's in your PATH."
    print_error "You can download Python from: https://www.python.org/downloads/"
    exit 1
  fi

  # Get Python version for display
  PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1)
  print_success "Found Python: $PYTHON_CMD ($PYTHON_VERSION)"

  # Step 2: Set installation directory
  INSTALL_DIR="$HOME/.pieces-cli"
  VENV_DIR="$INSTALL_DIR/venv"

  print_info "Installation directory: $INSTALL_DIR"

  # Create installation directory
  mkdir -p "$INSTALL_DIR"

  # Step 3: Create virtual environment
  print_info "Creating virtual environment..."
  if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf "$VENV_DIR"
  fi

  "$PYTHON_CMD" -m venv "$VENV_DIR"
  if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment."
    print_error "Please ensure you have the 'venv' module available."
    exit 1
  fi

  print_success "Virtual environment created successfully."

  # Step 4: Activate virtual environment and install pieces-cli
  print_info "Installing Pieces CLI..."

  # Activate virtual environment
  . "$VENV_DIR/bin/activate"

  # Upgrade pip first
  pip install --upgrade pip

  # Install pieces-cli
  pip install pieces-cli
  if [ $? -ne 0 ]; then
    print_error "Failed to install pieces-cli."
    print_error "Please check your internet connection and try again."
    exit 1
  fi

  print_success "Pieces CLI installed successfully!"

  # Step 5: Create wrapper script
  # Used to run pieces-cli from the command line without activating the virtual environment
  print_info "Creating wrapper script..."
  WRAPPER_SCRIPT="$INSTALL_DIR/pieces"

  cat >"$WRAPPER_SCRIPT" <<'EOF'
#!/bin/sh
# Pieces CLI Wrapper Script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PIECES_EXECUTABLE="$VENV_DIR/bin/pieces"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Pieces CLI virtual environment not found at $VENV_DIR"
    echo "Please reinstall Pieces CLI."
    exit 1
fi

# Check if pieces executable exists
if [ ! -f "$PIECES_EXECUTABLE" ]; then
    echo "Error: Pieces CLI executable not found at $PIECES_EXECUTABLE"
    echo "Please reinstall Pieces CLI."
    exit 1
fi

# Run pieces directly from venv without activation
exec "$PIECES_EXECUTABLE" "$@"
EOF

  chmod +x "$WRAPPER_SCRIPT"
  print_success "Wrapper script created at: $WRAPPER_SCRIPT"

  # Step 6: Configure shells
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

  # Step 7: Final instructions
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
  print_info "Shell completion can be enabled later with:"
  print_info "  pieces completion [bash|zsh|fish]"
  echo ""
  print_info "If you encounter any issues, visit:"
  print_info "  https://github.com/pieces-app/cli-agent"

  deactivate 2>/dev/null || true
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
