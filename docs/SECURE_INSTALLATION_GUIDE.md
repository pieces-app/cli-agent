# Secure Installation Guide for Pieces CLI

This guide provides detailed instructions for securely installing the Pieces CLI using various methods, ordered by security level.

## Table of Contents

1. [Security Overview](#security-overview)
2. [Installation Methods](#installation-methods)
   - [Method 1: Package Managers (Most Secure)](#method-1-package-managers-most-secure)
   - [Method 2: Verified Script Installation](#method-2-verified-script-installation)
   - [Method 3: pip with Hash Verification](#method-3-pip-with-hash-verification)
   - [Method 4: Docker Container](#method-4-docker-container)
   - [Method 5: Binary Releases](#method-5-binary-releases)
3. [Verification Steps](#verification-steps)
4. [Post-Installation Security](#post-installation-security)
5. [Troubleshooting](#troubleshooting)

## Security Overview

### Why Security Matters

Recent statistics show:
- **1,300% increase** in supply chain attacks
- **500,000+ malicious packages** on PyPI since 2023
- **100% of organizations** experienced supply chain attacks in 2024

### Our Security Measures

- ✅ SHA256 checksums for all releases
- ✅ Sigstore/Cosign signatures
- ✅ Trusted Publisher on PyPI
- ✅ Virtual environment isolation
- ✅ Regular security audits

## Installation Methods

### Method 1: Package Managers (Most Secure)

Package managers provide the highest security through:
- Automatic signature verification
- Managed dependencies
- Easy updates

#### Homebrew (macOS/Linux)

```bash
# Install
brew install pieces-cli

# Verify installation
brew list pieces-cli

# Update
brew upgrade pieces-cli
```

#### Chocolatey (Windows)

```powershell
# Install (Admin PowerShell)
choco install pieces-cli

# Verify installation
choco list --local-only pieces-cli

# Update
choco upgrade pieces-cli
```

### Method 2: Verified Script Installation

Our secure installer automatically verifies checksums:

```bash
# Download secure installer
curl -fsSL https://github.com/pieces-app/cli-agent/releases/latest/download/secure-install.sh -o secure-install.sh

# Make executable
chmod +x secure-install.sh

# Run installer (will verify checksums automatically)
./secure-install.sh
```

#### Manual Verification Option

If you prefer to verify manually:

```bash
# Download files
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/install_pieces_cli.sh
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/install_pieces_cli.sh.sha256

# Verify checksum
sha256sum -c install_pieces_cli.sh.sha256

# Review script (recommended)
less install_pieces_cli.sh

# Execute
sh install_pieces_cli.sh
```

### Method 3: pip with Hash Verification

For Python environments requiring hash verification:

```bash
# Download requirements with hashes
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/requirements-hashes.txt

# Install with hash verification
pip install --require-hashes --no-deps -r requirements-hashes.txt
```

#### Creating Virtual Environment

```bash
# Create virtual environment
python -m venv pieces-env

# Activate environment
source pieces-env/bin/activate  # Linux/macOS
# or
pieces-env\Scripts\activate  # Windows

# Install with verification
pip install --require-hashes --no-deps -r requirements-hashes.txt
```

### Method 4: Docker Container

Coming soon! Docker provides isolation and consistency:

```bash
# Pull official image
docker pull ghcr.io/pieces-app/cli:latest

# Verify image signature
cosign verify ghcr.io/pieces-app/cli:latest

# Run CLI
docker run --rm -it ghcr.io/pieces-app/cli:latest help
```

### Method 5: Binary Releases

Coming soon! Pre-built binaries with signatures:

```bash
# Download binary and signature
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/pieces-linux-amd64
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/pieces-linux-amd64.sig

# Verify signature
cosign verify-blob \
  --signature pieces-linux-amd64.sig \
  --certificate-identity-regexp "https://github.com/pieces-app/*" \
  pieces-linux-amd64

# Make executable and install
chmod +x pieces-linux-amd64
sudo mv pieces-linux-amd64 /usr/local/bin/pieces
```

## Verification Steps

### Checksum Verification

All our releases include SHA256 checksums:

```bash
# For shell script
sha256sum -c install_pieces_cli.sh.sha256

# For PowerShell script (Windows)
(Get-FileHash install_pieces_cli.ps1).Hash -eq (Get-Content install_pieces_cli.ps1.sha256).Split()[0]
```

### Signature Verification (Advanced)

We use Sigstore/Cosign for keyless signing:

```bash
# Install Cosign
brew install cosign  # macOS
# or see: https://docs.sigstore.dev/cosign/installation/

# Verify signature
cosign verify-blob \
  --certificate install_pieces_cli.sh.crt \
  --signature install_pieces_cli.sh.sig \
  --certificate-identity-regexp "https://github.com/pieces-app/*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  install_pieces_cli.sh
```

### Verifying PyPI Package

Check package integrity on PyPI:

```bash
# View package info
pip show pieces-cli

# Verify installed files
pip show -f pieces-cli

# Check for known vulnerabilities
pip-audit
```

## Post-Installation Security

### 1. Verify Installation

```bash
# Check version
pieces --version

# Verify installation location
which pieces  # Linux/macOS
where pieces  # Windows

# Run security check
pieces doctor  # Coming soon
```

### 2. Configure Secure Settings

```bash
# Set secure configuration directory
export PIECES_CONFIG_DIR="$HOME/.config/pieces"

# Restrict permissions
chmod 700 "$PIECES_CONFIG_DIR"
```

### 3. Keep Updated

```bash
# Check for updates
pieces manage update --check

# Update CLI
pieces manage update
```

### 4. Monitor Security Advisories

- Watch our repository: https://github.com/pieces-app/cli-agent
- Subscribe to security advisories
- Check SECURITY.md regularly

## Troubleshooting

### Common Issues

#### "Command not found" after installation

```bash
# Check PATH
echo $PATH

# Add to PATH manually
export PATH="$HOME/.pieces-cli:$PATH"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$HOME/.pieces-cli:$PATH"' >> ~/.bashrc
```

#### Permission denied errors

```bash
# Fix permissions
chmod +x ~/.pieces-cli/pieces

# For system-wide installation
sudo chmod 755 /usr/local/bin/pieces
```

#### Checksum verification fails

1. Re-download both files
2. Check for network issues
3. Verify you're downloading from official sources
4. Report to security@pieces.app if issue persists

### Getting Help

- Documentation: https://docs.pieces.app
- GitHub Issues: https://github.com/pieces-app/cli-agent/issues
- Security Issues: security@pieces.app
- General Support: support@pieces.app

## Security Checklist

Before running Pieces CLI:

- [ ] Downloaded from official source (github.com/pieces-app)
- [ ] Verified checksums or signatures
- [ ] Reviewed installation method security
- [ ] Checked system requirements
- [ ] Enabled 2FA on related accounts (GitHub, PyPI)
- [ ] Subscribed to security updates

## Conclusion

Security is a shared responsibility. By following this guide, you're taking important steps to protect your development environment from supply chain attacks. We continuously improve our security measures and welcome feedback at security@pieces.app.