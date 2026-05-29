// WebSocket server — bridges Python ML agents to the renderer's window.__ML_ENV.
// Runs in Electron main process. Uses executeJavaScript to call into renderer.
// Protocol: newline-delimited JSON over WebSocket.

import { BrowserWindow } from 'electron';
import { WebSocketServer, WebSocket } from 'ws';

const WS_PORT = 8765;

type WSMessage =
  | { type: 'reset'; seed?: number }
  | { type: 'step'; actions: number[] }
  | { type: 'getState' }
  | { type: 'getObservation' }
  | { type: 'setMLMode'; enabled: boolean }
  | { type: 'metrics'; episode: number; totalReward: number; goals: number; collisions: number; steps: number; aliveAtEnd: number }
  | { type: 'ping' };

async function callRenderer(win: BrowserWindow, js: string): Promise<unknown> {
  return win.webContents.executeJavaScript(js);
}

export function startWSBridge(win: BrowserWindow) {
  const wss = new WebSocketServer({ port: WS_PORT });

  wss.on('listening', () => {
    console.log(`[ml-bridge] WebSocket server listening on ws://localhost:${WS_PORT}`);
  });

  wss.on('connection', (ws: WebSocket) => {
    console.log('[ml-bridge] Python agent connected');

    ws.on('message', async (raw: Buffer) => {
      let msg: WSMessage;
      try {
        msg = JSON.parse(raw.toString());
      } catch {
        ws.send(JSON.stringify({ error: 'invalid JSON' }));
        return;
      }

      try {
        let result: unknown;

        switch (msg.type) {
          case 'ping': {
            const cfg = await callRenderer(win, `window.__ML_ENV.getConfig()`);
            result = { pong: true, ...(cfg as object) };
            break;
          }

          case 'reset': {
            const seed = (msg as { type: 'reset'; seed?: number }).seed;
            const js = seed !== undefined
              ? `window.__ML_ENV.reset(${seed})`
              : `window.__ML_ENV.reset()`;
            const obs = await callRenderer(win, js);
            result = { type: 'reset', observation: obs };
            break;
          }

          case 'step': {
            const actions = (msg as { type: 'step'; actions: number[] }).actions;
            const js = `window.__ML_ENV.step(${JSON.stringify(actions)})`;
            result = await callRenderer(win, js);
            break;
          }

          case 'getState': {
            result = await callRenderer(win, `window.__ML_ENV.getState()`);
            break;
          }

          case 'getObservation': {
            result = await callRenderer(win, `window.__ML_ENV.getObservation()`);
            break;
          }

          case 'setMLMode': {
            const enabled = (msg as { type: 'setMLMode'; enabled: boolean }).enabled;
            await callRenderer(win, `window.__ML_ENV.setMLMode(${enabled})`);
            result = { type: 'setMLMode', enabled };
            break;
          }

          case 'metrics': {
            const m = msg as { type: 'metrics'; episode: number; totalReward: number; goals: number; collisions: number; steps: number; aliveAtEnd: number };
            await callRenderer(win, `window.__METRICS.push(${JSON.stringify({ episode: m.episode, totalReward: m.totalReward, goals: m.goals, collisions: m.collisions, steps: m.steps, aliveAtEnd: m.aliveAtEnd })})`);
            result = { type: 'metrics', ok: true };
            break;
          }

          default:
            result = { error: `unknown type: ${(msg as { type: string }).type}` };
        }

        ws.send(JSON.stringify(result));
      } catch (err) {
        ws.send(JSON.stringify({ error: String(err) }));
      }
    });

    ws.on('close', () => {
      console.log('[ml-bridge] Python agent disconnected');
      // Restore UI control when Python disconnects
      callRenderer(win, `window.__ML_ENV.setMLMode(false)`).catch(() => {});
    });
  });

  wss.on('error', (err: Error) => {
    console.error('[ml-bridge] WS server error:', err.message);
  });

  return wss;
}
