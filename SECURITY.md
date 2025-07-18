# Security Policy

## Supported Versions

The following versions of Pieces CLI are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously at Pieces. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. Email security details to: **security@pieces.app**
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your recommended fix (if any)

We aim to respond within 48 hours and will keep you updated on our progress.

## Security Measures

### Installation Security

We provide multiple secure installation methods to protect against supply chain attacks:

#### 1. Package Managers (Most Secure)

Package managers provide built-in verification:

```bash
# Homebrew (macOS/Linux) - GPG signed
brew install pieces-cli

# Chocolatey (Windows) - Package verification
choco install pieces-cli

# pip with hash verification
pip install --require-hashes -r https://github.com/pieces-app/cli-agent/releases/latest/download/requirements-hashes.txt
```

#### 2. Verified Script Installation (Recommended)

Download and verify checksums before execution:

```bash
# Download secure installer
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/secure-install.sh
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/secure-install.sh.sha256

# Verify checksum
sha256sum -c secure-install.sh.sha256

# Run installer
sh secure-install.sh
```

#### 3. Manual Verification

For the standard installation scripts:

```bash
# Download files
curl -LO https://raw.githubusercontent.com/pieces-app/cli-agent/main/install_pieces_cli.sh
curl -LO https://raw.githubusercontent.com/pieces-app/cli-agent/main/install_pieces_cli.sh.sha256

# Verify checksum
sha256sum -c install_pieces_cli.sh.sha256

# Review script (recommended)
less install_pieces_cli.sh

# Execute
sh install_pieces_cli.sh
```

### Signature Verification (Advanced)

We sign our releases using Sigstore/Cosign for additional security:

```bash
# Install Cosign
brew install cosign

# Verify script signature
cosign verify-blob \
  --certificate install_pieces_cli.sh.crt \
  --signature install_pieces_cli.sh.sig \
  --certificate-identity-regexp "https://github.com/pieces-app/*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  install_pieces_cli.sh
```

## Security Best Practices

### For Users

1. **Always verify checksums** before running installation scripts
2. **Use official sources** - only download from github.com/pieces-app
3. **Keep CLI updated** - security patches are released regularly
4. **Enable 2FA** on your GitHub and PyPI accounts
5. **Review scripts** before execution when possible

### For Contributors

1. **Never commit secrets** - use environment variables
2. **Dependencies** - pin versions and use lock files
3. **Code review** - all PRs require security review
4. **Testing** - include security tests for new features

## Security Features

### Current Implementation

- ✅ SHA256 checksums for all installation scripts
- ✅ Sigstore/Cosign signatures for releases
- ✅ Virtual environment isolation
- ✅ Secure credential storage
- ✅ HTTPS-only communications
- ✅ Input validation and sanitization

### Planned Enhancements

- 🔄 SLSA Level 3 compliance (Q2 2024)
- 🔄 Reproducible builds
- 🔄 Binary releases with code signing
- 🔄 Container images with attestations

## Vulnerability Disclosure Timeline

1. **Initial Report**: Acknowledged within 48 hours
2. **Triage**: Severity assessment within 72 hours
3. **Fix Development**: Based on severity:
   - Critical: 24 hours
   - High: 48 hours
   - Medium: 7 days
   - Low: 30 days
4. **Disclosure**: Coordinated disclosure after fix is available

## Security Advisories

Security advisories are published at: https://github.com/pieces-app/cli-agent/security/advisories

## Compliance

Pieces CLI follows industry security standards:

- **OWASP** guidelines for secure development
- **CWE** vulnerability categorization
- **NIST** cybersecurity framework principles

## Contact

- Security issues: **security@pieces.app**
- General support: **support@pieces.app**
- Security updates: Watch this repository or subscribe to our security mailing list