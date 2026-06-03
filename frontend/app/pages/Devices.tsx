import React, { useState } from 'react'
import { Cpu, Bot, MapPin, Bell, Zap, RefreshCw, Plus, Pencil, Trash2, Loader2, Wifi } from 'lucide-react'
import { useFleet } from '../state/store'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle,
  AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction,
} from '../components/ui/alert-dialog'
import { RobotEditDialog } from '../components/RobotEditDialog'
import { PulledInfo } from '../components/PulledInfo'
import { CallbuttonStationRow } from '../components/CallbuttonStationRow'
import { fleetApi, FleetApiError } from '../api/fleet'
import type { Robot, ProbeResult } from '../api/types'


// ── Robot tab ─────────────────────────────────────────────────────────────────

function ConnDot({ connected }: { connected: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${connected ? 'bg-[#3fb950]' : 'bg-[#f85149]'}`} />
      <span className={connected ? 'text-[#3fb950]' : 'text-[#8b949e]'}>
        {connected ? 'online' : 'offline'}
      </span>
    </span>
  )
}

function RobotsTab() {
  const { robots } = useFleet()
  const [addOpen, setAddOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Robot | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Robot | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [probing, setProbing] = useState<string | null>(null)
  const [probeResults, setProbeResults] = useState<Record<string, ProbeResult>>({})
  const [probeErrors, setProbeErrors] = useState<Record<string, string>>({})

  const battColor = (b: number) =>
    b < 25 ? 'text-red-400' : b < 50 ? 'text-yellow-400' : 'text-green-400'

  type BadgeVariant = 'default' | 'outline' | 'success' | 'destructive' | 'secondary'
  const STATUS_V: Record<string, BadgeVariant> = {
    idle: 'outline', charging: 'secondary', error: 'destructive',
    offline: 'destructive', enroute_pickup: 'default', enroute_drop: 'default',
    at_pickup: 'secondary', returning: 'secondary',
  }

  // SSE world snapshots keep the table live — onSaved just nudges a fetch so we
  // surface backend state quickly even between pushes.
  const refresh = () => { fleetApi.getRobots().catch(() => {}) }

  async function handleProbe(id: string) {
    setProbing(id)
    setProbeErrors(p => { const n = { ...p }; delete n[id]; return n })
    try {
      const res = await fleetApi.probeRobot(id)
      setProbeResults(p => ({ ...p, [id]: res }))
    } catch (e) {
      setProbeErrors(p => ({ ...p, [id]: e instanceof FleetApiError ? e.message : 'Probe failed' }))
    } finally {
      setProbing(null)
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return
    setDeleting(true)
    setDeleteError(null)
    try {
      await fleetApi.deleteRobot(deleteTarget.id)
      refresh()
      setDeleteTarget(null)
    } catch (e) {
      setDeleteError(e instanceof FleetApiError ? e.message : 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="overflow-auto">
      <div className="flex items-center justify-between px-4 py-3">
        <span className="text-xs text-[#8b949e]">{robots.length} robots</span>
        <Button variant="primary" size="sm" onClick={() => setAddOpen(true)}>
          <Plus className="w-3.5 h-3.5 mr-1" />
          Add robot
        </Button>
      </div>

      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#161b22] border-b border-[#30363d]">
          <tr className="text-[#8b949e]">
            {['ID', 'Name', 'Model', 'IP', 'Conn', 'Status', 'Battery', 'Position', 'Last Seen', ''].map(h => (
              <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {robots.map(r => (
            <React.Fragment key={r.id}>
              <tr className="border-b border-[#21262d] hover:bg-[#161b22]">
                <td className="px-4 py-2 font-mono text-[#e6edf3]">{r.id}</td>
                <td className="px-4 py-2 text-[#c9d1d9]">{r.name || '—'}</td>
                <td className="px-4 py-2 font-mono text-[#8b949e]">{r.model || '—'}</td>
                <td className="px-4 py-2 font-mono text-[#8b949e]">{r.ip || '—'}</td>
                <td className="px-4 py-2"><ConnDot connected={r.connected} /></td>
                <td className="px-4 py-2">
                  <Badge variant={STATUS_V[r.status] ?? 'outline'}>{r.status.replace('_', ' ')}</Badge>
                </td>
                <td className={`px-4 py-2 font-mono ${battColor(r.battery)}`}>{r.battery.toFixed(0)}%</td>
                <td className="px-4 py-2 font-mono text-[#8b949e]">
                  ({r.x.toFixed(2)}, {r.y.toFixed(2)}, {(r.theta * 180 / Math.PI).toFixed(0)}°)
                </td>
                <td className="px-4 py-2 text-[#8b949e]">
                  {new Date(r.last_seen * 1000).toLocaleTimeString()}
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-1 justify-end">
                    <Button variant="ghost" size="sm" onClick={() => handleProbe(r.id)} disabled={probing === r.id}
                      title="Test / re-probe">
                      {probing === r.id
                        ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        : <Wifi className="w-3.5 h-3.5" />}
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setEditTarget(r)} title="Edit">
                      <Pencil className="w-3.5 h-3.5" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => { setDeleteTarget(r); setDeleteError(null) }}
                      title="Delete" className="hover:text-[#ff7b72]">
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </td>
              </tr>
              {(probeResults[r.id] || probeErrors[r.id]) && (
                <tr className="border-b border-[#21262d] bg-[#0d1117]">
                  <td colSpan={10} className="px-4 py-2">
                    {probeErrors[r.id]
                      ? <div className="text-xs text-[#ff7b72]">{probeErrors[r.id]}</div>
                      : <PulledInfo connected={probeResults[r.id].connected} pulled={probeResults[r.id].pulled} />}
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
          {robots.length === 0 && (
            <tr><td colSpan={10} className="px-4 py-8 text-center text-[#8b949e]">No robots configured</td></tr>
          )}
        </tbody>
      </table>

      <RobotEditDialog mode="add" open={addOpen} onOpenChange={setAddOpen} onSaved={refresh} />
      {editTarget && (
        <RobotEditDialog mode="edit" robot={editTarget}
          open={!!editTarget} onOpenChange={(o) => { if (!o) setEditTarget(null) }} onSaved={refresh} />
      )}

      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => { if (!o) setDeleteTarget(null) }}>
        <AlertDialogContent className="bg-[#161b22] border-[#30363d] text-[#e6edf3]">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {deleteTarget?.id}?</AlertDialogTitle>
            <AlertDialogDescription className="text-[#8b949e]">
              This removes the robot from the fleet. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          {deleteError && <div className="text-xs text-[#ff7b72]">{deleteError}</div>}
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={(e) => { e.preventDefault(); handleDelete() }} disabled={deleting}
              className="bg-[#da3633] text-white hover:bg-[#f85149] border-[#f85149]/30">
              {deleting && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

// ── Stations tab ──────────────────────────────────────────────────────────────

const TYPE_ICON: Record<string, React.ReactNode> = {
  callbutton: <Bell className="w-3.5 h-3.5" />,
  base:       <Zap  className="w-3.5 h-3.5" />,
  ap:         <MapPin className="w-3.5 h-3.5" />,
}

function StationsTab({ type }: { type: 'callbutton' | 'base' | 'ap' }) {
  const { stations } = useFleet()
  const filtered = stations.filter(s => s.type === type)
  const isCb = type === 'callbutton'

  const headers = isCb
    ? ['ID', 'Label', 'SEER LM', 'AP ID', 'OPC UA Node', 'Position', 'CB State', 'Test']
    : ['ID', 'Label', 'SEER LM', 'AP ID', 'OPC UA Node', 'Position', 'Type']

  return (
    <div className="overflow-auto">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#161b22] border-b border-[#30363d]">
          <tr className="text-[#8b949e]">
            {headers.map(h => (
              <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isCb && filtered.map(s => (
            <CallbuttonStationRow key={s.id} station={s} />
          ))}
          {!isCb && filtered.map(s => (
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
                <span className="flex items-center gap-1 text-[#8b949e]">{TYPE_ICON[s.type]}<span className="capitalize">{s.type}</span></span>
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr><td colSpan={headers.length} className="px-4 py-8 text-center text-[#8b949e]">No stations configured</td></tr>
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

