import React, { useState, useEffect, useRef } from 'react'
import { Bell, Loader2, X } from 'lucide-react'
import { toast } from 'sonner'
import { useFleet } from '../state/store'
import { fleetApi, FleetApiError } from '../api/fleet'
import type { Station, OpcuaTestResult, CallbuttonPressResult } from '../api/types'
import { PageHeader } from '@/app/components/PageHeader'

// ── Local extended type — backend sends these extra fields beyond the base type ──
interface PressResult extends CallbuttonPressResult {
  pending_origin?: string | null
  task?: unknown
}

// ── Constants — PoC Conversor de Torque station IDs ──────────────────────────
const ENVIO_IDS   = ['BTLOG1']
const POU_PREFIX  = 'FLBT10TC'

function stationGroup(id: string): 'envio' | 'pou' | 'other' {
  if (ENVIO_IDS.includes(id))       return 'envio'
  if (id.startsWith(POU_PREFIX))    return 'pou'
  return 'other'
}

// ── cb_state badge ────────────────────────────────────────────────────────────
const STATE_BADGE: Record<string, { label: string; cls: string }> = {
  idle:   { label: 'idle',     cls: 'bg-[#21262d] text-[#8b949e]' },
  ready:  { label: 'pronto',   cls: 'bg-[#d29922]/20 text-[#d29922]' },
  called: { label: 'chamado',  cls: 'bg-[#58a6ff]/20 text-[#58a6ff]' },
  served: { label: 'atendido', cls: 'bg-[#3fb950]/20 text-[#3fb950]' },
}

