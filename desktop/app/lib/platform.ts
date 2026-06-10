declare global {
  interface Window {
    electronAPI?: { platform: NodeJS.Platform }
  }
}

export {}

/** True only when running inside Electron on macOS. Safe when electronAPI is undefined (web build). */
export function isMac(): boolean {
  return typeof window !== 'undefined' && window.electronAPI?.platform === 'darwin'
}
