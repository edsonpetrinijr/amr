import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import { Button } from "../components/ui/button"
import { Map, ListChecks, Bell, Battery, Bot, AlertTriangle, CheckCircle2, Clock, ArrowRight } from "lucide-react"
import { Link } from "react-router"
import { cn } from "@/app/utils"

// ── Static placeholder data (replaced by WS in Phase 2) ──────────────────────
const facility = { name: "Piracicaba", id: "piracicaba" }

const robots = [
  { id: "AMR-01", status: "idle",            battery: 94, task: null },
  { id: "AMR-02", status: "enroute_pickup",  battery: 72, task: "T0041" },
  { id: "AMR-03", status: "charging",        battery: 31, task: null },
  { id: "AMR-04", status: "offline",         battery: 0,  task: null },
]

const recentTasks = [
  { id: "T0041", pickup: "Linha A · Posto 1", dropoff: "Almox · Doca 1", robot: "AMR-02", state: "enroute_pickup", age: "2 min ago" },
  { id: "T0040", pickup: "Linha B · Posto 2", dropoff: "Almox · Doca 2", robot: "AMR-01", state: "done",           age: "18 min ago" },
  { id: "T0039", pickup: "Linha C · Posto 1", dropoff: "Expedição",       robot: "AMR-01", state: "done",           age: "42 min ago" },
]

const statusColor: Record<string, string> = {
  idle:            "bg-[#3fb950]",
  enroute_pickup:  "bg-[#58a6ff]",
  at_pickup:       "bg-[#d29922]",
  enroute_drop:    "bg-[#58a6ff]",
  charging:        "bg-[#d29922]",
  error:           "bg-[#f85149]",
  offline:         "bg-[#6e7681]",
}

const statusLabel: Record<string, string> = {
  idle:           "Idle",
  enroute_pickup: "En Route",
  at_pickup:      "At Pickup",
  enroute_drop:   "Delivering",
  charging:       "Charging",
  error:          "Error",
  offline:        "Offline",
}

const taskStateColor: Record<string, string> = {
  enroute_pickup: "text-[#58a6ff]",
  at_pickup:      "text-[#d29922]",
  enroute_drop:   "text-[#58a6ff]",
  done:           "text-[#3fb950]",
  failed:         "text-[#f85149]",
  cancelled:      "text-[#6e7681]",
}

export function Dashboard() {
  const online   = robots.filter(r => r.status !== "offline").length
  const active   = robots.filter(r => r.status === "enroute_pickup" || r.status === "enroute_drop" || r.status === "at_pickup").length
  const charging = robots.filter(r => r.status === "charging").length
  const errors   = robots.filter(r => r.status === "error").length

  return (
    <div className="flex-1 overflow-auto bg-[#0d1117] p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <p className="text-xs font-mono text-[#8b949e] uppercase tracking-widest mb-1">Fleet Dashboard</p>
          <h1 className="text-2xl font-bold text-[#e6edf3]">{facility.name}</h1>
          <p className="text-[#8b949e] text-sm mt-1">AMR fleet overview — real-time via WS (Phase 2)</p>
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
                {robots.map(r => (
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
                        {r.battery}%
                      </span>
                      {r.task && (
                        <Link to="/tasks">
                          <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0 h-4">{r.task}</Badge>
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
                {recentTasks.map(t => (
                  <div key={t.id} className="px-4 py-3 hover:bg-[#21262d]/40 transition-colors">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-[#8b949e]">{t.id}</span>
                      <div className="flex items-center gap-2">
                        {t.state === "done"
                          ? <CheckCircle2 className="w-3.5 h-3.5 text-[#3fb950]" />
                          : <Clock className="w-3.5 h-3.5 text-[#58a6ff]" />
                        }
                        <span className={cn("text-xs font-mono capitalize", taskStateColor[t.state])}>
                          {t.state.replace(/_/g, " ")}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-[#c9d1d9]">{t.pickup}</span>
                      <ArrowRight className="w-3 h-3 text-[#6e7681] shrink-0" />
                      <span className="text-[#c9d1d9]">{t.dropoff}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-[#8b949e]">
                      <span className="font-mono">{t.robot}</span>
                      <span>{t.age}</span>
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

