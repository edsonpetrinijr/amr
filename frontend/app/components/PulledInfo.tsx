import type { RobotPulled } from '../api/types'

/** Inline connection status + pulled identity panel, shared by the add/edit
 *  dialog and the per-row probe result. */
export function PulledInfo({ connected, pulled }: { connected: boolean; pulled: RobotPulled }) {
  return (
    <div className={`rounded-md border px-3 py-2 text-xs ${
      connected
        ? 'border-[#2ea043]/30 bg-[#238636]/10'
        : 'border-[#f85149]/30 bg-[#da3633]/10'}`}>
      <div className={`font-semibold mb-1 ${connected ? 'text-[#3fb950]' : 'text-[#ff7b72]'}`}>
        {connected ? '✅ Connected' : '❌ Unreachable'}
      </div>
      {connected && (
        <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 font-mono text-[#c9d1d9]">
          <span className="text-[#8b949e]">name</span><span>{pulled.name || '—'}</span>
          <span className="text-[#8b949e]">model</span><span>{pulled.model || '—'}</span>
          <span className="text-[#8b949e]">battery</span><span>{pulled.battery.toFixed(0)}%</span>
          <span className="text-[#8b949e]">pose</span>
          <span>({pulled.x.toFixed(2)}, {pulled.y.toFixed(2)}, {(pulled.theta * 180 / Math.PI).toFixed(0)}°)</span>
        </div>
      )}
    </div>
  )
}
