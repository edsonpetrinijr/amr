import React from "react"
import { NavLink, Outlet } from "react-router"
import { LayoutDashboard, Beaker, Play, Settings, Combine, GitBranch, TrendingUp } from "lucide-react"
import { cn } from "@/app/utils"

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Beaker, label: "Experiments", path: "/experiments" },
  { icon: Play, label: "Runs", path: "/runs" },
  { icon: GitBranch, label: "Swarm Configurations", path: "/configs" },
  { icon: Combine, label: "Comparisons", path: "/comparisons" },
  { icon: TrendingUp, label: "Training", path: "/training" },
  { icon: Settings, label: "Settings", path: "/settings" },
]

export function Layout() {
  return (
    <div className="flex h-screen w-full bg-[#0d1117] text-[#c9d1d9] font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#30363d] bg-[#0d1117] flex flex-col shrink-0">
        {/* Traffic light spacer — hiddenInset titlebar overlaps ~52px */}
        <div className="h-8 shrink-0" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties} />
        <div className="h-14 border-b border-[#30363d] flex items-center px-4">
          <div className="w-6 h-6 bg-[#58a6ff] rounded-sm mr-3 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold font-mono">BX</span>
          </div>
          <span className="font-semibold text-[#e6edf3] tracking-wide">BehaveX</span>
        </div>
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
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
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-[#30363d] text-xs text-[#8b949e] font-mono">
          <div>v2.4.1 (stable)</div>
          <div className="flex items-center gap-2 mt-1">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            Core: Online
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <Outlet />
      </main>
    </div>
  )
}
