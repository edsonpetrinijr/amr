import React, { useState, useEffect } from 'react'
import { Settings, Save, AlertTriangle, CheckCircle, Wifi, WifiOff } from 'lucide-react'
import { useFleet } from '../state/store'
import { fleetApi, FleetApiError, type MapInfo } from '../api/fleet'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'

const DEFAULT_URL = 'http://localhost:8765'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-xs font-semibold text-[#8b949e] uppercase tracking-widest mb-3">{title}</h2>
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg divide-y divide-[#30363d]">
        {children}
      </div>
    </div>
  )
}

function Row({ label, sub, children }: { label: string; sub?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between px-4 py-3.5 gap-4">
      <div>
        <p className="text-sm text-[#c9d1d9] font-medium">{label}</p>
        {sub && <p className="text-xs text-[#8b949e] mt-0.5">{sub}</p>}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  )
}

function Toggle({ value, onChange, disabled }: { value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      role="switch"
      aria-checked={value}
      disabled={disabled}
      onClick={() => onChange(!value)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none
        ${value ? 'bg-[#1f6feb]' : 'bg-[#30363d]'} ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}>
      <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transform transition-transform
        ${value ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
  )
}

function MapSelector() {
  const [maps, setMaps] = useState<MapInfo[]>([])
  const [selected, setSelected] = useState<string>('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    fleetApi.getMaps()
      .then(list => {
        if (!alive) return
        setMaps(list)
        setSelected(list.find(m => m.current)?.name ?? list[0]?.name ?? '')
      })
      .catch(e => { if (alive) setError(e instanceof Error ? e.message : 'Failed to load maps') })
    return () => { alive = false }
  }, [])

  async function onChange(name: string) {
    const prev = selected
    setSelected(name)      // optimistic
    setBusy(true)
    setError(null)
    try {
      await fleetApi.selectMap(name)
      // SSE `map` message refreshes the canvas; just mark this one current.
      setMaps(ms => ms.map(m => ({ ...m, current: m.name === name })))
    } catch (e) {
      setSelected(prev)    // revert on failure
      setError(e instanceof FleetApiError ? e.message : (e instanceof Error ? e.message : 'Failed to switch map'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <select
        className="w-56 bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-xs font-mono text-[#58a6ff]
          focus:outline-none focus:border-[#58a6ff] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        value={selected}
        disabled={busy || maps.length === 0}
        onChange={e => onChange(e.target.value)}
      >
        {maps.length === 0 && <option value="">No maps available</option>}
        {maps.map(m => (
          <option key={m.name} value={m.name} className="bg-[#0d1117] text-[#c9d1d9]">{m.name}</option>
        ))}
      </select>
      {busy && <span className="text-xs text-[#8b949e]">Switching…</span>}
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  )
}

export function SettingsPage() {
  const { connected } = useFleet()

  // Connection
  const [backendUrl, setBackendUrl] = useState(
    () => localStorage.getItem('fleet_backend_url') || DEFAULT_URL
  )
  const [urlDirty, setUrlDirty] = useState(false)

  // Sim mode
  const [simInfo, setSimInfo] = useState<{ sim_mode: boolean; version?: string } | null>(null)
  const [simLoading, setSimLoading] = useState(false)

  // OPC UA
  const [opcuaEndpoint, setOpcuaEndpoint] = useState(
    () => localStorage.getItem('fleet_opcua_endpoint') || ''
  )
  const [opcuaDirty, setOpcuaDirty] = useState(false)

  // Load backend info on mount
  useEffect(() => {
    fetch(`${backendUrl}/health`)
      .then(r => r.json())
      .then(d => setSimInfo(d))
      .catch(() => setSimInfo(null))
  }, [backendUrl])

  function saveBackendUrl() {
    localStorage.setItem('fleet_backend_url', backendUrl)
    setUrlDirty(false)
    // Reload page so SSE client picks up new URL
    window.location.reload()
  }

  async function toggleSimMode() {
    if (!simInfo) return
    setSimLoading(true)
    try {
      const res = await fetch(`${backendUrl}/config/sim_mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sim_mode: !simInfo.sim_mode }),
      })
      if (res.ok) setSimInfo(prev => prev ? { ...prev, sim_mode: !prev.sim_mode } : null)
    } catch (e) {
      console.error(e)
    } finally {
      setSimLoading(false)
    }
  }

  function saveOpcua() {
    localStorage.setItem('fleet_opcua_endpoint', opcuaEndpoint)
    setOpcuaDirty(false)
    // POST to backend so it can restart the driver
    fetch(`${backendUrl}/config/opcua`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: opcuaEndpoint }),
    }).catch(console.error)
  }

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <Settings className="w-4 h-4 text-[#58a6ff]" />
        <h1 className="text-sm font-semibold text-[#e6edf3]">Settings</h1>
        <div className={`w-2 h-2 rounded-full ml-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-xs text-[#8b949e]">{connected ? 'Connected' : 'Disconnected'}</span>
      </div>

      <div className="flex-1 overflow-auto p-6 max-w-2xl space-y-6">

        {/* Connection */}
        <Section title="Backend Connection">
          <Row label="Backend URL" sub="SSE event stream and REST API base URL">
            <div className="flex gap-2">
              <input
                className="w-52 bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-xs font-mono text-[#c9d1d9]
                  focus:outline-none focus:border-[#58a6ff]"
                value={backendUrl}
                onChange={e => { setBackendUrl(e.target.value); setUrlDirty(true) }}
              />
              {urlDirty && (
                <Button size="sm" onClick={saveBackendUrl} variant="primary">
                  <Save className="w-3 h-3 mr-1" /> Save
                </Button>
              )}
            </div>
          </Row>
          <Row label="Connection status" sub="">
            <div className="flex items-center gap-2 text-xs">
              {connected
                ? <><Wifi className="w-4 h-4 text-green-400" /><span className="text-green-400">Live</span></>
                : <><WifiOff className="w-4 h-4 text-red-400" /><span className="text-red-400">No connection</span></>
              }
              {simInfo?.version && (
                <Badge variant="outline" className="ml-2">v{simInfo.version}</Badge>
              )}
            </div>
          </Row>
        </Section>

        {/* Simulation */}
        <Section title="Simulation">
          <Row
            label="Sim Mode"
            sub="When enabled, robots are simulated; no SEER TCP connections are made">
            <div className="flex items-center gap-3">
              {simInfo ? (
                <>
                  <Toggle
                    value={simInfo.sim_mode}
                    onChange={toggleSimMode}
                    disabled={simLoading}
                  />
                  <Badge variant={simInfo.sim_mode ? 'secondary' : 'outline'}>
                    {simInfo.sim_mode ? 'Sim' : 'Hardware'}
                  </Badge>
                </>
              ) : (
                <span className="text-xs text-[#8b949e]">unavailable</span>
              )}
            </div>
          </Row>
          {simInfo && !simInfo.sim_mode && (
            <Row label="" sub="">
              <div className="flex items-center gap-2 text-xs text-[#d29922]">
                <AlertTriangle className="w-4 h-4" />
                <span>Hardware mode — real AMRs will be commanded</span>
              </div>
            </Row>
          )}
        </Section>

        {/* OPC UA */}
        <Section title="OPC UA (Call Buttons)">
          <Row label="Endpoint URL" sub="Adilson's PLC OPC UA server address">
            <div className="flex gap-2">
              <input
                className="w-56 bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-xs font-mono text-[#c9d1d9]
                  focus:outline-none focus:border-[#58a6ff] placeholder-[#8b949e]"
                placeholder="opc.tcp://10.0.0.5:4840"
                value={opcuaEndpoint}
                onChange={e => { setOpcuaEndpoint(e.target.value); setOpcuaDirty(true) }}
              />
              {opcuaDirty && (
                <Button size="sm" onClick={saveOpcua} variant="primary">
                  <Save className="w-3 h-3 mr-1" /> Apply
                </Button>
              )}
            </div>
          </Row>
          <Row label="Status" sub="">
            <span className="text-xs text-[#8b949e]">
              {opcuaEndpoint
                ? <span className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-green-500" /> Configured</span>
                : 'Not configured — buttons unavailable'}
            </span>
          </Row>
        </Section>

        {/* Facility */}
        <Section title="Facility">
          <Row label="Active facility" sub="Multi-facility support coming in a future release">
            <Badge variant="outline" className="font-mono">Piracicaba</Badge>
          </Row>
          <Row label="Map file" sub=".smap loaded by the backend — switch the active map at runtime">
            <MapSelector />
          </Row>
        </Section>

        {/* About */}
        <Section title="About">
          <Row label="Caterpillar Inc. Fleet" sub="Fleet management system for Caterpillar Piracicaba">
            <Badge variant="outline">v0.1.0 alpha</Badge>
          </Row>
          <Row label="Backend" sub="Python Flask · SEER Robokit TCP driver · asyncua">
            <span className="text-xs font-mono text-[#8b949e]">port 8765</span>
          </Row>
        </Section>
      </div>
    </div>
  )
}

