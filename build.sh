#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
#  TechSoul Audit Suite — Cross-Platform Build Script
#  Builds a Windows installer (.exe) from macOS using Docker.
#  Usage:
#    chmod +x build.sh
#    ./build.sh
# ════════════════════════════════════════════════════════════════
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ELECTRON_DIR="$REPO_ROOT/electron-app"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
DIST_DIR="$REPO_ROOT/dist"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  TechSoul Audit Suite — Windows Build        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Build Next.js frontend ─────────────────────────────
echo "▶ [1/4] Building Next.js frontend…"
cd "$FRONTEND_DIR"
npm install --silent
npm run build
echo "    ✓ Frontend built → frontend/.next/"

# ── Step 2: Bundle Python backend with PyInstaller (via Docker) ─
echo ""
echo "▶ [2/4] Bundling Python backend with PyInstaller (Docker)…"
echo "    (This requires Docker Desktop to be running)"
echo ""

docker run --rm \
  -v "$BACKEND_DIR:/src/backend" \
  -v "$ELECTRON_DIR:/src/electron-app" \
  --workdir /src/backend \
  cdrx/pyinstaller-windows:python3 \
  bash -c "
    pip install --quiet fastapi uvicorn[standard] reportlab google-generativeai httpx aiofiles python-multipart &&
    pyinstaller audit_server.spec --distpath /src/electron-app/backend-dist --clean -y
  "

echo "    ✓ Backend bundled → electron-app/backend-dist/"

# ── Step 3: Install Electron dependencies ──────────────────────
echo ""
echo "▶ [3/4] Installing Electron dependencies…"
cd "$ELECTRON_DIR"
npm install --silent
echo "    ✓ electron-builder ready"

# ── Step 4: Build Windows installer ───────────────────────────
echo ""
echo "▶ [4/4] Building Windows installer with electron-builder…"
mkdir -p "$DIST_DIR"

# electron-builder cross-compiles to Windows using Wine inside Docker
docker run --rm \
  -v "$ELECTRON_DIR:/project" \
  -v "$DIST_DIR:/project/dist" \
  -e ELECTRON_CACHE="/root/.cache/electron" \
  -e ELECTRON_BUILDER_CACHE="/root/.cache/electron-builder" \
  electronuserland/builder:wine \
  bash -c "
    cd /project &&
    npm install --silent &&
    npx electron-builder --win --x64
  "

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ BUILD COMPLETE                                        ║"
echo "║                                                           ║"
echo "║  Output: dist/TechSoul Audit Suite Setup 1.0.0.exe      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
