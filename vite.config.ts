import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import electron from 'vite-plugin-electron/simple'
import path from 'node:path'

export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
    electron({
      main: {
        entry: 'electron/main.ts',
      },
      preload: {
        input: 'electron/preload.ts',
      },
      renderer: {},
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './desktop'),
    },
  },
  server: {
    watch: {
      // Exclude the Python backend directory entirely — SQLite journals,
      // .db files and Python caches change constantly and must never
      // trigger a Vite HMR/reload cycle.
      ignored: ['**/server/**', '**/*.db', '**/*.db-journal', '**/*.db-wal', '**/*.db-shm'],
    },
  },
})
