import React, { useState } from 'react'
import { Truck, RotateCcw } from 'lucide-react'
import { useFleet } from '../state/store'
import { fleetApi } from '../api/fleet'
import type { Station } from '../api/types'

const SUPPLIER = 'AP1'
const CONSUMER = 'CB1'
const FWD_LABEL = 'Almox → Linha'
const RET_LABEL = 'Linha → Almox'

function DirectionRow({ dir, label, supplier, consumer, task, onPress, pressing }: {
  dir: 'fwd' | 'ret'
  label: string
  supplier: Station | undefined
  consumer: Station | undefined
  task: any
  onPress: (id: string, d: 'fwd' | 'ret') => void
  pressing: string | null
}) {
  const sReady      = supplier?.cb_state === 'ready'   && supplier?.cb_dir === dir
  const cReady      = consumer?.cb_state === 'ready'   && consumer?.cb_dir === dir
  const dispatched  = supplier?.cb_state === 'called'  && supplier?.cb_dir === dir
  const active      = sReady || cReady || dispatched
  const canPressS   = !dispatched && !sReady
  const canPressC   = !dispatched && !cReady

  return (
    <div className={`flex items-center gap-6 px-6 py-5 rounded-xl border transition-all
      ${dispatched ? 'border-[#58a6ff]/50 bg-[#58a6ff]/5' :
        active      ? 'border-[#d29922]/40 bg-[#d29922]/5' :
                      'border-[#30363d] bg-[#161b22]'}`}>

      {/* Supplier button */}
      <div className="flex flex-col items-center gap-2">
        <button
          disabled={!canPressS || !!pressing}
          onClick={() => onPress(SUPPLIER, dir)}
          className={`w-20 h-20 rounded-full border-4 text-xs font-semibold transition-all active:scale-95
            ${sReady || dispatched
              ? 'border-[#3fb950] bg-[#3fb950]/10 text-[#3fb950] cursor-not-allowed'
              : 'border-[#30363d] bg-[#0d1117] text-[#8b949e] hover:border-[#58a6ff] hover:text-[#58a6ff]'}`}>
          {sReady || dispatched ? '✓' : 'Pronto'}
        </button>
        <span className="text-[10px] text-[#484f58]">{supplier?.label ?? SUPPLIER}</span>
      </div>

      {/* Arrow */}
      <div className="flex-1 flex flex-col items-center gap-1">
        <span className="text-xs font-medium text-[#8b949e]">{label}</span>
        <div className="flex items-center gap-2 w-full">
          <div className="flex-1 border-t border-dashed border-[#30363d]" />
          {dispatched
            ? <Truck className="w-5 h-5 text-[#58a6ff] animate-pulse shrink-0" />
            : <span className="text-[#484f58] shrink-0">→</span>}
          <div className="flex-1 border-t border-dashed border-[#30363d]" />
        </div>
        {dispatched && task?.robot && (
          <span className="text-[10px] text-[#58a6ff]">{task.robot}</span>
        )}
      </div>

      {/* Consumer button */}
      <div className="flex flex-col items-center gap-2">
        <button
          disabled={!canPressC || !!pressing}
          onClick={() => onPress(CONSUMER, dir)}
          className={`w-20 h-20 rounded-full border-4 text-xs font-semibold transition-all active:scale-95
            ${cReady || dispatched
              ? 'border-[#3fb950] bg-[#3fb950]/10 text-[#3fb950] cursor-not-allowed'
              : 'border-[#30363d] bg-[#0d1117] text-[#8b949e] hover:border-[#58a6ff] hover:text-[#58a6ff]'}`}>
          {cReady || dispatched ? '✓' : 'Preciso'}
        </button>
        <span className="text-[10px] text-[#484f58]">{consumer?.label ?? CONSUMER}</span>
      </div>
    </div>
  )
}

export function Callbuttons() {
  const { stations, tasks, connected } = useFleet()
  const [pressing, setPressing] = useState<string | null>(null)
  const [resetting, setResetting] = useState(false)

  const supplier = stations.find(s => s.id === SUPPLIER)
  const consumer = stations.find(s => s.id === CONSUMER)

  const fwdTask = tasks.find(t => t.pickup === SUPPLIER && t.dropoff === CONSUMER)
  const retTask = tasks.find(t => t.pickup === CONSUMER && t.dropoff === SUPPLIER)

  const anyActive = supplier?.cb_state !== 'idle' || consumer?.cb_state !== 'idle'

  async function handlePress(id: string, dir: 'fwd' | 'ret') {
    setPressing(id + dir)
    try { await fleetApi.buttonPress(id, dir) } catch {}
    finally { setPressing(null) }
  }

  async function handleReset() {
    setResetting(true)
    try { await fleetApi.resetPair(SUPPLIER) } catch {}
    finally { setResetting(false) }
  }

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`} />
        <span className="text-sm font-semibold text-[#e6edf3]">Call Buttons</span>
        <span className="text-xs text-[#484f58] ml-1">— via OPC UA quando SIM_MODE=false</span>
      </div>

      {/* Rows */}
      <div className="flex-1 flex flex-col justify-center gap-4 p-8">
        <DirectionRow dir="fwd" label={FWD_LABEL}
          supplier={supplier} consumer={consumer} task={fwdTask}
          onPress={handlePress} pressing={pressing} />

        <DirectionRow dir="ret" label={RET_LABEL}
          supplier={supplier} consumer={consumer} task={retTask}
          onPress={handlePress} pressing={pressing} />

        {/* Reset */}
        <div className="flex justify-center mt-2">
          <button
            disabled={!anyActive || resetting}
            onClick={handleReset}
            className="flex items-center gap-2 text-xs px-4 py-2 rounded-lg border border-[#30363d]
              text-[#8b949e] hover:border-red-500/50 hover:text-red-400 disabled:opacity-30 transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
            Cancelar / Resetar
          </button>
        </div>
      </div>
    </div>
  )
}
