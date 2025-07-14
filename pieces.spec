# -*- mode: python ; coding: utf-8 -*-

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
    [("W ignore", None, "OPTION")],
    a.binaries,
    a.zipfiles,
    a.datas,
    name="pieces",
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    icon=app_icon,
)
