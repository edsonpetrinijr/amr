"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const electron = require("electron");
const node_url = require("node:url");
const path = require("node:path");
const ws = require("ws");
var _documentCurrentScript = typeof document !== "undefined" ? document.currentScript : null;
const WS_PORT = 8765;
async function callRenderer(win2, js) {
  return win2.webContents.executeJavaScript(js);
}
function startWSBridge(win2) {
  const wss = new ws.WebSocketServer({ port: WS_PORT });
  wss.on("listening", () => {
    console.log(`[ml-bridge] WebSocket server listening on ws://localhost:${WS_PORT}`);
  });
  wss.on("connection", (ws2) => {
    console.log("[ml-bridge] Python agent connected");
    ws2.on("message", async (raw) => {
      let msg;
      try {
        msg = JSON.parse(raw.toString());
      } catch {
        ws2.send(JSON.stringify({ error: "invalid JSON" }));
        return;
      }
      try {
        let result;
        switch (msg.type) {
          case "ping": {
            const cfg = await callRenderer(win2, `window.__ML_ENV.getConfig()`);
            result = { pong: true, ...cfg };
            break;
          }
          case "reset": {
            const seed = msg.seed;
            const js = seed !== void 0 ? `window.__ML_ENV.reset(${seed})` : `window.__ML_ENV.reset()`;
            const obs = await callRenderer(win2, js);
            result = { type: "reset", observation: obs };
            break;
          }
          case "step": {
            const actions = msg.actions;
            const js = `window.__ML_ENV.step(${JSON.stringify(actions)})`;
            result = await callRenderer(win2, js);
            break;
          }
          case "getState": {
            result = await callRenderer(win2, `window.__ML_ENV.getState()`);
            break;
          }
          case "getObservation": {
            result = await callRenderer(win2, `window.__ML_ENV.getObservation()`);
            break;
          }
          case "setMLMode": {
            const enabled = msg.enabled;
            await callRenderer(win2, `window.__ML_ENV.setMLMode(${enabled})`);
            result = { type: "setMLMode", enabled };
            break;
          }
          case "metrics": {
            const m = msg;
            await callRenderer(win2, `window.__METRICS.push(${JSON.stringify({ episode: m.episode, totalReward: m.totalReward, goals: m.goals, collisions: m.collisions, steps: m.steps, aliveAtEnd: m.aliveAtEnd })})`);
            result = { type: "metrics", ok: true };
            break;
          }
          default:
            result = { error: `unknown type: ${msg.type}` };
        }
        ws2.send(JSON.stringify(result));
      } catch (err) {
        ws2.send(JSON.stringify({ error: String(err) }));
      }
    });
    ws2.on("close", () => {
      console.log("[ml-bridge] Python agent disconnected");
      callRenderer(win2, `window.__ML_ENV.setMLMode(false)`).catch(() => {
      });
    });
  });
  wss.on("error", (err) => {
    console.error("[ml-bridge] WS server error:", err.message);
  });
  return wss;
}
const __dirname$1 = path.dirname(node_url.fileURLToPath(typeof document === "undefined" ? require("url").pathToFileURL(__filename).href : _documentCurrentScript && _documentCurrentScript.tagName.toUpperCase() === "SCRIPT" && _documentCurrentScript.src || new URL("main.js", document.baseURI).href));
process.env.APP_ROOT = path.join(__dirname$1, "..");
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
const MAIN_DIST = path.join(process.env.APP_ROOT, "dist-electron");
const RENDERER_DIST = path.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, "public") : RENDERER_DIST;
let win;
function createWindow() {
  win = new electron.BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1e3,
    minHeight: 700,
    titleBarStyle: "hiddenInset",
    backgroundColor: "#0d1117",
    webPreferences: {
      preload: path.join(__dirname$1, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL);
  } else {
    win.loadFile(path.join(RENDERER_DIST, "index.html"));
  }
  const _win = win;
  _win.webContents.once("did-finish-load", () => {
    startWSBridge(_win);
  });
}
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
    win = null;
  }
});
electron.app.on("activate", () => {
  if (electron.BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
electron.app.whenReady().then(createWindow);
exports.MAIN_DIST = MAIN_DIST;
exports.RENDERER_DIST = RENDERER_DIST;
exports.VITE_DEV_SERVER_URL = VITE_DEV_SERVER_URL;
