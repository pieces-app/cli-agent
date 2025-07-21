# -*- mode: python ; coding: utf-8 -*-
"""
Pieces CLI PyInstaller Specification

ANTIVIRUS OPTIMIZATION STRATEGY:
1. Single Directory Mode: Separates exe from DLLs for better AV analysis
2. No Optimization: Uses optimize=0 to keep bytecode readable
3. No Compression: Disables all compression for transparency
4. Code Signing: Integrated with DigiCert signing in CI/CD
5. Manifest: Includes proper Windows manifest for legitimacy
6. Runtime Hook: Adds legitimacy signals during execution

This configuration prioritizes antivirus compatibility over file size.
"""

import sys
from pathlib import Path

windows_icon_path = "./assets/pieces.ico"
macos_icon_path = "./assets/pieces.icns"

app_icon = windows_icon_path
if sys.platform.startswith("win"):
    app_icon = windows_icon_path
elif sys.platform.startswith("darwin"):
    app_icon = macos_icon_path

# Get the src directory path
src_path = Path("src").resolve()

a = Analysis(
    ["src/pieces/app.py"],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        (str(src_path / "pieces"), "pieces"),
        (str(src_path / "pieces" / "completions"), "pieces/completions"),
    ],
    hiddenimports=["pieces", "pieces.pieces_argparser"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["src/pieces/runtime_hook.py"],
    excludes=[
        "tkinter",
        "_tkinter",
        "tkinter.ttk",
        "tkinter.constants",
        "Tkinter",
        "test",
        "unittest",
        "doctest",
        "pdb",
        "idlelib",
        "distutils",
        "lib2to3",
        "pydoc",
        "py_compile",
        "ensurepip",
        "pkg_resources",
        "PIL",
        "Pillow",
        # Additional excludes for smaller, cleaner binary
        "matplotlib",
        "IPython",
        "jupyter",
        "pandas",
        "numpy",
        "scipy",
        "sklearn",
        "tensorflow",
        "torch",
    ],
    noarchive=False,
    # ANTIVIRUS OPTIMIZATION: Use minimal optimization to avoid suspicion
    optimize=0,  # No bytecode optimization - most compatible
)

pyz = PYZ(a.pure,
    # ANTIVIRUS OPTIMIZATION: Disable compression in PYZ
    compress=False  # Uncompressed bytecode is less suspicious
)

exe = EXE(
    pyz,
    a.scripts,
    # ANTIVIRUS OPTIMIZATION: Remove warning suppression for transparency
    [],
    exclude_binaries=True,  # CRITICAL: This makes it single directory mode
    name="pieces",
    debug=False,
    strip=False,  # Never strip symbols - causes issues and looks suspicious
    upx=False,   # Never use UPX - major cause of false positives
    console=True,
    icon=app_icon,
    # Add version information for legitimacy
    version="version_info.txt" if sys.platform.startswith("win") else None,
    # ANTIVIRUS OPTIMIZATION: Add manifest for Windows
    manifest="""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="Pieces.CLI"
    type="win32"
  />
  <description>Pieces CLI - Command-line interface for Pieces developer tools</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/> <!-- Windows Vista -->
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/> <!-- Windows 7 -->
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/> <!-- Windows 8 -->
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/> <!-- Windows 8.1 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/> <!-- Windows 10 -->
    </application>
  </compatibility>
</assembly>""" if sys.platform.startswith("win") else None,
)

# CRITICAL: Add COLLECT for single directory mode
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,  # Never strip in collection
    upx=False,    # Never compress in collection
    upx_exclude=[],
    name="pieces",  # This creates a 'pieces' directory with all files
)