function CbStateBadge({ state }: { state: string }) {
  const b = STATE_BADGE[state] ?? { label: state, cls: 'bg-[#21262d] text-[#8b949e]' }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium ${b.cls}`}>
      {b.label}
    </span>
  )
}

// ── Per-press inline banner inside a card ─────────────────────────────────────
type PressState = 'waiting_destination' | 'dispatched' | 'idle' | string

function InlinePressResult({ state, message }: { state: PressState; message?: string }) {
  if (state === 'waiting_destination') {
    return (
      <div className="mt-3 px-3 py-2 rounded-lg bg-[#d29922]/10 border border-[#d29922]/30 text-[#d29922] text-xs">
        ⏳ Aguardando destino… {message && <span className="text-[#8b949e]">{message}</span>}
      </div>
    )
  }
  if (state === 'dispatched') {
    return (
      <div className="mt-3 px-3 py-2 rounded-lg bg-[#3fb950]/10 border border-[#3fb950]/30 text-[#3fb950] text-xs">
        🚀 Despachado! AMR a caminho {message && <span className="text-[#8b949e]">— {message}</span>}
      </div>
    )
  }
  return null
}

// ── Station card (prominent, for envio + pou groups) ─────────────────────────
function StationCard({
  station,
  pressing,
  lastResult,
  onPress,
}: {
  station: Station
  pressing: string | null
  lastResult: PressResult | null
  onPress: (id: string) => void
}) {
  const isPressed = pressing === station.id

  return (
    <div className="rounded-xl border border-[#30363d] bg-[#161b22] p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1 min-w-0">
          <span className="text-sm font-medium text-[#e6edf3] truncate">{station.label}</span>
          <span className="text-[11px] font-mono text-[#484f58]">{station.id}</span>
        </div>
        <CbStateBadge state={station.cb_state ?? 'idle'} />
      </div>

      <button
        disabled={isPressed || pressing !== null}
        onClick={() => onPress(station.id)}
        className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg border
          border-[#30363d] text-xs font-medium transition-all active:scale-95
          text-[#e6edf3] hover:border-[#58a6ff]/60 hover:bg-[#58a6ff]/5 hover:text-[#58a6ff]
          disabled:opacity-40 disabled:cursor-not-allowed">
        {isPressed
          ? <><Loader2 className="w-3.5 h-3.5 animate-spin" />Pressionando…</>
          : '⚡ Simular pressão'}
      </button>

      {lastResult && lastResult.state && (
        <InlinePressResult state={lastResult.state} message={lastResult.message} />
      )}
    </div>
  )
}

// ── Compact row (for "other" stations) ────────────────────────────────────────
function StationRow({
  station,
  pressing,
  onPress,
}: {
  station: Station
  pressing: string | null
  onPress: (id: string) => void
}) {
  const isPressed = pressing === station.id
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3
      rounded-lg border border-[#30363d] bg-[#161b22]">
      <div className="flex items-center gap-3 min-w-0">
        <CbStateBadge state={station.cb_state ?? 'idle'} />
        <span className="text-xs text-[#e6edf3] truncate">{station.label}</span>
        <span className="text-[10px] font-mono text-[#484f58] shrink-0">{station.id}</span>
      </div>
      <button
        disabled={isPressed || pressing !== null}
        onClick={() => onPress(station.id)}
        className="flex items-center gap-1.5 shrink-0 text-xs px-3 py-1.5 rounded-lg border
          border-[#30363d] text-[#8b949e] hover:border-[#58a6ff]/50 hover:text-[#58a6ff]
          disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
        {isPressed ? <Loader2 className="w-3 h-3 animate-spin" /> : '⚡'}
        Simular
      </button>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export function Callbuttons() {
  const { stations, connected } = useFleet()
  const [pressing, setPressing]           = useState<string | null>(null)
  const [lastResults, setLastResults]     = useState<Record<string, PressResult>>({})
  const [pendingOrigin, setPendingOrigin] = useState<string | null>(null)
  const bannerTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Auto-dismiss pending-origin banner after 30 s
  useEffect(() => {
    if (!pendingOrigin) return
    if (bannerTimerRef.current) clearTimeout(bannerTimerRef.current)
    bannerTimerRef.current = setTimeout(() => setPendingOrigin(null), 30_000)
    return () => { if (bannerTimerRef.current) clearTimeout(bannerTimerRef.current) }
  }, [pendingOrigin])

  const cbStations = stations.filter(s => s.type === 'callbutton')
  const envioStations = cbStations.filter(s => stationGroup(s.id) === 'envio')
  const pouStations   = cbStations.filter(s => stationGroup(s.id) === 'pou')
  const otherStations = cbStations.filter(s => stationGroup(s.id) === 'other')

  const [showOthers, setShowOthers] = useState(false)

  async function handlePress(id: string) {
    setPressing(id)
    try {
      const res = await fleetApi.pressCallbutton(id) as PressResult
      // Update per-station last result
      setLastResults(prev => ({ ...prev, [id]: res }))
      // Track pending origin
      if (res.pending_origin != null) {
        setPendingOrigin(res.pending_origin)
      } else if (res.state === 'dispatched' || res.state === 'idle') {
        setPendingOrigin(null)
      }
      // Toast feedback
      if (res.state === 'dispatched') {
        toast.success('Tarefa despachada!', { description: res.message ?? `AMR enviado para ${id}` })
      } else if (res.state === 'waiting_destination') {
        toast.info('Origem registrada', { description: res.message ?? `Pressione agora a estação de destino` })
      } else {
        toast.success('Pressão simulada', { description: res.message ?? `Estação ${id} pressionada` })
      }
    } catch (e) {
      const detail = e instanceof FleetApiError ? e.message : 'Backend inacessível'
      toast.error('Falha ao simular pressão', { description: detail })
    } finally {
      setPressing(null)
    }
  }

  function handleClearPending() {
    if (bannerTimerRef.current) clearTimeout(bannerTimerRef.current)
    setPendingOrigin(null)
  }

  // Stations with OPC UA nodes (for hardware diagnostics)
  const opcuaStations = cbStations.filter(s => s.opcua_node)

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <PageHeader
        icon={<Bell className="w-4 h-4 text-[#58a6ff]" />}
        title="Botões de Chamada"
        status={
          <span className="ml-1 flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`} />
            <span className="text-xs text-[#484f58]">— PoC Conversor de Torque</span>
          </span>
        }
      />

      {/* Pending-origin banner */}
      {pendingOrigin && (
        <div className="mx-6 mt-4 flex items-center justify-between gap-4
          px-4 py-3 rounded-xl border border-[#d29922]/40 bg-[#d29922]/8">
          <span className="text-sm text-[#d29922]">
            ⏳ Origem registrada:{' '}
            <code className="font-mono text-[#e6edf3] bg-[#0d1117] px-1.5 py-0.5 rounded">
              {pendingOrigin}
            </code>
            {' '}— pressione agora a estação de destino
          </span>
          <button
            onClick={handleClearPending}
            title="Limpar seleção"
            className="shrink-0 p-1 rounded hover:bg-[#d29922]/20 text-[#d29922] transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Disconnected fallback */}
      {cbStations.length === 0 && (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center space-y-2">
            <p className="text-sm text-[#8b949e]">Nenhuma estação de tipo <code className="font-mono">callbutton</code> encontrada.</p>
            <p className="text-xs text-[#484f58]">
              {connected ? 'Mapa carregado sem estações callbutton.' : 'Backend desconectado — aguardando SSE…'}
            </p>
          </div>
        </div>
      )}

      {cbStations.length > 0 && (
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Envio / Estoque */}
          {envioStations.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
                📦 Envio / Estoque
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {envioStations.map(s => (
                  <StationCard
                    key={s.id}
                    station={s}
                    pressing={pressing}
                    lastResult={lastResults[s.id] ?? null}
                    onPress={handlePress}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Pontos de Uso (Linha) */}
          {pouStations.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
                🏭 Pontos de Uso (Linha)
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {pouStations.map(s => (
                  <StationCard
                    key={s.id}
                    station={s}
                    pressing={pressing}
                    lastResult={lastResults[s.id] ?? null}
                    onPress={handlePress}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Outras estações (collapsed by default) */}
          {otherStations.length > 0 && (
            <section className="space-y-2">
              <button
                onClick={() => setShowOthers(v => !v)}
                className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                  text-[#484f58] hover:text-[#8b949e] transition-colors">
                <span>{showOthers ? '▾' : '▸'}</span>
                Outras estações ({otherStations.length})
              </button>
              {showOthers && (
                <div className="space-y-2">
                  {otherStations.map(s => (
                    <StationRow
                      key={s.id}
                      station={s}
                      pressing={pressing}
                      onPress={handlePress}
                    />
                  ))}
                </div>
              )}
            </section>
          )}

          {/* Limpar seleção */}
          {pendingOrigin && (
            <div className="flex justify-center pt-2">
              <button
                onClick={handleClearPending}
                className="text-xs px-4 py-2 rounded-lg border border-[#30363d]
                  text-[#8b949e] hover:border-[#484f58] hover:text-[#e6edf3] transition-colors">
                Limpar seleção
              </button>
            </div>
          )}

          {/* OPC UA diagnostics — only for stations with a configured node */}
          {opcuaStations.length > 0 && (
            <section className="space-y-3 pt-2 border-t border-[#30363d]">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-[#484f58]">
                🔌 Diagnóstico OPC UA
              </h2>
              <div className="flex flex-wrap gap-3">
                {opcuaStations.map(s => (
                  <OpcuaTestButton key={s.id} station={s} />
                ))}
              </div>
            </section>
          )}

        </div>
      )}
    </div>
  )
}

// ── OPC UA test button (kept from original) ───────────────────────────────────
function OpcuaTestButton({ station }: { station: Station }) {
  const [testing, setTesting] = useState(false)
  const [result, setResult]   = useState<OpcuaTestResult | null>(null)
  const [error, setError]     = useState<string | null>(null)

  async function handleTest() {
    setTesting(true)
    setError(null)
    setResult(null)
    try {
      const res = await fleetApi.testOpcua({ station_id: station.id })
      console.debug('opcua test', station.id, res.node, res.value)
      setResult(res)
    } catch (e) {
      setError(e instanceof FleetApiError ? e.message : 'Falha no teste')
    } finally {
      setTesting(false)
    }
  }

  const msg = error
    ? <span className="text-[#ff7b72]">{error}</span>
    : !result ? null
    : !result.configured ? <span className="text-[#8b949e]">sem OPC UA</span>
    : result.ok ? <span className="text-[#3fb950]">✅ Leitura OK</span>
    : <span className="text-[#ff7b72]">❌ {result.error ?? 'falhou'}</span>

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        disabled={testing}
        onClick={handleTest}
        className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-[#30363d]
          text-[#8b949e] hover:border-[#58a6ff]/50 hover:text-[#58a6ff] disabled:opacity-30 transition-colors">
        {testing && <Loader2 className="w-3 h-3 animate-spin" />}
        Testar {station.label}
      </button>
      {msg && <span className="text-[10px] font-mono">{msg}</span>}
    </div>
  )
}
