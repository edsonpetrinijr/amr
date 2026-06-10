import React, { useCallback, useEffect, useRef, useState } from 'react'
import { PackageCheck, CheckCircle2, RotateCcw, AlertTriangle, Loader2, Truck } from 'lucide-react'
import { toast } from 'sonner'
import { fleetApi, onFleetMsg, FleetApiError } from '../api/fleet'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { PageHeader } from '@/app/components/PageHeader'
import { cn } from '@/app/utils'
import type { ErpOrder, ErpOrderStatus, ErpOrdersResponse } from '../api/types'

// Backend status strings (server/app/erp/service.py) → pt-BR badge metadata.
// Lifecycle: seen → blocked_unmapped | ready_for_confirmation
//                 → confirmed/dispatched → em_entrega → delivered (or cancelled)
type StatusMeta = {
  label: string
  variant: 'default' | 'success' | 'destructive' | 'secondary' | 'outline'
  className?: string
}

const STATUS_META: Record<ErpOrderStatus, StatusMeta> = {
  seen:                   { label: 'Detectado',               variant: 'secondary' },
  blocked_unmapped:       { label: 'Bloqueado — sem mapa',    variant: 'destructive' },
  ready_for_confirmation: { label: 'Aguardando confirmação',  variant: 'outline',
                            className: 'bg-[#d29922]/10 text-[#d29922] border-[#d29922]/40' },
  confirmed:              { label: 'Em entrega',              variant: 'default' },
  dispatched:             { label: 'Em entrega',              variant: 'default' },
  em_entrega:             { label: 'Em entrega',              variant: 'default' },
  delivered:              { label: 'Entregue',                variant: 'success' },
  cancelled:              { label: 'Cancelado',               variant: 'secondary' },
}

function StatusBadge({ status }: { status: ErpOrderStatus }) {
  const meta = STATUS_META[status] ?? { label: status, variant: 'outline' as const }
  return <Badge variant={meta.variant} className={meta.className}>{meta.label}</Badge>
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] uppercase tracking-wide text-[#6e7681]">{label}</span>
      <span className="text-sm text-[#c9d1d9] font-mono">{value || '—'}</span>
    </div>
  )
}

function OrderCard({ order }: { order: ErpOrder }) {
  return (
    <div className="border border-[#30363d] rounded-lg bg-[#161b22] p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <Field label="Célula" value={order.cell} />
        <StatusBadge status={order.status} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Ponto de uso (POU)" value={order.pou} />
        <Field label="Part number" value={order.part_number} />
        <Field label="Quantidade" value={order.quantity} />
        <Field label="AMR atribuído" value={order.task_id ? order.task_id.slice(-8) : 'Não atribuído'} />
      </div>
      {order.note && (
        <div className="text-xs text-[#8b949e] border-t border-[#21262d] pt-2">{order.note}</div>
      )}
    </div>
  )
}

function EmptyReturnRow({ order }: { order: ErpOrder }) {
  return (
    <div className="flex items-center justify-between gap-3 border border-[#30363d] rounded-md bg-[#161b22] px-4 py-2.5">
      <div className="flex items-center gap-3">
        <RotateCcw className="w-4 h-4 text-[#58a6ff] shrink-0" />
        <div className="flex flex-col">
          <span className="text-sm text-[#c9d1d9]">
            {order.pickup_station ?? '—'} → {order.dropoff_station ?? 'RECEBIMENTO'}
          </span>
          <span className="text-[11px] text-[#8b949e] font-mono">
            {order.task_id ? `AMR ${order.task_id.slice(-8)}` : 'Sem AMR'}
          </span>
        </div>
      </div>
      <StatusBadge status={order.status} />
    </div>
  )
}

type DispatchMode = 'dual' | 'single' | 'unavailable' | null

function DispatchModeBadge({ mode }: { mode: DispatchMode }) {
  if (!mode) return null
  if (mode === 'dual')
    return (
      <Badge variant="success" className="gap-1 font-semibold">
        <Truck className="w-3 h-3" /><Truck className="w-3 h-3 -ml-1.5" />
        2 AMRs prontos
      </Badge>
    )
  if (mode === 'single')
    return (
      <Badge variant="outline" className="bg-[#d29922]/10 text-[#d29922] border-[#d29922]/40 gap-1">
        <Truck className="w-3 h-3" />
        1 AMR — retorno manual
      </Badge>
    )
  // unavailable
  return <Badge variant="secondary">Sem AMR disponível</Badge>
}

