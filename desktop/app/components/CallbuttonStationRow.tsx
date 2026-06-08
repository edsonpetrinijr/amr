import { useEffect, useState } from 'react'
import { Loader2, Save, Bell } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { fleetApi, FleetApiError } from '../api/fleet'
import type { Station, OpcuaTestResult } from '../api/types'

const CB_V: Record<string, 'default' | 'outline' | 'success' | 'destructive' | 'secondary'> = {
  idle: 'outline', called: 'default', acknowledged: 'secondary', served: 'success',
}

/** Operator-facing pt-BR labels for the callbutton state badge. */
const CB_LABEL: Record<string, string> = {
  idle: 'ocioso', ready: 'pronto', called: 'chamado', acknowledged: 'reconhecido', served: 'atendido',
}

/** Editable callbutton row: OPC UA node id + Save + Test diagnostics. */
export function CallbuttonStationRow({ station }: { station: Station }) {
  const [node, setNode] = useState(station.opcua_node ?? '')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<OpcuaTestResult | null>(null)
  const [testError, setTestError] = useState<string | null>(null)
  const [pressing, setPressing] = useState(false)

  // Keep input in sync if the SSE snapshot changes the configured node.
  useEffect(() => { setNode(station.opcua_node ?? '') }, [station.opcua_node])

  const dirty = node.trim() !== (station.opcua_node ?? '')

  async function handleSave() {
    setSaving(true)
    setSaveError(null)
    try {
      const body: { opcua_node: string | null; opcua_ret?: string | null } = {
        opcua_node: node.trim() || null,
      }
      if (station.opcua_ret != null) body.opcua_ret = station.opcua_ret
      await fleetApi.updateStation(station.id, body)
    } catch (e) {
      setSaveError(e instanceof FleetApiError ? e.message : 'Falha ao salvar')
    } finally {
      setSaving(false)
    }
  }

  async function handleTest() {
    setTesting(true)
    setTestError(null)
    setTestResult(null)
    try {
      const res = await fleetApi.testOpcua({ station_id: station.id })
      // Raw read value kept for debugging only — never shown to the operator.
      console.debug('opcua test', station.id, res.node, res.value)
      setTestResult(res)
    } catch (e) {
      setTestError(e instanceof FleetApiError ? e.message : 'Falha no teste')
    } finally {
      setTesting(false)
    }
  }

  async function handlePress() {
    setPressing(true)
    try {
      const res = await fleetApi.pressCallbutton(station.id)
      const detail = res.message
        ?? (res.state === 'waiting_destination' ? 'aguardando destino'
          : res.state === 'dispatched' ? 'transporte despachado'
          : res.state)
      toast.success(`${station.id} apertado`, detail ? { description: detail } : undefined)
    } catch (e) {
      toast.error('Falha ao apertar', {
        description: e instanceof FleetApiError ? e.message : 'Backend inacessível',
      })
    } finally {
      setPressing(false)
    }
  }

  return (
    <>
      <tr className="border-b border-[#21262d] hover:bg-[#161b22]">
        <td className="px-4 py-2 font-mono text-[#e6edf3]">{station.id}</td>
        <td className="px-4 py-2 text-[#c9d1d9]">{station.label}</td>
        <td className="px-4 py-2 font-mono text-[#58a6ff]">{station.seer_lm ?? '—'}</td>
        <td className="px-4 py-2 font-mono text-[#8b949e]">{station.ap_id ?? '—'}</td>
        <td className="px-4 py-2">
          <div className="flex items-center gap-1">
            <Input value={node} onChange={e => setNode(e.target.value)} placeholder="ns=2;s=…"
              className="h-7 bg-[#0d1117] border-[#30363d] text-[#c9d1d9] font-mono text-[10px] w-56"
              disabled={saving} />
            <Button variant="outline" size="sm" onClick={handleSave} disabled={saving || !dirty} title="Salvar nó">
              {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
            </Button>
          </div>
        </td>
        <td className="px-4 py-2 font-mono text-[#8b949e]">
          ({station.x.toFixed(1)}, {station.y.toFixed(1)})
        </td>
        <td className="px-4 py-2">
          <Badge variant={CB_V[station.cb_state] ?? 'outline'}>{CB_LABEL[station.cb_state] ?? station.cb_state}</Badge>
        </td>
        <td className="px-4 py-2">
          <div className="flex items-center gap-1">
            <Button variant="outline" size="sm" onClick={handleTest} disabled={testing}>
              {testing && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
              Testar
            </Button>
            <Button variant="outline" size="sm" onClick={handlePress} disabled={pressing}
              title="Simular pressão física do botão de chamada">
              {pressing ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Bell className="w-3.5 h-3.5 mr-1" />}
              Apertar
            </Button>
          </div>
        </td>
      </tr>
      {(saveError || testError || testResult) && (
        <tr className="border-b border-[#21262d] bg-[#0d1117]">
          <td colSpan={8} className="px-4 py-2 text-xs">
            {saveError && <div className="text-[#ff7b72] mb-1">{saveError}</div>}
            {testError && <div className="text-[#ff7b72]">{testError}</div>}
            {testResult && <TestResultLine res={testResult} />}
          </td>
        </tr>
      )}
    </>
  )
}

function TestResultLine({ res }: { res: OpcuaTestResult }) {
  if (!res.configured) {
    return <div className="text-[#8b949e]">Nenhum endpoint OPC UA configurado.</div>
  }
  if (res.ok) {
    return (
      <div className="text-[#3fb950]">
        ✅ Leitura OK <span className="font-mono text-[#c9d1d9]">{res.node}</span>
        {res.endpoint && <span className="text-[#484f58] ml-2">@ {res.endpoint}</span>}
      </div>
    )
  }
  return (
    <div className="text-[#ff7b72]">
      ❌ {res.error ?? 'Falha na leitura'}
      {res.node && <span className="font-mono text-[#8b949e] ml-2">({res.node})</span>}
    </div>
  )
}
