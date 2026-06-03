import React from 'react'

// Root-level error boundary. A thrown error during boot (bad import, render
// exception) would otherwise leave Electron showing a completely BLANK window.
// This catches it and paints a visible, self-contained message — styled with
// inline styles only, so it stays readable even if Tailwind/CSS never loaded.
interface State { error: Error | null }

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Surface to the Electron/devtools console for field diagnostics.
    console.error('[fleet] boot error:', error, info.componentStack)
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children

    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 24,
          background: '#0d1117',
          color: '#c9d1d9',
          fontFamily: 'system-ui, -apple-system, Segoe UI, sans-serif',
        }}
      >
        <div style={{ maxWidth: 640 }}>
          <h1 style={{ color: '#f85149', fontSize: 20, fontWeight: 600, margin: '0 0 12px' }}>
            The Fleet console hit an error while starting
          </h1>
          <p style={{ color: '#8b949e', margin: '0 0 16px', lineHeight: 1.5 }}>
            The interface failed to boot. This does not stop the robots — it only
            affects this console. Try reloading. If it persists, share the details
            below with engineering.
          </p>
          <pre
            style={{
              background: '#161b22',
              border: '1px solid #30363d',
              borderRadius: 6,
              padding: 12,
              fontSize: 12,
              color: '#e6edf3',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {error.message}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: 16,
              padding: '8px 16px',
              borderRadius: 6,
              border: 0,
              background: '#238636',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Reload console
          </button>
        </div>
      </div>
    )
  }
}
