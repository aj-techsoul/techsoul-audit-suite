// Preload script – exposes a safe bridge between Electron and the renderer
const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronApp", {
  platform: process.platform,
  version:  process.env.npm_package_version || "1.0.0",
});
