# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the src directory path
src_path = Path('src').resolve()

a = Analysis(
    ['src/pieces/app.py'],
    pathex=[str(src_path)],  # Add src to the path
    binaries=[],
    datas=[],
    hiddenimports=[
        "pieces",
        "pieces.pieces_argparser",
        "pieces.command_registry",
        "pieces.settings",
        "pieces.logger",
        "pieces.command_interface",
        "pieces.command_interface.config_command",
        "pieces.command_interface.list_command",
        "pieces.command_interface.auth_commands",
        "pieces.command_interface.search_command",
        "pieces.command_interface.asset_commands",
        "pieces.command_interface.simple_commands",
        "pieces.command_interface.ask_command",
        "pieces.command_interface.conversation_commands",
        "pieces.command_interface.commit_command",
        "pieces.command_interface.open_command",
        "pieces.command_interface.mcp_command_group",
        "pieces.core",
        "pieces.core.config_command",
        "pieces.core.cli_loop",
        "pieces.core.change_model",
        "pieces.core.search_command",
        "pieces.core.list_command",
        "pieces.core.auth_commands",
        "pieces.core.execute_command",
        "pieces.core.assets_command",
        "pieces.core.onboarding",
        "pieces.core.feedbacks",
        "pieces.core.install_pieces_os",
        "pieces.core.open_command",
        "pieces.core.extensions",
        "pieces.copilot",
        "pieces.autocommit",
        "pieces.mcp",
        "pieces.utils",
        "pieces.urls",
        "pieces.gui",
        "pieces.base_command",
        "pieces_os_client",
        "pieces_os_client.wrapper",
        "pieces_os_client.wrapper.websockets",
        "pieces_os_client.wrapper.websockets.base_websocket",
        # Add common dependencies that might be missed
        "pkg_resources",
        "multiprocessing",
        "multiprocessing.spawn",
        "multiprocessing.popen_spawn_win32",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', '_tkinter', 'tkinter.ttk', 'tkinter.constants', 'Tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('W ignore', None, 'OPTION')],
    exclude_binaries=True,
    name='pieces',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pieces',
)
