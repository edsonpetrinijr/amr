import React, { useState } from 'react'
import { ListChecks, Plus, X } from 'lucide-react'
import { useFleet } from '../state/store'
import { fleetApi } from '../api/fleet'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import type { Task } from '../api/types'

const STATE_VARIANT: Record<string, 'success' | 'destructive' | 'default' | 'secondary' | 'outline'> = {
  pending:        'outline',
  assigned:       'default',
  enroute_pickup: 'default',
  at_pickup:      'secondary',
  enroute_drop:   'default',
  done:           'success',
  cancelled:      'secondary',
  failed:         'destructive',
}

function elapsed(ts: number | null) {
  if (!ts) return '—'
  const s = Math.floor((Date.now() / 1000) - ts)
  if (s < 60)  return `${s}s ago`
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  return `${Math.floor(s / 3600)}h ago`
}

function TaskRow({ task, onCancel }: { task: Task; onCancel?: (id: string) => void }) {
  const active = !['done', 'cancelled', 'failed'].includes(task.state)
  return (
    <tr className="border-b border-[#21262d] hover:bg-[#161b22] transition-colors text-xs">
      <td className="px-3 py-2 font-mono text-[#8b949e]">{task.id.slice(-8)}</td>
      <td className="px-3 py-2 text-[#c9d1d9]">{task.pickup}</td>
      <td className="px-3 py-2 text-[#c9d1d9]">{task.dropoff}</td>
      <td className="px-3 py-2">
        <Badge variant={STATE_VARIANT[task.state] ?? 'outline'}>
          {task.state.replace('_', ' ')}
        </Badge>
      </td>
      <td className="px-3 py-2 text-[#8b949e] font-mono">{task.robot ?? '—'}</td>
      <td className="px-3 py-2 text-[#8b949e]">{elapsed(task.created_at)}</td>
      <td className="px-3 py-2">
        {active && onCancel && (
          <button onClick={() => onCancel(task.id)}
            className="text-[#8b949e] hover:text-red-400 transition-colors">
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </td>
    </tr>
  )
}

export function Tasks() {
  const { allTasks, stations, robots, connected } = useFleet()
  const [showForm, setShowForm] = useState(false)
  const [pickup,   setPickup]   = useState('')
  const [dropoff,  setDropoff]  = useState('')
  const [sending,  setSending]  = useState(false)
  const [filter,   setFilter]   = useState<'all' | 'active' | 'done'>('all')

  const aps = stations.filter(s => s.type !== 'base')
  const filtered = allTasks.filter(t => {
    if (filter === 'active') return !['done', 'cancelled', 'failed'].includes(t.state)
    if (filter === 'done')   return  ['done', 'cancelled', 'failed'].includes(t.state)
    return true
  })

  async function handleCreate() {
    if (!pickup || !dropoff) return
    setSending(true)
    try {
      await fleetApi.createTask(pickup, dropoff)
      setPickup(''); setDropoff(''); setShowForm(false)
    } catch (e) { console.error(e) }
    finally { setSending(false) }
  }

  async function handleCancel(id: string) {
    try { await fleetApi.cancelTask(id) }
    catch (e) { console.error(e) }
  }

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <ListChecks className="w-4 h-4 text-[#58a6ff]" />
        <h1 className="text-sm font-semibold text-[#e6edf3]">Tasks</h1>
        <div className={`w-2 h-2 rounded-full ml-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-xs text-[#8b949e]">{allTasks.length} total</span>

        {/* Filter tabs */}
        <div className="ml-4 flex gap-1">
          {(['all', 'active', 'done'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-2 py-0.5 rounded text-xs transition-colors ${
                filter === f
                  ? 'bg-[#21262d] text-[#e6edf3] border border-[#58a6ff]'
                  : 'text-[#8b949e] hover:text-[#c9d1d9]'}`}>
              {f}
            </button>
          ))}
        </div>

        <div className="ml-auto">
          <Button variant="primary" size="sm" onClick={() => setShowForm(v => !v)}>
            <Plus className="w-3.5 h-3.5 mr-1" />
            New task
          </Button>
        </div>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 bg-[#161b22] flex-shrink-0">
          <select className="text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1"
            value={pickup} onChange={e => setPickup(e.target.value)}>
            <option value="">Pickup station…</option>
            {aps.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
          </select>
          <span className="text-[#8b949e] text-xs">→</span>
          <select className="text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1"
            value={dropoff} onChange={e => setDropoff(e.target.value)}>
            <option value="">Drop-off station…</option>
            {aps.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
          </select>
          <Button variant="primary" size="sm" disabled={!pickup || !dropoff || sending} onClick={handleCreate}>
            {sending ? 'Creating…' : 'Create'}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>Cancel</Button>
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {filtered.length === 0 ? (
          <div className="h-full flex items-center justify-center text-[#8b949e] text-sm">
            No tasks yet
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[#161b22] border-b border-[#30363d]">
              <tr className="text-[#8b949e]">
                <th className="px-3 py-2 text-left font-medium">ID</th>
                <th className="px-3 py-2 text-left font-medium">Pickup</th>
                <th className="px-3 py-2 text-left font-medium">Drop-off</th>
                <th className="px-3 py-2 text-left font-medium">State</th>
                <th className="px-3 py-2 text-left font-medium">Robot</th>
                <th className="px-3 py-2 text-left font-medium">Created</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {filtered.map(t => <TaskRow key={t.id} task={t} onCancel={handleCancel} />)}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

