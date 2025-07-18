#!/bin/sh
# Pieces CLI Secure Installer
# This script downloads and verifies the Pieces CLI installation script before execution

set -e

# Configuration
REPO="pieces-app/cli-agent"
BASE_URL="https://github.com/${REPO}/releases/latest/download"
INSTALL_SCRIPT="install_pieces_cli.sh"
CHECKSUM_FILE="${INSTALL_SCRIPT}.sha256"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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
    echo "${RED}[ERROR]${NC} $1" >&2
}

cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}

verify_checksum() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum -c "$1"
    elif command -v shasum >/dev/null 2>&1; then
        # macOS fallback
        shasum -a 256 -c "$1"
    else
        print_warning "No checksum verification tool found (sha256sum or shasum)"
        print_warning "Cannot verify installation script integrity"
        printf "Continue without verification? [y/N] "
        read -r response
        case "$response" in
            [yY][eE][sS]|[yY])
                return 0
                ;;
            *)
                return 1
                ;;
        esac
    fi
}

# Main installation process
main() {
    echo "Pieces CLI Secure Installer"
    echo "=========================="
    echo ""
    
    # Set up cleanup trap
    trap cleanup EXIT INT TERM
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'pieces-install')
    if [ ! -d "$TEMP_DIR" ]; then
        print_error "Failed to create temporary directory"
        exit 1
    fi
    
    cd "$TEMP_DIR"
    
    # Download installation script
    print_info "Downloading installation script..."
    if ! curl -fsSL "${BASE_URL}/${INSTALL_SCRIPT}" -o "$INSTALL_SCRIPT"; then
        print_error "Failed to download installation script"
        print_error "URL: ${BASE_URL}/${INSTALL_SCRIPT}"
        exit 1
    fi
    
    # Download checksum
    print_info "Downloading checksum file..."
    if ! curl -fsSL "${BASE_URL}/${CHECKSUM_FILE}" -o "$CHECKSUM_FILE"; then
        print_error "Failed to download checksum file"
        print_error "URL: ${BASE_URL}/${CHECKSUM_FILE}"
        exit 1
    fi
    
    # Verify checksum
    print_info "Verifying installation script integrity..."
    if ! verify_checksum "$CHECKSUM_FILE"; then
        print_error "Checksum verification failed!"
        print_error "The installation script may have been tampered with."
        print_error "Please report this issue to: security@pieces.app"
        exit 1
    fi
    
    print_success "Checksum verification passed!"
    
    # Optional: Allow user to review the script
    printf "Would you like to review the installation script before running? [y/N] "
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            ${PAGER:-less} "$INSTALL_SCRIPT"
            printf "Proceed with installation? [y/N] "
            read -r response
            case "$response" in
                [yY][eE][sS]|[yY])
                    ;;
                *)
                    print_info "Installation cancelled by user"
                    exit 0
                    ;;
            esac
            ;;
    esac
    
    # Execute the verified installation script
    print_info "Starting Pieces CLI installation..."
    echo ""
    
    # Pass through any arguments to the installation script
    sh "$INSTALL_SCRIPT" "$@"
}

# Run main function
main "$@"