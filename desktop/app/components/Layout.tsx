import React, { useCallback, useEffect, useRef, useState } from "react"
import { NavLink, Outlet, useNavigate } from "react-router"
import { LayoutDashboard, Map, Cpu, Wrench, ListChecks, Bell, Settings, OctagonX, Play, ShieldAlert } from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/app/utils"
import { useFleet } from "@/app/state/store"
import { fleetApi } from "@/app/api/fleet"
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader,
  AlertDialogFooter, AlertDialogTitle, AlertDialogDescription,
  AlertDialogAction, AlertDialogCancel,
} from "@/app/components/ui/alert-dialog"

const navItems = [
  { icon: LayoutDashboard, label: "Painel",          path: "/" },
  { icon: Map,             label: "Visão de Campo",   path: "/field" },
  { icon: ListChecks,      label: "Tarefas",          path: "/tasks" },
  { icon: Bell,            label: "Botões de Chamada", path: "/callbuttons" },
  { icon: Cpu,             label: "Dispositivos",     path: "/devices" },
  { icon: Wrench,          label: "Calibração",       path: "/calibration" },
  { icon: Settings,        label: "Configurações",    path: "/settings" },
]

export function Layout() {
  const { connected, robots, tasks, alarms } = useFleet()
  const navigate = useNavigate()

  const activeRobots = robots.filter(r => r.status !== 'idle' && r.status !== 'offline' && r.status !== 'charging').length
  const activeTasks  = tasks.filter(t => !['done','cancelled','failed'].includes(t.state)).length

  // ── Relocalization-assist CTA ───────────────────────────────────────────────
  // The backend latches one alarm per incident; we de-dupe by incident_id so an
  // SSE reconnect / re-render can't re-toast the same incident.
  const seenIncidents = useRef<Set<string>>(new Set())
  useEffect(() => {
    for (const a of alarms) {
      const p = a.payload
      if (!p || p.action !== 'RELOCALIZE_ASSIST_V1') continue
      if (seenIncidents.current.has(p.incident_id)) continue
      seenIncidents.current.add(p.incident_id)
      toast.error(`Robô ${p.robot_id} precisa de relocalização`, {
        description: a.message || `Motivo: ${p.reason}`,
        duration: 12000,
        action: {
          label: 'Abrir Assistente',
          onClick: () => navigate(`/calibration/${p.robot_id}`),
        },
      })
    }
  }, [alarms, navigate])

  // ── Software STOP-ALL halt state ────────────────────────────────────────────
  const [halted, setHalted] = useState(false)
  const [busy, setBusy] = useState(false)

  // Poll /stats/summary so the halted flag stays in sync even if another operator
  // toggles it. Silent on failure (backend down) — never crashes the shell.
  useEffect(() => {
    let alive = true
    const poll = () => {
      fleetApi.getStatsSummary()
        .then(s => { if (alive) setHalted(s.halted) })
        .catch(() => { /* backend offline — keep last known state */ })
    }
    poll()
    const id = setInterval(poll, 6000)
    return () => { alive = false; clearInterval(id) }
  }, [])

  const onStopAll = useCallback(async () => {
    setBusy(true)
    try {
      const res = await fleetApi.stopAll()
      setHalted(res.halted)
      toast.warning('PARADA GERAL acionada', {
        description: `${res.cancelled.length} tarefa(s) cancelada(s) · apenas parada por software`,
      })
    } catch {
      toast.error('Falha na PARADA GERAL', { description: 'Backend inacessível' })
    } finally {
      setBusy(false)
    }
  }, [])

  const onResume = useCallback(async () => {
    setBusy(true)
    try {
      const res = await fleetApi.resume()
      setHalted(res.halted)
      toast.success('Frota retomada — despacho automático reativado')
    } catch {
      toast.error('Falha ao retomar', { description: 'Backend inacessível' })
    } finally {
      setBusy(false)
    }
  }, [])

  return (
    <div className="flex h-screen w-full bg-[#0d1117] text-[#c9d1d9] font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#30363d] bg-[#0d1117] flex flex-col shrink-0">
        {/* Traffic light spacer */}
        <div className="h-8 shrink-0" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties} />
        <div className="h-14 border-b border-[#30363d] flex items-center px-4">
          <div className="w-6 h-6 bg-[#58a6ff] rounded-sm mr-3 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold font-mono">CAT</span>
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

        {/* Always-visible software STOP-ALL / RESUME */}
        <div className="px-3 pb-3">
          {halted ? (
            <button
              onClick={onResume}
              disabled={busy}
              title="Limpa a parada por software e reativa o despacho automático"
              className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-md text-sm font-bold
                bg-[#238636] hover:bg-[#2ea043] text-white transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4" /> RETOMAR FROTA
            </button>
          ) : (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <button
                  disabled={busy}
                  title="Parada por software — não é uma parada de emergência física"
                  className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-md text-sm font-bold
                    bg-[#da3633] hover:bg-[#f85149] text-white transition-colors disabled:opacity-50 animate-none"
                >
                  <OctagonX className="w-4 h-4" /> PARAR TUDO
                </button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-[#161b22] border-[#30363d] text-[#c9d1d9]">
                <AlertDialogHeader>
                  <AlertDialogTitle className="flex items-center gap-2 text-[#f85149]">
                    <ShieldAlert className="w-5 h-5" /> Parar toda a frota?
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-[#8b949e]">
                    Isto interrompe todos os robôs, cancela todas as tarefas ativas e pausa o
                    despacho automático até você pressionar Retomar.
                    <span className="block mt-2 text-[#d29922] font-medium">
                      Esta é uma Parada por Software — NÃO é uma parada de emergência física. Use a
                      parada de emergência física para emergências reais.
                    </span>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-transparent border-[#30363d] text-[#c9d1d9] hover:bg-[#21262d]">
                    Cancelar
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={onStopAll}
                    className="bg-[#da3633] hover:bg-[#f85149] text-white border-0"
                  >
                    Parar Tudo
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
          <p className="text-[10px] text-[#6e7681] text-center mt-1.5 leading-tight">
            Parada por Software — não é uma parada de emergência física
          </p>
        </div>

        {/* Footer — facility + connection status */}
        <div className="p-4 border-t border-[#30363d] text-xs text-[#8b949e] font-mono space-y-1.5">
          <div className="text-[#c9d1d9] font-medium text-sm">🏭 Piracicaba</div>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full shrink-0 ${connected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`} />
            <span className={connected ? 'text-green-400' : 'text-red-400'}>
              {connected ? 'Backend ativo' : 'Conectando…'}
            </span>
          </div>
          <div className="flex gap-3">
            <span>{robots.length} robôs</span>
            {activeRobots > 0 && <span className="text-[#58a6ff]">{activeRobots} ativos</span>}
          </div>
          <div className="text-[#6e7681]">v0.1.0 alpha</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {halted && (
          <div className="flex items-center justify-center gap-2 bg-[#da3633] text-white text-xs font-bold
            uppercase tracking-wide py-1.5 px-4 shrink-0">
            <ShieldAlert className="w-4 h-4" />
            Frota interrompida — parada por software acionada · despacho automático pausado
          </div>
        )}
        <Outlet />
      </main>
    </div>
  )
}
