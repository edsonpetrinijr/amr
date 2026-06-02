import React, { useState } from 'react'
import { Cpu, Bot, MapPin, Bell, Zap, RefreshCw } from 'lucide-react'
import { useFleet } from '../state/store'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'


// ── Robot tab ─────────────────────────────────────────────────────────────────

function RobotsTab() {
  const { robots } = useFleet()

  const battColor = (b: number) =>
    b < 25 ? 'text-red-400' : b < 50 ? 'text-yellow-400' : 'text-green-400'

  type BadgeVariant = 'default' | 'outline' | 'success' | 'destructive' | 'secondary'
  const STATUS_V: Record<string, BadgeVariant> = {
    idle: 'outline', charging: 'secondary', error: 'destructive',
    offline: 'destructive', enroute_pickup: 'default', enroute_drop: 'default',
    at_pickup: 'secondary', returning: 'secondary',
  }

  return (
    <div className="overflow-auto">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#161b22] border-b border-[#30363d]">
          <tr className="text-[#8b949e]">
            {['ID', 'IP', 'Status', 'Battery', 'Position', 'Current Task', 'Last Seen'].map(h => (
              <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {robots.map(r => (
            <tr key={r.id} className="border-b border-[#21262d] hover:bg-[#161b22]">
              <td className="px-4 py-2 font-mono text-[#e6edf3]">{r.id}</td>
              <td className="px-4 py-2 font-mono text-[#8b949e]">{r.ip || '—'}</td>
              <td className="px-4 py-2">
                <Badge variant={STATUS_V[r.status] ?? 'outline'}>{r.status.replace('_', ' ')}</Badge>
              </td>
              <td className={`px-4 py-2 font-mono ${battColor(r.battery)}`}>{r.battery.toFixed(0)}%</td>
              <td className="px-4 py-2 font-mono text-[#8b949e]">
                ({r.x.toFixed(2)}, {r.y.toFixed(2)}, {(r.theta * 180 / Math.PI).toFixed(0)}°)
              </td>
              <td className="px-4 py-2 font-mono text-[#c9d1d9]">{r.current_task ?? '—'}</td>
              <td className="px-4 py-2 text-[#8b949e]">
                {new Date(r.last_seen * 1000).toLocaleTimeString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Stations tab ──────────────────────────────────────────────────────────────

const TYPE_ICON: Record<string, React.ReactNode> = {
  callbutton: <Bell className="w-3.5 h-3.5" />,
  base:       <Zap  className="w-3.5 h-3.5" />,
  ap:         <MapPin className="w-3.5 h-3.5" />,
}

const CB_V: Record<string, 'default' | 'outline' | 'success' | 'destructive' | 'secondary'> = {
  idle: 'outline', called: 'default', acknowledged: 'secondary', served: 'success',
}

function StationsTab({ type }: { type: 'callbutton' | 'base' | 'ap' }) {
  const { stations } = useFleet()
  const filtered = stations.filter(s => s.type === type)

  return (
    <div className="overflow-auto">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#161b22] border-b border-[#30363d]">
          <tr className="text-[#8b949e]">
            {['ID', 'Label', 'SEER LM', 'AP ID', 'OPC UA Node', 'Position',
              type === 'callbutton' ? 'CB State' : 'Type'].map(h => (
              <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filtered.map(s => (
            <tr key={s.id} className="border-b border-[#21262d] hover:bg-[#161b22]">
              <td className="px-4 py-2 font-mono text-[#e6edf3]">{s.id}</td>
              <td className="px-4 py-2 text-[#c9d1d9]">{s.label}</td>
              <td className="px-4 py-2 font-mono text-[#58a6ff]">{s.seer_lm ?? '—'}</td>
              <td className="px-4 py-2 font-mono text-[#8b949e]">{s.ap_id ?? '—'}</td>
              <td className="px-4 py-2 font-mono text-[#8b949e] text-[10px]">{s.opcua_node ?? '—'}</td>
              <td className="px-4 py-2 font-mono text-[#8b949e]">
                ({s.x.toFixed(1)}, {s.y.toFixed(1)})
              </td>
              <td className="px-4 py-2">
                {type === 'callbutton'
                  ? <Badge variant={CB_V[s.cb_state] ?? 'outline'}>{s.cb_state}</Badge>
                : <span className="flex items-center gap-1 text-[#8b949e]">{TYPE_ICON[s.type]}<span className="capitalize">{s.type}</span></span>
                }
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-[#8b949e]">No stations configured</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

// ── Map info tab ──────────────────────────────────────────────────────────────

function MapTab() {
  const { map } = useFleet()
  if (!map) return (
    <div className="flex items-center justify-center h-64 text-[#8b949e] text-sm">
      No map loaded
    </div>
  )
  return (
    <div className="p-6 grid grid-cols-2 gap-4 text-xs max-w-2xl">
      {[
        ['Name',       map.name],
        ['Type',       map.map_type],
        ['Version',    map.version],
        ['Resolution', `${map.resolution} m/px`],
        ['Extents X',  `${map.min_pos.x.toFixed(2)} → ${map.max_pos.x.toFixed(2)} m`],
        ['Extents Y',  `${map.min_pos.y.toFixed(2)} → ${map.max_pos.y.toFixed(2)} m`],
        ['Walls',      String(map.walls.length)],
        ['Nav points', String(map.nav_points.length)],
        ['Action pts', String(map.action_points.length)],
        ['Landmarks',  String(map.landmarks.length)],
        ['Areas',      String(map.areas.length)],
      ].map(([label, val]) => (
        <div key={label} className="flex gap-3 items-baseline">
          <span className="text-[#8b949e] w-32 flex-shrink-0">{label}</span>
          <span className="font-mono text-[#e6edf3]">{val}</span>
        </div>
      ))}
    </div>
  )
}

// ── Root ──────────────────────────────────────────────────────────────────────

type TabId = 'robots' | 'callbuttons' | 'aps' | 'bases' | 'map'

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: 'robots',      label: 'Robots',      icon: <Bot    className="w-4 h-4" /> },
  { id: 'callbuttons', label: 'Call buttons', icon: <Bell   className="w-4 h-4" /> },
  { id: 'aps',         label: 'Action points',icon: <MapPin className="w-4 h-4" /> },
  { id: 'bases',       label: 'Bases / Charge',icon:<Zap   className="w-4 h-4" /> },
  { id: 'map',         label: 'Map info',     icon: <Cpu    className="w-4 h-4" /> },
]

export function Devices() {
  const [tab, setTab] = useState<TabId>('robots')
  const { robots, stations, map, connected } = useFleet()

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <Cpu className="w-4 h-4 text-[#58a6ff]" />
        <h1 className="text-sm font-semibold text-[#e6edf3]">Devices</h1>
        <div className={`w-2 h-2 rounded-full ml-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-xs text-[#8b949e]">
          {robots.length} robots · {stations.length} stations{map ? ` · ${map.name}` : ''}
        </span>
        <div className="ml-auto">
          <Button variant="ghost" size="sm" onClick={() => window.location.reload()}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-[#30363d] px-4 gap-1 flex-shrink-0 bg-[#0d1117]">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs transition-colors border-b-2 -mb-px
              ${tab === t.id
                ? 'border-[#58a6ff] text-[#e6edf3]'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'}`}>
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-auto">
        {tab === 'robots'      && <RobotsTab />}
        {tab === 'callbuttons' && <StationsTab type="callbutton" />}
        {tab === 'aps'         && <StationsTab type="ap" />}
        {tab === 'bases'       && <StationsTab type="base" />}
        {tab === 'map'         && <MapTab />}
      </div>
    </div>
  )
}

