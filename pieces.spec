# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the src directory path
src_path = Path("src").resolve()

a = Analysis(
    ["src/pieces/app.py"],
    pathex=[str(src_path)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "pieces",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    ],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('W ignore', None, 'OPTION')],
    a.binaries,
    a.zipfiles,
    a.datas,
    name="pieces",
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
)
