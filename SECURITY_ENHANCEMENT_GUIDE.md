# Pieces CLI Security Enhancement Implementation Guide

## Executive Summary

This guide provides a comprehensive solution to address the security concerns identified in PR #351, based on extensive research of current threats and industry best practices. The implementation is organized into immediate, short-term, and long-term phases.

## Table of Contents

1. [Security Threat Overview](#security-threat-overview)
2. [Phased Implementation Roadmap](#phased-implementation-roadmap)
3. [Immediate Actions (Week 1-2)](#immediate-actions-week-1-2)
4. [Short-term Improvements (Month 1-2)](#short-term-improvements-month-1-2)
5. [Long-term Strategy (Month 3-6)](#long-term-strategy-month-3-6)
6. [Implementation Details](#implementation-details)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Security Threat Overview

Based on our research:
- **Supply chain attacks increased 1,300%** in recent years
- **500,000+ malicious packages** added to PyPI since Nov 2023
- **100% of organizations** experienced supply chain attacks in 2024
- Multiple high-profile compromises despite 2FA (Ultralytics, Django-log-tracker)

## Phased Implementation Roadmap

### Phase 1: Immediate Security Hardening (Week 1-2)
- Add checksum verification to installation scripts
- Create secure installation documentation
- Implement basic integrity checks

### Phase 2: Enhanced Security Infrastructure (Month 1-2)
- Implement Sigstore/Cosign signing
- Create secure binary releases
- Establish trusted publisher on PyPI

### Phase 3: Industry-Leading Security (Month 3-6)
- Achieve SLSA Level 3 compliance
- Implement reproducible builds
- Establish continuous security monitoring

## Immediate Actions (Week 1-2)

### 1. Add Checksum Verification to Installation Scripts

#### A. Generate Checksums for Release Assets

Create a GitHub Action that automatically generates checksums:

```yaml
# .github/workflows/release-checksums.yml
name: Generate Release Checksums

on:
  release:
    types: [created]

jobs:
  checksums:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Script Checksums
        run: |
          sha256sum install_pieces_cli.sh > install_pieces_cli.sh.sha256
          sha256sum install_pieces_cli.ps1 > install_pieces_cli.ps1.sha256
          
      - name: Upload Checksums to Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            install_pieces_cli.sh.sha256
            install_pieces_cli.ps1.sha256
```

#### B. Modify Installation Instructions

Update README.md with secure installation method:

```bash
# Secure Installation Method (Recommended)
# 1. Download and verify the installation script
curl -fsSL https://github.com/pieces-app/cli-agent/releases/latest/download/install_pieces_cli.sh -o install_pieces_cli.sh
curl -fsSL https://github.com/pieces-app/cli-agent/releases/latest/download/install_pieces_cli.sh.sha256 -o install_pieces_cli.sh.sha256

# 2. Verify checksum
sha256sum -c install_pieces_cli.sh.sha256

# 3. Review the script (optional but recommended)
less install_pieces_cli.sh

# 4. Execute the verified script
sh install_pieces_cli.sh
```

#### C. Create Wrapper Script with Built-in Verification

Create a new secure installer entry point:

```bash
#!/bin/sh
# secure-install.sh - Secure installer with verification

set -e

REPO="pieces-app/cli-agent"
INSTALL_SCRIPT_URL="https://github.com/${REPO}/releases/latest/download/install_pieces_cli.sh"
CHECKSUM_URL="https://github.com/${REPO}/releases/latest/download/install_pieces_cli.sh.sha256"

echo "Pieces CLI Secure Installer"
echo "=========================="

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

cd "$TEMP_DIR"

# Download files
echo "Downloading installation script..."
if ! curl -fsSL "$INSTALL_SCRIPT_URL" -o install_pieces_cli.sh; then
    echo "Error: Failed to download installation script" >&2
    exit 1
fi

echo "Downloading checksum..."
if ! curl -fsSL "$CHECKSUM_URL" -o install_pieces_cli.sh.sha256; then
    echo "Error: Failed to download checksum file" >&2
    exit 1
fi

# Verify checksum
echo "Verifying integrity..."
if command -v sha256sum >/dev/null 2>&1; then
    if ! sha256sum -c install_pieces_cli.sh.sha256; then
        echo "Error: Checksum verification failed!" >&2
        echo "The installation script may have been tampered with." >&2
        exit 1
    fi
elif command -v shasum >/dev/null 2>&1; then
    # macOS fallback
    if ! shasum -a 256 -c install_pieces_cli.sh.sha256; then
        echo "Error: Checksum verification failed!" >&2
        exit 1
    fi
else
    echo "Warning: No checksum tool available. Proceeding without verification." >&2
    echo "Install 'sha256sum' or 'shasum' for secure installation." >&2
fi

echo "Checksum verified successfully!"

# Execute the verified script
echo "Starting installation..."
sh install_pieces_cli.sh "$@"
```

### 2. Enhance pip Installation Security

#### A. Create requirements-hashes.txt

Generate a requirements file with hashes:

```bash
# Generate requirements with hashes
pip-compile --generate-hashes requirements.in -o requirements-hashes.txt
```

Example requirements-hashes.txt:
```txt
pieces-cli==1.2.3 \
    --hash=sha256:abcd1234... \
    --hash=sha256:efgh5678...
rich==13.7.0 \
    --hash=sha256:ijkl9012... \
    --hash=sha256:mnop3456...
# ... all dependencies with hashes
```

#### B. Update Installation Scripts

Modify both PowerShell and shell scripts to use hash verification:

```python
# In install_pieces_cli.ps1
Write-Info "Installing pieces-cli package with hash verification..."
try {
    # First, install pip-tools if not present
    & $venvPip install pip-tools --quiet
    
    # Download requirements with hashes
    $requirementsUrl = "https://github.com/pieces-app/cli-agent/releases/latest/download/requirements-hashes.txt"
    Invoke-WebRequest -Uri $requirementsUrl -OutFile "requirements-hashes.txt"
    
    # Install with hash verification
    & $venvPip install --require-hashes --no-deps -r requirements-hashes.txt
    if ($LASTEXITCODE -ne 0) { throw "Hash verification failed" }
}
```

### 3. Create Security Documentation

Create SECURITY.md:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities to: security@pieces.app

## Secure Installation Methods

### Method 1: Package Managers (Recommended)
```bash
# Homebrew (macOS/Linux)
brew install pieces-cli

# pip with hash verification
pip install --require-hashes -r https://github.com/pieces-app/cli-agent/releases/latest/download/requirements-hashes.txt
```

### Method 2: Verified Script Installation
```bash
# Download and verify before execution
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/secure-install.sh
curl -LO https://github.com/pieces-app/cli-agent/releases/latest/download/secure-install.sh.sha256
sha256sum -c secure-install.sh.sha256
sh secure-install.sh
```

### Method 3: Binary Releases (Coming Soon)
Signed binary releases with GPG verification.

## Verification Steps

1. Always verify checksums before installation
2. Use official sources only (github.com/pieces-app)
3. Enable 2FA on your PyPI account
4. Regular updates for security patches
```

## Short-term Improvements (Month 1-2)

### 1. Implement Sigstore/Cosign Signing

#### A. GitHub Action for Signing Releases

```yaml
# .github/workflows/sign-release.yml
name: Sign Release Artifacts

on:
  release:
    types: [created]

jobs:
  sign:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Cosign
        uses: sigstore/cosign-installer@v3
        
      - name: Sign Installation Scripts
        run: |
          # Sign with keyless signing (OIDC)
          cosign sign-blob --yes install_pieces_cli.sh --output-signature install_pieces_cli.sh.sig
          cosign sign-blob --yes install_pieces_cli.ps1 --output-signature install_pieces_cli.ps1.sig
          
      - name: Create Verification Bundle
        run: |
          cat > verify.sh << 'EOF'
          #!/bin/sh
          echo "Verifying Pieces CLI installation scripts..."
          cosign verify-blob \
            --signature install_pieces_cli.sh.sig \
            --certificate-identity-regexp "https://github.com/pieces-app/*" \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com \
            install_pieces_cli.sh
          EOF
          chmod +x verify.sh
          
      - name: Upload Signatures
        uses: softprops/action-gh-release@v1
        with:
          files: |
            *.sig
            verify.sh
```

### 2. Create Signed Binary Releases

#### A. Build Configuration

```yaml
# .github/workflows/build-binaries.yml
name: Build and Sign Binaries

on:
  release:
    types: [created]

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: linux-amd64
          - os: macos-latest
            target: darwin-amd64
          - os: macos-latest
            target: darwin-arm64
          - os: windows-latest
            target: windows-amd64
            
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Dependencies
        run: |
          pip install pyinstaller pieces-cli
          
      - name: Build Binary
        run: |
          pyinstaller \
            --onefile \
            --name pieces-${{ matrix.target }} \
            --add-data "src/pieces:pieces" \
            src/pieces/__main__.py
            
      - name: Sign Binary (macOS)
        if: startsWith(matrix.os, 'macos')
        run: |
          codesign --deep --force --verify --verbose \
            --sign "${{ secrets.APPLE_DEVELOPER_ID }}" \
            dist/pieces-${{ matrix.target }}
            
      - name: Sign Binary (Windows)
        if: startsWith(matrix.os, 'windows')
        run: |
          signtool sign /n "${{ secrets.WINDOWS_CERT_NAME }}" \
            /t http://timestamp.sectigo.com \
            dist/pieces-${{ matrix.target }}.exe
            
      - name: Create Checksum
        run: |
          cd dist
          sha256sum pieces-${{ matrix.target }}* > pieces-${{ matrix.target }}.sha256
          
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: pieces-${{ matrix.target }}
          path: dist/pieces-${{ matrix.target }}*
```

### 3. Establish PyPI Trusted Publisher

#### A. Configure PyPI Project

1. Go to PyPI project settings
2. Add trusted publisher:
   - Repository: pieces-app/cli-agent
   - Workflow: .github/workflows/publish.yml
   - Environment: pypi-production

#### B. Update Publishing Workflow

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi-production
    permissions:
      id-token: write
      contents: read
      attestations: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Dependencies
        run: |
          pip install build twine
          
      - name: Build Package
        run: python -m build
        
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          artifact-name: pieces-cli-sbom.spdx
          
      - name: Attest Build Provenance
        uses: actions/attest-build-provenance@v1
        with:
          subject-path: 'dist/*'
          
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No credentials needed - uses trusted publisher
```

## Long-term Strategy (Month 3-6)

### 1. SLSA Level 3 Compliance

#### A. Isolated Build Environment

```yaml
# .github/workflows/slsa-build.yml
name: SLSA Level 3 Build

on:
  release:
    types: [created]

jobs:
  build:
    permissions:
      id-token: write
      contents: read
      attestations: write
      
    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml@v1.9.0
    with:
      go-version: 1.21
      config-file: .github/workflows/slsa-config.yml
      
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
      
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
    with:
      base64-subjects: "${{ needs.build.outputs.digests }}"
      upload-assets: true
```

### 2. Reproducible Builds

#### A. Build Configuration

```python
# setup.py modifications for reproducibility
import os
from datetime import datetime

# Set reproducible timestamp
SOURCE_DATE_EPOCH = os.environ.get('SOURCE_DATE_EPOCH', '1640995200')
os.environ['SOURCE_DATE_EPOCH'] = SOURCE_DATE_EPOCH

# Disable randomization
os.environ['PYTHONHASHSEED'] = '0'

# Configure build
setup(
    name='pieces-cli',
    version=VERSION,
    # ... other config
    zip_safe=False,  # Ensure consistent file layout
    options={
        'bdist_wheel': {
            'universal': False,  # Platform-specific builds
        },
        'egg_info': {
            'tag_date': False,  # Disable date tagging
        },
    },
)
```

#### B. Verification Script

```bash
#!/bin/bash
# verify-reproducible.sh

set -e

# Build twice in different environments
docker run --rm -v $(pwd):/app python:3.11 \
  bash -c "cd /app && SOURCE_DATE_EPOCH=1640995200 python -m build"
mv dist dist1

docker run --rm -v $(pwd):/app python:3.11 \
  bash -c "cd /app && SOURCE_DATE_EPOCH=1640995200 python -m build"
mv dist dist2

# Compare checksums
sha256sum dist1/* > checksums1.txt
sha256sum dist2/* > checksums2.txt

if diff checksums1.txt checksums2.txt; then
    echo "Build is reproducible!"
else
    echo "Build is NOT reproducible!"
    exit 1
fi
```

### 3. Container-Based Distribution

#### A. Official Docker Image

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash pieces

# Install pieces-cli
COPY requirements-hashes.txt /tmp/
RUN pip install --require-hashes --no-deps -r /tmp/requirements-hashes.txt

# Runtime stage
FROM python:3.11-slim

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/pieces /usr/local/bin/pieces

# Create non-root user
RUN useradd -m -s /bin/bash pieces
USER pieces

ENTRYPOINT ["pieces"]
```

#### B. Sign and Push Container

```yaml
# .github/workflows/container-release.yml
name: Build and Sign Container

on:
  release:
    types: [created]

jobs:
  container:
    runs-on: ubuntu-latest
    permissions:
      packages: write
      id-token: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and Push
        id: build
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/pieces-app/cli:latest
            ghcr.io/pieces-app/cli:${{ github.ref_name }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          
      - name: Sign Container
        run: |
          cosign sign --yes ghcr.io/pieces-app/cli@${{ steps.build.outputs.digest }}
          
      - name: Attest SBOM
        run: |
          syft ghcr.io/pieces-app/cli@${{ steps.build.outputs.digest }} \
            -o spdx-json > sbom.spdx.json
          cosign attest --yes --predicate sbom.spdx.json \
            ghcr.io/pieces-app/cli@${{ steps.build.outputs.digest }}
```

## Implementation Details

### 1. CI/CD Security Pipeline

```yaml
# .github/workflows/security-checks.yml
name: Security Checks

on:
  pull_request:
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy Security Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          
      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
          
      - name: Check Dependencies
        run: |
          pip install safety
          safety check --json
          
      - name: SAST Scan
        uses: github/super-linter@v5
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Automated Dependency Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    security-updates-only: true
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Security Headers for Distribution

```nginx
# nginx.conf for download server
server {
    listen 443 ssl http2;
    server_name downloads.pieces.app;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Content-Security-Policy "default-src 'none'; style-src 'unsafe-inline';" always;
    
    # Integrity headers
    add_header Digest "sha-256=..." always;
    add_header Want-Digest "sha-256" always;
    
    location /cli/ {
        root /var/www/downloads;
        
        # Enable checksum files
        location ~ \.(sha256|sig|asc)$ {
            add_header Cache-Control "public, max-age=3600";
        }
    }
}
```

## Monitoring and Maintenance

### 1. Security Monitoring

```python
# scripts/security-monitor.py
#!/usr/bin/env python3
"""Monitor for security issues in Pieces CLI."""

import requests
import json
from datetime import datetime

def check_pypi_security():
    """Check for known vulnerabilities in PyPI packages."""
    # Use PyUp.io Safety API
    response = requests.get(
        "https://pyup.io/api/v1/safety/check",
        json={"packages": ["pieces-cli"]},
        headers={"X-Api-Key": os.environ["SAFETY_API_KEY"]}
    )
    return response.json()

def check_github_security():
    """Check GitHub security advisories."""
    query = """
    {
      repository(owner: "pieces-app", name: "cli-agent") {
        vulnerabilityAlerts(first: 10) {
          nodes {
            severity
            vulnerableManifestPath
            securityAdvisory {
              summary
              description
            }
          }
        }
      }
    }
    """
    # Query GitHub GraphQL API
    # ... implementation

def main():
    """Run security checks and alert if issues found."""
    issues = []
    
    # Check various sources
    issues.extend(check_pypi_security())
    issues.extend(check_github_security())
    
    if issues:
        # Send alerts (email, Slack, etc.)
        send_security_alert(issues)
    
if __name__ == "__main__":
    main()
```

### 2. Automated Security Updates

```yaml
# .github/workflows/auto-security-update.yml
name: Auto Security Update

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Update Dependencies
        run: |
          pip install pip-tools
          pip-compile --upgrade --generate-hashes \
            requirements.in -o requirements-hashes.txt
            
      - name: Create PR if Changes
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Security: Update dependencies"
          body: "Automated security update of dependencies"
          branch: security/auto-update
```

### 3. Incident Response Plan

Create INCIDENT_RESPONSE.md:

```markdown
# Security Incident Response Plan

## 1. Detection
- Automated monitoring alerts
- User reports to security@pieces.app
- Third-party vulnerability disclosures

## 2. Triage (Within 2 hours)
- Assess severity (Critical/High/Medium/Low)
- Identify affected versions
- Determine exploit potential

## 3. Response (Within 24 hours)
- **Critical**: Immediate patch release
- **High**: Patch within 48 hours
- **Medium/Low**: Next regular release

## 4. Communication
- Security advisory on GitHub
- Email to affected users
- Update status page

## 5. Post-Incident
- Root cause analysis
- Update security processes
- Public disclosure after patch
```

## Success Metrics

1. **Security Metrics**
   - Time to patch critical vulnerabilities: < 24 hours
   - Percentage of releases with signatures: 100%
   - SLSA compliance level: 3+

2. **Adoption Metrics**
   - Percentage using secure installation: > 80%
   - Downloads of signed artifacts: > 90%
   - Security documentation views: Track monthly

3. **Quality Metrics**
   - False positive rate in security scans: < 5%
   - Build reproducibility rate: > 95%
   - Dependency update frequency: Weekly

## Conclusion

This comprehensive implementation guide provides a clear path from the current state to industry-leading security practices. The phased approach allows for immediate security improvements while building toward long-term goals like SLSA Level 3 compliance and reproducible builds.

Key success factors:
1. Start with high-impact, low-effort improvements (checksums)
2. Build security into the CI/CD pipeline
3. Maintain backwards compatibility during transition
4. Clear communication with users about security improvements
5. Regular security audits and updates

By following this guide, Pieces CLI can significantly enhance its security posture and protect users from the growing threat of supply chain attacks.