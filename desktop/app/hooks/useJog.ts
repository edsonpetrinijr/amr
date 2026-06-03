// ─────────────────────────────────────────────────────────────────────────────
// useJog — encapsulates manual-jog control (WASD + Q/E + arrows + on-screen pad).
//
// Installs global keydown/keyup/blur listeners while mounted, composes a velocity
// vector from the held directions, POSTs /jog on a 150 ms cadence (immediate post
// then interval), and sends /jog/stop on release / blur / unmount / robot change.
//
// Shared by Calibration's JogPanel and Field's RobotPanel D-pad. Pass a null
// robotId to keep the hook inert (no posts, no listeners doing anything).
// ─────────────────────────────────────────────────────────────────────────────
import { useState, useEffect, useRef, useCallback } from 'react'
import { toast } from 'sonner'
import { fleetApi, FleetApiError } from '../api/fleet'

// Sane operator velocities; the backend clamps to the JOG_MAX_* envelope and runs
// an idle watchdog (~0.4s) that auto-stops if it stops receiving /jog commands.
export const JOG_V = 0.2          // m/s for translate/strafe
export const JOG_W = 0.3          // rad/s for rotate
export const JOG_INTERVAL_MS = 150 // re-post cadence while a key/button is held

export type JogDir = 'forward' | 'back' | 'left' | 'right' | 'ccw' | 'cw'

// Per-direction contribution to the composed velocity vector.
export const JOG_DIR_VECTORS: Record<JogDir, { vx: number; vy: number; w: number }> = {
  forward: { vx:  JOG_V, vy: 0,      w: 0 },
  back:    { vx: -JOG_V, vy: 0,      w: 0 },
  left:    { vx: 0,      vy:  JOG_V, w: 0 },
  right:   { vx: 0,      vy: -JOG_V, w: 0 },
  ccw:     { vx: 0,      vy: 0,      w:  JOG_W },
  cw:      { vx: 0,      vy: 0,      w: -JOG_W },
}

// Keyboard mapping: WASD + Q/E plus arrow keys. Keys are normalised to lowercase.
export const KEY_TO_DIR: Record<string, JogDir> = {
  w: 'forward', s: 'back', a: 'left', d: 'right', q: 'ccw', e: 'cw',
  arrowup: 'forward', arrowdown: 'back', arrowleft: 'left', arrowright: 'right',
}

export interface UseJog {
  active: Set<JogDir>
  startDir: (dir: JogDir) => void
  stopDir: (dir: JogDir) => void
  stopAll: () => void
}

export function useJog(robotId: string | null): UseJog {
  // Directions currently held (via keyboard or buttons). A ref drives the interval
  // (always reads the latest set without restarting it); state drives the UI.
  const activeRef = useRef<Set<JogDir>>(new Set())
  const [active, setActive] = useState<Set<JogDir>>(new Set())
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const robotIdRef = useRef(robotId)
  robotIdRef.current = robotId

  const syncActive = useCallback(() => setActive(new Set(activeRef.current)), [])

  const stopAll = useCallback(() => {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    const wasActive = activeRef.current.size > 0
    activeRef.current = new Set()
    syncActive()
    if (wasActive && robotIdRef.current) {
      fleetApi.jogStop(robotIdRef.current).catch(() => { /* best-effort stop */ })
    }
  }, [syncActive])

  // Compose the current vector and POST it once.
  const postVelocity = useCallback(() => {
    const id = robotIdRef.current
    if (!id) return
    let vx = 0, vy = 0, w = 0
    activeRef.current.forEach(dir => {
      const v = JOG_DIR_VECTORS[dir]
      vx += v.vx; vy += v.vy; w += v.w
    })
    fleetApi.jog(id, { vx, vy, w }).catch(e => {
      if (e instanceof FleetApiError) {
        if (e.status === 409)      toast.error('Jog recusado', { description: e.message })
        else if (e.status === 404) toast.error('Robô desconhecido', { description: e.message })
        else if (e.status === 400) toast.error('Comando inválido', { description: e.message })
        else                       toast.error('Falha no jog', { description: e.message })
      } else {
        toast.error('Falha no jog', { description: 'Backend inacessível' })
      }
      // Stop the runaway stream on error.
      stopAll()
    })
  }, [stopAll])

  // Begin streaming a direction. Idempotent — guards against key auto-repeat.
  const startDir = useCallback((dir: JogDir) => {
    if (!robotIdRef.current) return
    if (activeRef.current.has(dir)) return
    activeRef.current.add(dir)
    syncActive()
    postVelocity() // immediate response, then the interval keeps it alive
    if (!intervalRef.current) {
      intervalRef.current = setInterval(postVelocity, JOG_INTERVAL_MS)
    }
  }, [postVelocity, syncActive])

  // Release a direction; if none remain, stop the robot and clear the interval.
  const stopDir = useCallback((dir: JogDir) => {
    if (!activeRef.current.has(dir)) return
    activeRef.current.delete(dir)
    syncActive()
    if (activeRef.current.size === 0) {
      stopAll()
    }
  }, [stopAll, syncActive])

  // Global keyboard handlers — active while the hook is mounted.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const dir = KEY_TO_DIR[e.key.toLowerCase()]
      if (!dir) return
      if (e.repeat) { e.preventDefault(); return } // ignore auto-repeat
      e.preventDefault()
      startDir(dir)
    }
    function onKeyUp(e: KeyboardEvent) {
      const dir = KEY_TO_DIR[e.key.toLowerCase()]
      if (!dir) return
      e.preventDefault()
      stopDir(dir)
    }
    // Safety: stop everything if the window loses focus mid-hold.
    function onBlur() { stopAll() }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    window.addEventListener('blur', onBlur)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('blur', onBlur)
      stopAll() // clean up the interval + send stop on unmount
    }
  }, [startDir, stopDir, stopAll])

  // If the selected robot changes, halt the previous stream.
  useEffect(() => { stopAll() }, [robotId, stopAll])

  return { active, startDir, stopDir, stopAll }
}
