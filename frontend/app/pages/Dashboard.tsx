import React, { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import { Button } from "../components/ui/button"
import { Map, ListChecks, Bell, Battery, Bot, AlertTriangle, CheckCircle2, Clock, ArrowRight, XCircle, Gauge, Timer } from "lucide-react"
import { Link } from "react-router"
import { cn } from "@/app/utils"
import { useFleet } from "../state/store"
import { fleetApi } from "../api/fleet"
import type { Station, Task, StatsSummary } from "../api/types"

const facility = { name: "Piracicaba", id: "piracicaba" }

const ACTIVE_ROBOT_STATES = ["enroute_pickup", "enroute_drop", "at_pickup", "returning"]

const statusColor: Record<string, string> = {
  idle:            "bg-[#3fb950]",
  enroute_pickup:  "bg-[#58a6ff]",
  at_pickup:       "bg-[#d29922]",
  enroute_drop:    "bg-[#58a6ff]",
  returning:       "bg-[#58a6ff]",
  charging:        "bg-[#d29922]",
  error:           "bg-[#f85149]",
  offline:         "bg-[#6e7681]",
}

const statusLabel: Record<string, string> = {
  idle:           "Idle",
  enroute_pickup: "En Route",
  at_pickup:      "At Pickup",
  enroute_drop:   "Delivering",
  returning:      "Returning",
  charging:       "Charging",
  error:          "Error",
  offline:        "Offline",
}

const taskStateColor: Record<string, string> = {
  pending:        "text-[#8b949e]",
  assigned:       "text-[#58a6ff]",
  enroute_pickup: "text-[#58a6ff]",
  at_pickup:      "text-[#d29922]",
  enroute_drop:   "text-[#58a6ff]",
  done:           "text-[#3fb950]",
  failed:         "text-[#f85149]",
  cancelled:      "text-[#6e7681]",
}

function elapsed(ts: number | null) {
  if (!ts) return "—"
  const s = Math.floor((Date.now() / 1000) - ts)
  if (s < 60)   return `${s}s ago`
  if (s < 3600) return `${Math.floor(s / 60)} min ago`
  return `${Math.floor(s / 3600)}h ago`
}

export function Dashboard() {
  const { robots, allTasks, stations, connected } = useFleet()

  // Live analytics from /stats/summary — refreshed on an interval and whenever a
  // task update lands (allTasks changes). Gracefully null when backend is down.
  const [stats, setStats] = useState<StatsSummary | null>(null)
  const [statsError, setStatsError] = useState(false)

  useEffect(() => {
    let alive = true
    const load = () => {
      fleetApi.getStatsSummary()
        .then(s => { if (alive) { setStats(s); setStatsError(false) } })
        .catch(() => { if (alive) setStatsError(true) })
    }
    load()
    const id = setInterval(load, 8000)
    return () => { alive = false; clearInterval(id) }
    // Refetch promptly when a task transitions (SSE → allTasks).
  }, [allTasks.length])

  const online   = robots.filter(r => r.status !== "offline").length
  const active   = robots.filter(r => ACTIVE_ROBOT_STATES.includes(r.status)).length
  const charging = robots.filter(r => r.status === "charging").length
  const errors   = robots.filter(r => r.status === "error").length

  const stationLabel = (id: string) => stations.find((s: Station) => s.id === id)?.label ?? id

  const recentTasks = [...allTasks]
    .sort((a, b) => (b.created_at ?? 0) - (a.created_at ?? 0))
    .slice(0, 6)

  const waiting = !connected && robots.length === 0

  return (
    <div className="flex-1 overflow-auto bg-[#0d1117] p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <p className="text-xs font-mono text-[#8b949e] uppercase tracking-widest mb-1">Fleet Dashboard</p>
          <h1 className="text-2xl font-bold text-[#e6edf3]">{facility.name}</h1>
          <p className="text-[#8b949e] text-sm mt-1">
            AMR fleet overview · {connected ? "live" : "waiting for fleet…"}
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/field">
            <Button variant="outline" className="flex items-center gap-2">
              <Map className="w-4 h-4" />
              Field View
            </Button>
          </Link>
          <Link to="/tasks">
            <Button variant="outline" className="flex items-center gap-2">
              <ListChecks className="w-4 h-4" />
              All Tasks
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard label="Online"   value={online}   total={robots.length} color="#3fb950" icon={<Bot className="w-4 h-4" />} />
        <KpiCard label="Active"   value={active}   total={online}        color="#58a6ff" icon={<ArrowRight className="w-4 h-4" />} />
        <KpiCard label="Charging" value={charging} total={robots.length} color="#d29922" icon={<Battery className="w-4 h-4" />} />
        <KpiCard label="Errors"   value={errors}   total={robots.length} color="#f85149" icon={<AlertTriangle className="w-4 h-4" />} />
      </div>

      {/* Analytics strip — /stats/summary */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[10px] font-mono text-[#8b949e] uppercase tracking-widest">Today's Analytics</p>
          {stats?.halted && (
            <span className="text-[10px] font-mono uppercase tracking-wide text-[#f85149] flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> Fleet halted
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard label="Completed Today" value={fmtNum(stats?.tasks_completed_today)} color="#3fb950"
            icon={<CheckCircle2 className="w-4 h-4" />} loading={!stats} error={statsError} />
          <StatCard label="Failed Today" value={fmtNum(stats?.tasks_failed_today)} color="#f85149"
            icon={<XCircle className="w-4 h-4" />} loading={!stats} error={statsError} />
          <StatCard label="Avg Duration" value={fmtDuration(stats?.avg_task_duration_s)} color="#58a6ff"
            icon={<Timer className="w-4 h-4" />} loading={!stats} error={statsError} />
          <StatCard label="Utilization" value={fmtPct(stats?.fleet_utilization)} color="#d29922"
            icon={<Gauge className="w-4 h-4" />} loading={!stats} error={statsError}
            sub={stats ? `${stats.fleet_active}/${stats.fleet_total} active` : undefined} />
          <StatCard label="Avg Battery" value={stats?.avg_battery != null ? `${stats.avg_battery.toFixed(0)}%` : "—"} color="#3fb950"
            icon={<Battery className="w-4 h-4" />} loading={!stats} error={statsError} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Robot fleet list */}
        <div className="xl:col-span-1">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Bot className="w-4 h-4 text-[#8b949e]" />
                Fleet ({robots.length} robots)
              </CardTitle>
              <Link to="/devices" className="text-xs text-[#58a6ff] hover:underline">Configure →</Link>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-[#30363d]">
                {robots.length === 0 ? (
                  <div className="px-4 py-8 text-center text-xs text-[#8b949e]">
                    {waiting ? "Waiting for fleet…" : "No robots connected"}
                  </div>
                ) : robots.map(r => (
                  <div key={r.id} className="flex items-center justify-between px-4 py-3 hover:bg-[#21262d]/40 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={cn("w-2 h-2 rounded-full shrink-0", statusColor[r.status] ?? "bg-[#6e7681]")} />
                      <div>
                        <p className="text-sm font-mono text-[#e6edf3]">{r.id}</p>
                        <p className="text-xs text-[#8b949e] mt-0.5">{statusLabel[r.status] ?? r.status}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Battery className="w-3 h-3 text-[#8b949e]" />
                      <span className={cn("text-xs font-mono", r.battery < 25 ? "text-[#f85149]" : "text-[#8b949e]")}>
                        {r.battery.toFixed(0)}%
                      </span>
                      {r.current_task && (
                        <Link to="/tasks">
                          <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0 h-4">{r.current_task.slice(-8)}</Badge>
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent tasks */}
        <div className="xl:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <ListChecks className="w-4 h-4 text-[#8b949e]" />
                Recent Tasks
              </CardTitle>
              <Link to="/tasks" className="text-xs text-[#58a6ff] hover:underline">All tasks →</Link>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-[#30363d]">
                {recentTasks.length === 0 ? (
                  <div className="px-4 py-8 text-center text-xs text-[#8b949e]">
                    {waiting ? "Waiting for fleet…" : "No tasks yet"}
                  </div>
                ) : recentTasks.map((t: Task) => (
                  <div key={t.id} className="px-4 py-3 hover:bg-[#21262d]/40 transition-colors">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-[#8b949e]">{t.id.slice(-8)}</span>
                      <div className="flex items-center gap-2">
                        {t.state === "done"
                          ? <CheckCircle2 className="w-3.5 h-3.5 text-[#3fb950]" />
                          : <Clock className="w-3.5 h-3.5 text-[#58a6ff]" />
                        }
                        <span className={cn("text-xs font-mono capitalize", taskStateColor[t.state] ?? "text-[#8b949e]")}>
                          {t.state.replace(/_/g, " ")}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-[#c9d1d9]">{stationLabel(t.pickup)}</span>
                      <ArrowRight className="w-3 h-3 text-[#6e7681] shrink-0" />
                      <span className="text-[#c9d1d9]">{stationLabel(t.dropoff)}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-[#8b949e]">
                      <span className="font-mono">{t.robot ?? "—"}</span>
                      <span>{elapsed(t.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick actions */}
          <Card className="mt-6">
            <CardHeader className="py-3">
              <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="p-4 grid grid-cols-2 gap-2">
              <Link to="/field">
                <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                  <Map className="w-3 h-3 mr-2" /> Open Field View
                </Button>
              </Link>
              <Link to="/callbuttons">
                <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                  <Bell className="w-3 h-3 mr-2" /> Call Buttons
                </Button>
              </Link>
              <Link to="/calibration">
                <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                  <ArrowRight className="w-3 h-3 mr-2" /> Calibrate Robot
                </Button>
              </Link>
              <Link to="/devices">
                <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                  <Bot className="w-3 h-3 mr-2" /> Manage Devices
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ label, value, total, color, icon }: { label: string; value: number; total: number; color: string; icon: React.ReactNode }) {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex items-center gap-4">
      <div className="w-8 h-8 rounded-md flex items-center justify-center shrink-0" style={{ background: color + "22", color }}>
        {icon}
      </div>
      <div>
        <p className="text-[10px] font-mono text-[#8b949e] uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold font-mono text-[#e6edf3]">
          {value}
          <span className="text-sm text-[#8b949e] ml-1">/ {total}</span>
        </p>
      </div>
    </div>
  )
}

// ── Analytics helpers ─────────────────────────────────────────────────────────

function fmtNum(n: number | null | undefined): string {
  return n == null ? "—" : String(n)
}
function fmtPct(n: number | null | undefined): string {
  return n == null ? "—" : `${Math.round(n * 100)}%`
}
function fmtDuration(s: number | null | undefined): string {
  if (s == null) return "—"
  if (s < 60) return `${Math.round(s)}s`
  const m = Math.floor(s / 60)
  const rem = Math.round(s % 60)
  return `${m}m ${rem}s`
}

function StatCard({ label, value, color, icon, loading, error, sub }: {
  label: string; value: string; color: string; icon: React.ReactNode
  loading?: boolean; error?: boolean; sub?: string
}) {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex items-center gap-4">
      <div className="w-8 h-8 rounded-md flex items-center justify-center shrink-0" style={{ background: color + "22", color }}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[10px] font-mono text-[#8b949e] uppercase tracking-wider truncate">{label}</p>
        <p className="text-2xl font-bold font-mono text-[#e6edf3] leading-tight">
          {error ? <span className="text-sm text-[#f85149]">offline</span>
            : loading ? <span className="text-sm text-[#6e7681]">…</span>
            : value}
        </p>
        {sub && !loading && !error && (
          <p className="text-[10px] font-mono text-[#6e7681] mt-0.5 truncate">{sub}</p>
        )}
      </div>
    </div>
  )
}

