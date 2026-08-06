/**
 * TechSoul Audit Suite – Electron Main Process
 *
 * Lifecycle:
 *  1. Show splash screen immediately
 *  2. Spawn the bundled Python/FastAPI backend (.exe on Windows)
 *  3. Poll /api/health until backend is ready (max 30 s)
 *  4. Load the app in the main window
 *  5. On quit, kill the backend process
 */

const { app, BrowserWindow, shell, dialog } = require("electron");
const path  = require("path");
const { spawn, execFile } = require("child_process");
const http  = require("http");
const log   = require("electron-log");

// ── Config ──────────────────────────────────────────────────────────
const BACKEND_PORT = 8765;          // Use a non-standard port to avoid conflicts
const BACKEND_URL  = `http://127.0.0.1:${BACKEND_PORT}`;
const MAX_WAIT_MS  = 40_000;        // 40 s startup timeout
const POLL_MS      = 500;

let backendProcess = null;
let splashWindow   = null;
let mainWindow     = null;

// ── Logging ─────────────────────────────────────────────────────────
log.transports.file.level = "info";
log.info("App starting…");

// ── Splash window ────────────────────────────────────────────────────
function createSplash() {
  splashWindow = new BrowserWindow({
    width: 520,
    height: 320,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    webPreferences: { nodeIntegration: false },
  });
  splashWindow.loadFile(path.join(__dirname, "splash.html"));
  splashWindow.center();
}

// ── Main window ──────────────────────────────────────────────────────
function createMain() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    icon: path.join(__dirname, "assets", "icon.png"),
    title: "TechSoul Audit Suite",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadURL(BACKEND_URL);
  mainWindow.setMenuBarVisibility(false);

  mainWindow.once("ready-to-show", () => {
    if (splashWindow) { splashWindow.close(); splashWindow = null; }
    mainWindow.show();
    mainWindow.maximize();
  });

  // Open external links in the real browser, not Electron
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (!url.startsWith(BACKEND_URL)) shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => { mainWindow = null; });
}

// ── Backend launcher ─────────────────────────────────────────────────
function getBackendPath() {
  // In development: look for uvicorn. In production: use bundled exe.
  if (app.isPackaged) {
    const exeName = process.platform === "win32" ? "audit_server.exe" : "audit_server";
    return path.join(process.resourcesPath, "backend", exeName);
  }
  // Dev mode: run Python directly
  return null;
}

function startBackend() {
  return new Promise((resolve, reject) => {
    const backendExe = getBackendPath();

    if (backendExe) {
      // Production – run bundled exe
      log.info("Starting backend:", backendExe);
      backendProcess = execFile(
        backendExe,
        [`--port=${BACKEND_PORT}`],
        { windowsHide: true }
      );
    } else {
      // Development – run uvicorn via Python
      log.info("Dev mode: starting uvicorn");
      const backendDir = path.join(__dirname, "..", "backend");
      backendProcess = spawn(
        "python3",
        ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", `--port=${BACKEND_PORT}`],
        { cwd: backendDir, windowsHide: true }
      );
    }

    backendProcess.stdout?.on("data", (d) => log.info("[backend]", d.toString().trim()));
    backendProcess.stderr?.on("data", (d) => log.warn("[backend]", d.toString().trim()));

    backendProcess.on("error", (err) => {
      log.error("Backend failed to start:", err);
      reject(err);
    });

    // Poll the health endpoint
    const deadline = Date.now() + MAX_WAIT_MS;
    const timer = setInterval(() => {
      http.get(`${BACKEND_URL}/api/health`, (res) => {
        if (res.statusCode === 200) {
          clearInterval(timer);
          log.info("Backend is ready.");
          resolve();
        }
      }).on("error", () => {
        if (Date.now() > deadline) {
          clearInterval(timer);
          reject(new Error("Backend startup timed out"));
        }
      });
    }, POLL_MS);
  });
}

// ── App lifecycle ────────────────────────────────────────────────────
app.whenReady().then(async () => {
  createSplash();

  try {
    await startBackend();
    createMain();
  } catch (err) {
    log.error("Fatal:", err);
    if (splashWindow) splashWindow.close();
    dialog.showErrorBox(
      "TechSoul Audit Suite — Startup Error",
      `Could not start the backend server.\n\n${err.message}\n\nCheck logs for details.`
    );
    app.quit();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createMain();
});

app.on("before-quit", () => {
  if (backendProcess) {
    log.info("Shutting down backend…");
    backendProcess.kill();
  }
});
