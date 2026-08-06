# audit_server.spec
# PyInstaller spec file — bundles FastAPI backend into a single executable.
# Run on Windows:  pyinstaller audit_server.spec

import os, sys
from pathlib import Path

ROOT = Path(SPECPATH)          # backend/ directory
STATIC = ROOT / "static"

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # ── Include all static assets (logos, HTML) ──────────────
        (str(STATIC / "*.png"),   "static"),
        (str(STATIC / "*.svg"),   "static"),
        (str(STATIC / "*.html"),  "static"),
        # ── Include the reports output folder placeholder ────────
    ],
    hiddenimports=[
        # FastAPI / Starlette internals
        "uvicorn.lifespan.on",
        "uvicorn.logging",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "starlette.routing",
        "starlette.middleware",
        "starlette.responses",
        "starlette.staticfiles",
        "starlette.templating",
        "starlette.background",
        "fastapi",
        "fastapi.responses",
        "fastapi.middleware",
        "fastapi.middleware.cors",
        # ReportLab
        "reportlab",
        "reportlab.pdfgen",
        "reportlab.lib",
        "reportlab.lib.pagesizes",
        "reportlab.platypus",
        "reportlab.graphics",
        # Google AI
        "google.generativeai",
        # Other deps
        "httpx",
        "anyio",
        "h11",
        "aiofiles",
        "pydantic",
        "pydantic.v1",
        "multipart",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "numpy", "PIL"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="audit_server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No console window on Windows
    icon=str(ROOT.parent / "electron-app" / "assets" / "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="audit_server",
)
