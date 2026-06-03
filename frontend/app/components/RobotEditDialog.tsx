import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from './ui/dialog'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { fleetApi, FleetApiError } from '../api/fleet'
import type { Robot, RobotMutationResult } from '../api/types'
import { PulledInfo } from './PulledInfo'

interface Props {
  mode: 'add' | 'edit'
  robot?: Robot
  open: boolean
  onOpenChange: (open: boolean) => void
  /** Called after a successful mutation so the parent can re-fetch the list. */
  onSaved: () => void
}

const labelCls = 'text-[11px] uppercase tracking-wide text-[#8b949e]'
const fieldCls = 'bg-[#0d1117] border-[#30363d] text-[#e6edf3] font-mono text-xs'

export function RobotEditDialog({ mode, robot, open, onOpenChange, onSaved }: Props) {
  const [ip, setIp] = useState('')
  const [id, setId] = useState('')
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<RobotMutationResult | null>(null)

  // Reset form whenever the dialog (re)opens.
  useEffect(() => {
    if (open) {
      setIp(robot?.ip ?? '')
      setId(robot?.id ?? '')
      setName(robot?.name ?? '')
      setError(null)
      setResult(null)
      setBusy(false)
    }
  }, [open, robot])

  async function handleSubmit() {
    if (!ip.trim()) { setError('IP is required'); return }
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const res = mode === 'add'
        ? await fleetApi.addRobot({
            ip: ip.trim(),
            ...(id.trim() ? { id: id.trim() } : {}),
            ...(name.trim() ? { name: name.trim() } : {}),
          })
        : await fleetApi.updateRobot(robot!.id, {
            ip: ip.trim(),
            ...(name.trim() ? { name: name.trim() } : {}),
          })
      setResult(res)
      onSaved()
    } catch (e) {
      setError(e instanceof FleetApiError ? e.message : 'Request failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#161b22] border-[#30363d] text-[#e6edf3]">
        <DialogHeader>
          <DialogTitle>{mode === 'add' ? 'Add robot' : `Edit ${robot?.id}`}</DialogTitle>
          <DialogDescription className="text-[#8b949e]">
            {mode === 'add'
              ? 'Register a unit by IP. We probe it and pull its identity.'
              : 'Change the IP or name. We re-probe on save.'}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <span className={labelCls}>IP address *</span>
            <Input value={ip} onChange={e => setIp(e.target.value)} placeholder="192.168.1.50"
              className={fieldCls} disabled={busy} autoFocus />
          </div>
          {mode === 'add' && (
            <div className="flex flex-col gap-1">
              <span className={labelCls}>ID (optional)</span>
              <Input value={id} onChange={e => setId(e.target.value)} placeholder="auto"
                className={fieldCls} disabled={busy} />
            </div>
          )}
          <div className="flex flex-col gap-1">
            <span className={labelCls}>Name (optional)</span>
            <Input value={name} onChange={e => setName(e.target.value)} placeholder="from unit"
              className={fieldCls} disabled={busy} />
          </div>

          {error && (
            <div className="text-xs text-[#ff7b72] bg-[#da3633]/10 border border-[#f85149]/30 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          {result && (
            <PulledInfo connected={result.connected} pulled={result.pulled} />
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} disabled={busy}>
            {result ? 'Close' : 'Cancel'}
          </Button>
          <Button variant="primary" size="sm" onClick={handleSubmit} disabled={busy}>
            {busy && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
            {mode === 'add' ? 'Add & probe' : 'Save & probe'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
