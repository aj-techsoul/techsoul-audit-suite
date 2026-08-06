# TechSoul Audit Suite — Windows Build Guide

## What gets packaged

```
TechSoul Audit Suite.exe  (installer, ~250 MB)
  └── installs to:
        audit_server.exe     ← FastAPI backend (Python + all libs bundled)
        TechSoul Audit Suite.exe  ← Electron shell
        resources/backend/   ← logo assets, DB, reports folder
```

## Build Options

### Option A: GitHub Actions (Easiest — Recommended)

No tools needed on your Mac. GitHub's Windows servers do all the work.

1. Push the project to GitHub:
   ```bash
   cd /Applications/XAMPP/xamppfiles/htdocs/vibeconfig/proposal-maker
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/techsoul-audit
   git push -u origin main
   ```

2. Tag a release to trigger the build:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. Go to **GitHub → Actions** tab → watch the build run (~8 min).

4. Download the `.exe` from **GitHub → Releases** or the **Actions → Artifacts** section.

---

### Option B: Docker on Mac (No Windows machine needed)

1. Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

2. Open Docker Desktop and make sure it's running (whale icon in menu bar).

3. Run the build script:
   ```bash
   cd /Applications/XAMPP/xamppfiles/htdocs/vibeconfig/proposal-maker
   ./build.sh
   ```

4. Output: `dist/TechSoul Audit Suite Setup 1.0.0.exe`

Build time: ~10–15 minutes on first run (downloads Docker images), ~5 min after.

---

### Option C: Build directly on Windows

1. Copy the entire `proposal-maker/` folder to a Windows 10/11 machine.

2. Install prerequisites:
   - [Python 3.11](https://www.python.org/downloads/) — check "Add to PATH"
   - [Node.js 18+](https://nodejs.org/)
   - [Git for Windows](https://git-scm.com/download/win)

3. Open PowerShell in the project folder and run:
   ```powershell
   # Install Python deps
   cd backend
   pip install pyinstaller fastapi "uvicorn[standard]" reportlab google-generativeai httpx aiofiles python-multipart

   # Bundle backend
   pyinstaller audit_server.spec --distpath ..\electron-app\backend-dist --clean -y

   # Build Electron app
   cd ..\electron-app
   npm install
   npx electron-builder --win --x64
   ```

4. Output: `dist\TechSoul Audit Suite Setup 1.0.0.exe`

---

## What the installed app does

1. User double-clicks **TechSoul Audit Suite** from Desktop/Start Menu
2. A dark branded **splash screen** appears while the backend loads (~3–5 sec)
3. The full audit interface opens in an Electron window (no browser needed)
4. User enters a URL → Gemini analyses it → PDF report downloads
5. On close, the backend process shuts down cleanly

## First Run (User Setup)

The user needs to enter their **Gemini API key** once in Settings.  
Key is stored locally — never sent anywhere except Google's API.

## File sizes (approximate)

| Component | Size |
|-----------|------|
| Electron runtime | ~120 MB |
| Python + FastAPI bundle | ~80 MB |
| ReportLab + other deps | ~30 MB |
| **Installer total** | **~250 MB** |
| **Installed size** | **~350 MB** |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Windows protected your PC" warning | Click "More Info" → "Run Anyway" (code signing needed for production) |
| App opens but shows blank screen | Firewall may block 127.0.0.1:8765 — add exception |
| PDF not generating | Check Gemini API key is set in Settings |
| Crash on startup | Check `%AppData%\techsoul-audit-suite\logs\main.log` |