export function Reposicao() {
  const [orders, setOrders] = useState<ErpOrder[]>([])
  const [amrReady, setAmrReady] = useState(false)
  const [dispatchMode, setDispatchMode] = useState<DispatchMode>(null)
  const [envioStation, setEnvioStation] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [requesting, setRequesting] = useState(false)
  const aliveRef = useRef(true)
  const _refetchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const refetch = useCallback(async () => {
    try {
      const res: ErpOrdersResponse = await fleetApi.getErpOrders()
      if (!aliveRef.current) return
      setOrders(res.orders ?? [])
      setAmrReady(!!res.amr_ready)
      setDispatchMode(res.dispatch_mode ?? null)
      setEnvioStation(res.envio_station ?? '')
      setError(null)
    } catch {
      if (!aliveRef.current) return
      setError('Não foi possível carregar os pedidos. Backend inacessível.')
    } finally {
      if (aliveRef.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    aliveRef.current = true
    refetch()

    // Prefer SSE-triggered refresh: the ERP service broadcasts `erp_order` on every
    // create / status change. We use it as a signal to re-pull the authoritative
    // board (amr_ready isn't carried in the per-order message).
    // Debounced so a burst of 5 erp_order events (one per new order) collapses into
    // one HTTP call instead of 5 rapid re-renders of the order grid.
    const unsub = onFleetMsg((msg) => {
      if (msg.type === 'erp_order') {
        if (_refetchTimerRef.current) clearTimeout(_refetchTimerRef.current)
        _refetchTimerRef.current = setTimeout(refetch, 300)
      }
    })

    // Polling fallback keeps amr_ready fresh even with no order churn.
    const id = setInterval(refetch, 5000)

    return () => {
      aliveRef.current = false
      if (_refetchTimerRef.current) clearTimeout(_refetchTimerRef.current)
      unsub()
      clearInterval(id)
    }
  }, [refetch])

  const mainOrders   = orders.filter(o => o.record_type_class !== 'empty_return')
  const emptyReturns = orders.filter(o => o.record_type_class === 'empty_return')
  const hasReady     = mainOrders.some(o => o.status === 'ready_for_confirmation')

  const handleConfirm = useCallback(async () => {
    setConfirming(true)
    try {
      const res = await fleetApi.confirmDelivery()
      if (res.ok) {
        const msg = res.dispatch_mode === 'dual'
          ? 'Entrega + retorno despachados — 2 AMRs'
          : 'Entrega confirmada — AMR despachado'
        toast.success(msg)
      } else {
        toast.error('Nada para confirmar na fila')
      }
      await refetch()
    } catch (e) {
      const msg = e instanceof FleetApiError ? e.message : 'Backend inacessível'
      toast.error('Falha ao confirmar entrega', { description: msg })
    } finally {
      setConfirming(false)
    }
  }, [refetch])

  const handleRequestEmpty = useCallback(async () => {
    setRequesting(true)
    try {
      const res = await fleetApi.requestEmpty()
      if (res.ok) toast.success('Retorno forçado — AMR a caminho')
      else toast.error('Não foi possível solicitar retorno')
      await refetch()
    } catch (e) {
      const msg = e instanceof FleetApiError ? e.message : 'Backend inacessível'
      toast.error('Falha ao forçar retorno', { description: msg })
    } finally {
      setRequesting(false)
    }
  }, [refetch])

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] overflow-hidden">
      <PageHeader
        icon={<PackageCheck className="w-4 h-4 text-[#58a6ff]" />}
        title="Reposição"
        status={
          <span className="ml-1 flex items-center gap-2 text-xs text-[#8b949e]">
            <span className={cn('w-2 h-2 rounded-full', amrReady ? 'bg-green-400' : 'bg-[#6e7681]')} />
            <span className={amrReady ? 'text-green-400' : 'text-[#8b949e]'}>
              {amrReady ? 'AMR pronto no ENVIO' : 'AMR ocupado'}
            </span>
            {envioStation && <span className="text-[#6e7681] font-mono">· {envioStation}</span>}
            <DispatchModeBadge mode={dispatchMode} />
          </span>
        }
        actions={
          <>
            <Button variant="primary" size="sm" disabled={!hasReady || confirming} onClick={handleConfirm}>
              {confirming
                ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                : <CheckCircle2 className="w-3.5 h-3.5 mr-1" />}
              Confirmar entrega
            </Button>
            <span
              title="Despacha um AMR para buscar rack vazio manualmente"
              className="inline-flex"
            >
              <Button
                variant="outline"
                size="sm"
                disabled={requesting || dispatchMode === 'dual'}
                onClick={handleRequestEmpty}
              >
                {requesting
                  ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                  : <RotateCcw className="w-3.5 h-3.5 mr-1" />}
                Forçar retorno
              </Button>
            </span>
          </>
        }
      />

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {loading ? (
          <div className="h-full flex items-center justify-center text-[#8b949e] text-sm gap-2">
            <Loader2 className="w-4 h-4 animate-spin" /> Carregando pedidos…
          </div>
        ) : error ? (
          <div className="h-full flex flex-col items-center justify-center text-[#8b949e] text-sm gap-2">
            <AlertTriangle className="w-5 h-5 text-[#f85149]" />
            {error}
          </div>
        ) : (
          <>
            {/* Main FIFO order queue */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[#8b949e]">
                <Truck className="w-3.5 h-3.5" />
                Fila de pedidos AMR
                <span className="text-[#6e7681]">({mainOrders.length})</span>
              </div>
              {mainOrders.length === 0 ? (
                <div className="border border-dashed border-[#30363d] rounded-lg py-10 text-center text-sm text-[#8b949e]">
                  Nenhum pedido na fila
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-3">
                  {mainOrders.map(o => <OrderCard key={o.order_key} order={o} />)}
                </div>
              )}
            </section>

            {/* Empties / return lane */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[#8b949e]">
                <RotateCcw className="w-3.5 h-3.5" />
                Retorno de vazios
                <span className="text-[#6e7681]">({emptyReturns.length})</span>
              </div>
              {emptyReturns.length === 0 ? (
                <div className="border border-dashed border-[#30363d] rounded-lg py-6 text-center text-sm text-[#8b949e]">
                  Nenhum retorno de vazio
                </div>
              ) : (
                <div className="space-y-2">
                  {emptyReturns.map(o => <EmptyReturnRow key={o.order_key} order={o} />)}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  )
}
