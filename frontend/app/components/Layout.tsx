import React from "react"
import { NavLink, Outlet } from "react-router"
import { LayoutDashboard, Map, Cpu, Wrench, ListChecks, Bell, Settings } from "lucide-react"
import { cn } from "@/app/utils"
import { useFleet } from "@/app/state/store"

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard",    path: "/" },
  { icon: Map,             label: "Field View",   path: "/field" },
  { icon: ListChecks,      label: "Tasks",        path: "/tasks" },
  { icon: Bell,            label: "Call Buttons", path: "/callbuttons" },
  { icon: Cpu,             label: "Devices",      path: "/devices" },
  { icon: Wrench,          label: "Calibration",  path: "/calibration" },
  { icon: Settings,        label: "Settings",     path: "/settings" },
]

export function Layout() {
  const { connected, robots, tasks } = useFleet()

  const activeRobots = robots.filter(r => r.status !== 'idle' && r.status !== 'offline' && r.status !== 'charging').length
  const activeTasks  = tasks.filter(t => !['done','cancelled','failed'].includes(t.state)).length

  return (
    <div className="flex h-screen w-full bg-[#0d1117] text-[#c9d1d9] font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#30363d] bg-[#0d1117] flex flex-col shrink-0">
        {/* Traffic light spacer */}
        <div className="h-8 shrink-0" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties} />
        <div className="h-14 border-b border-[#30363d] flex items-center px-4">
          <div className="w-6 h-6 bg-[#58a6ff] rounded-sm mr-3 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold font-mono">AF</span>
          </div>
          <span className="font-semibold text-[#e6edf3] tracking-wide">Caterpillar Inc. Fleet</span>
        </div>
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-[#21262d] text-[#e6edf3]"
                    : "text-[#8b949e] hover:bg-[#21262d]/50 hover:text-[#c9d1d9]"
                )
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
              {/* Badge for Call Buttons with active calls */}
              {item.path === "/callbuttons" && activeTasks > 0 && (
                <span className="ml-auto bg-[#1f6feb] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                  {activeTasks}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        {/* Footer — facility + connection status */}
        <div className="p-4 border-t border-[#30363d] text-xs text-[#8b949e] font-mono space-y-1.5">
          <div className="text-[#c9d1d9] font-medium text-sm">🏭 Piracicaba</div>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full shrink-0 ${connected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`} />
            <span className={connected ? 'text-green-400' : 'text-red-400'}>
              {connected ? 'Backend live' : 'Connecting…'}
            </span>
          </div>
          <div className="flex gap-3">
            <span>{robots.length} robots</span>
            {activeRobots > 0 && <span className="text-[#58a6ff]">{activeRobots} active</span>}
          </div>
          <div className="text-[#6e7681]">v0.1.0 alpha</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <Outlet />
      </main>
    </div>
  )
}
