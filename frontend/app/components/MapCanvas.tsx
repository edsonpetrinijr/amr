/**
 * MapCanvas — SVG renderer for a .smap MapModel + live robots.
 *
 * Coordinate system: SEER uses metres with y-up. SVG uses y-down.
 * We flip y: svgY = (maxY - realY) * scale
 *
 * Props:
 *   map          — MapModel from the backend
 *   robots       — live robot array
 *   stations     — station array (for AP markers)
 *   onClickAP    — called when user clicks an action point / station
 *   onClickRobot — called when user clicks a robot
 *   selectedId   — highlight a robot or station id
 */
import React, { useMemo, useRef, useState, useCallback, useEffect } from 'react'
import type { MapModel, Robot, Station, Pos2D, Route } from '../api/types'

interface Props {
  map: MapModel
  robots?: Robot[]
  stations?: Station[]
  onClickAP?: (station: Station) => void
  onClickRobot?: (robot: Robot) => void
  selectedId?: string | null
  className?: string
}

// Canvas fixed size — we scale the world into this viewport
const W = 900
const H = 700

function useTransform(map: MapModel) {
  return useMemo(() => {
    const worldW = map.max_pos.x - map.min_pos.x
    const worldH = map.max_pos.y - map.min_pos.y
    const scaleX = (W - 40) / worldW
    const scaleY = (H - 40) / worldH
    const scale  = Math.min(scaleX, scaleY)
    const offX   = 20 - map.min_pos.x * scale
    const offY   = 20 + map.max_pos.y * scale  // y-flip origin

    const tx = (x: number) => x * scale + offX
    const ty = (y: number) => offY - y * scale   // flip

    return { tx, ty, scale }
  }, [map])
}

// Status colours
const STATUS_COLOR: Record<string, string> = {
  idle:           '#3fb950',
  enroute_pickup: '#58a6ff',
  at_pickup:      '#d29922',
  enroute_drop:   '#58a6ff',
  returning:      '#8b949e',
  charging:       '#d29922',
  error:          '#f85149',
  offline:        '#6e7681',
}

const STATION_COLOR: Record<string, string> = {
  callbutton: '#d29922',
  base:       '#3fb950',
  ap:         '#58a6ff',
}

export function MapCanvas({ map, robots = [], stations = [], onClickAP, onClickRobot, selectedId, className }: Props) {
  const { tx, ty, scale } = useTransform(map)

  // ── Camera (pan + zoom) — manipulate the SVG viewBox ─────────────
  const svgRef = useRef<SVGSVGElement | null>(null)
  const [view, setView] = useState({ x: 0, y: 0, w: W, h: H })
  const dragRef = useRef<{ startX: number; startY: number; viewX: number; viewY: number } | null>(null)
  const didDragRef = useRef(false)

  // Reset view when the map changes (new map = new scale)
  useEffect(() => { setView({ x: 0, y: 0, w: W, h: H }) }, [map])

  // Convert client (mouse) coords → SVG user coords using current viewBox
  const clientToSvg = useCallback((clientX: number, clientY: number) => {
    const el = svgRef.current
    if (!el) return { x: 0, y: 0 }
    const rect = el.getBoundingClientRect()
    const px = (clientX - rect.left) / rect.width
    const py = (clientY - rect.top)  / rect.height
    return { x: view.x + px * view.w, y: view.y + py * view.h }
  }, [view])

  const onWheel = useCallback((e: React.WheelEvent<SVGSVGElement>) => {
    e.preventDefault()
    const zoomFactor = Math.exp(e.deltaY * 0.0015) // smooth zoom; >1 zoom out, <1 zoom in
    // Clamp zoom: viewBox width between W*0.1 (10x in) and W*5 (5x out)
    const newW = Math.max(W * 0.1, Math.min(W * 5, view.w * zoomFactor))
    const newH = newW * (H / W)
    const { x: mx, y: my } = clientToSvg(e.clientX, e.clientY)
    // Keep the point under the cursor stationary
    const k = newW / view.w
    setView({
      x: mx - (mx - view.x) * k,
      y: my - (my - view.y) * k,
      w: newW,
      h: newH,
    })
  }, [view, clientToSvg])

  const onPointerDown = useCallback((e: React.PointerEvent<SVGSVGElement>) => {
    // Only start panning on primary or middle button, and not on interactive children
    if (e.button !== 0 && e.button !== 1) return
    dragRef.current = { startX: e.clientX, startY: e.clientY, viewX: view.x, viewY: view.y }
    didDragRef.current = false
    ;(e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId)
  }, [view])

  const onPointerMove = useCallback((e: React.PointerEvent<SVGSVGElement>) => {
    const d = dragRef.current
    if (!d) return
    const el = svgRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const dx = (e.clientX - d.startX) * (view.w / rect.width)
    const dy = (e.clientY - d.startY) * (view.h / rect.height)
    if (Math.abs(e.clientX - d.startX) + Math.abs(e.clientY - d.startY) > 3) didDragRef.current = true
    setView(v => ({ ...v, x: d.viewX - dx, y: d.viewY - dy }))
  }, [view.w, view.h])

  const endDrag = useCallback((e: React.PointerEvent<SVGSVGElement>) => {
    if (dragRef.current) {
      try { (e.currentTarget as SVGSVGElement).releasePointerCapture(e.pointerId) } catch {}
    }
    dragRef.current = null
  }, [])

  // Swallow clicks that were actually drags (so robots/stations aren't selected on drag-release)
  const onClickCapture = useCallback((e: React.MouseEvent) => {
    if (didDragRef.current) {
      e.stopPropagation()
      e.preventDefault()
      didDragRef.current = false
    }
  }, [])

  const resetView = () => setView({ x: 0, y: 0, w: W, h: H })

  // Nav points — render as tiny dots for the drivable area cloud
  // Downsample to max 600 pts for perf
  const navSample = useMemo(() => {
    const step = Math.max(1, Math.floor(map.nav_points.length / 600))
    return map.nav_points.filter((_, i) => i % step === 0)
  }, [map.nav_points])

  return (
    <svg
      ref={svgRef}
      viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
      className={className}
      style={{
        background: '#0d1117',
        width: '100%',
        height: '100%',
        cursor: dragRef.current ? 'grabbing' : 'grab',
        touchAction: 'none',
      }}
      onWheel={onWheel}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      onClickCapture={onClickCapture}
      onDoubleClick={resetView}
    >
      {/* ── Grid background ─────────────────────────────────────────── */}
      <defs>
        <pattern id="grid" width={scale} height={scale} patternUnits="userSpaceOnUse"
          x={tx(0) % scale} y={ty(0) % scale}>
          <path d={`M ${scale} 0 L 0 0 0 ${scale}`} fill="none" stroke="#21262d" strokeWidth="0.5" />
        </pattern>
      </defs>
      <rect width={W} height={H} fill="url(#grid)" />

      {/* ── Nav cloud (drivable area) ────────────────────────────────── */}
      {navSample.map((p, i) => (
        <circle key={i} cx={tx(p.x)} cy={ty(p.y)} r={1.2} fill="#1c2128" />
      ))}

      {/* ── Walls / feature lines ────────────────────────────────────── */}
      {map.walls.map((w, i) => (
        <line key={i}
          x1={tx(w.start.x)} y1={ty(w.start.y)}
          x2={tx(w.end.x)}   y2={ty(w.end.y)}
          stroke="#58a6ff" strokeWidth={1.5} strokeOpacity={0.6}
        />
      ))}

      {/* ── Routes (LM paths from advancedCurveList) ─────────────────────── */}
      {(map.routes ?? []).map((r, i) => {
        const x1 = tx(r.start.x), y1 = ty(r.start.y)
        const x2 = tx(r.ctrl1.x), y2 = ty(r.ctrl1.y)
        const x3 = tx(r.ctrl2.x), y3 = ty(r.ctrl2.y)
        const x4 = tx(r.end.x),   y4 = ty(r.end.y)
        const d = `M ${x1} ${y1} C ${x2} ${y2}, ${x3} ${y3}, ${x4} ${y4}`
        // For one-way routes, draw a small arrowhead near the end
        const ang = Math.atan2(y4 - y3, x4 - x3)
        const aw = 6
        const arrowD = r.direction !== 0
          ? `M ${x4} ${y4} l ${-aw * Math.cos(ang - 0.4)} ${-aw * Math.sin(ang - 0.4)} M ${x4} ${y4} l ${-aw * Math.cos(ang + 0.4)} ${-aw * Math.sin(ang + 0.4)}`
          : ''
        return (
          <g key={i}>
            <path d={d} fill="none" stroke="#30a46c" strokeWidth={1.5}
              strokeOpacity={0.7} strokeDasharray={r.direction === 0 ? undefined : '5 3'} />
            {r.direction !== 0 && (
              <path d={arrowD} fill="none" stroke="#30a46c" strokeWidth={1.5} strokeLinecap="round" />
            )}
          </g>
        )
      })}

      {/* ── Areas ────────────────────────────────────────────────────── */}
      {map.areas.map(area => {
        if (area.points.length < 3) return null
        const pts = area.points.map(p => `${tx(p.x)},${ty(p.y)}`).join(' ')
        const color = area.class_name.toLowerCase().includes('charge') ? '#d29922'
                    : area.class_name.toLowerCase().includes('forbidden') ? '#f85149'
                    : '#3fb950'
        return (
          <polygon key={area.id} points={pts}
            fill={color + '20'} stroke={color} strokeWidth={1} strokeOpacity={0.5}
          />
        )
      })}

      {/* ── Landmarks ────────────────────────────────────────────────── */}
      {map.landmarks.map(lm => (
        <g key={lm.id} transform={`translate(${tx(lm.x)},${ty(lm.y)})`}>
          <circle r={5} fill="#8b949e22" stroke="#8b949e" strokeWidth={1} />
          <text y={-8} textAnchor="middle" fill="#8b949e" fontSize={9} fontFamily="monospace">
            {lm.id}
          </text>
        </g>
      ))}

      {/* ── Stations ─────────────────────────────────────────────────── */}
      {stations.map(s => {
        const color  = STATION_COLOR[s.type] ?? '#58a6ff'
        const isSelected = s.id === selectedId
        const size   = s.type === 'base' ? 10 : 7
        return (
          <g key={s.id}
            transform={`translate(${tx(s.x)},${ty(s.y)})`}
            onClick={() => onClickAP?.(s)}
            style={{ cursor: onClickAP ? 'pointer' : 'default' }}
          >
            {s.type === 'base' ? (
              <rect x={-size} y={-size} width={size*2} height={size*2}
                fill={color + '30'} stroke={color} strokeWidth={isSelected ? 2.5 : 1.5}
                rx={2}
              />
            ) : (
              <circle r={size}
                fill={color + '25'} stroke={color} strokeWidth={isSelected ? 2.5 : 1.5}
              />
            )}
            {/* Callbutton blink ring when called */}
            {s.type === 'callbutton' && s.cb_state === 'called' && (
              <circle r={size + 4} fill="none" stroke={color} strokeWidth={1} strokeOpacity={0.4}>
                <animate attributeName="r" values={`${size+2};${size+8};${size+2}`} dur="1.4s" repeatCount="indefinite" />
                <animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="1.4s" repeatCount="indefinite" />
              </circle>
            )}
            <text y={size + 11} textAnchor="middle" fill={color} fontSize={8} fontFamily="monospace">
              {s.label.length > 14 ? s.label.slice(0, 13) + '…' : s.label}
            </text>
          </g>
        )
      })}

      {/* ── Robots ───────────────────────────────────────────────────── */}
      {robots.map(r => {
        const color     = STATUS_COLOR[r.status] ?? '#8b949e'
        const isSelected = r.id === selectedId
        const cx = tx(r.x)
        const cy = ty(r.y)
        const bodyR = 10
        // Direction arrow end point (SEER theta: 0=east, CCW positive → svg-flipped)
        const arrowLen = bodyR + 8
        const ax = cx + arrowLen * Math.cos(r.theta)
        const ay = cy - arrowLen * Math.sin(r.theta) // y-flipped

        return (
          <g key={r.id}
            onClick={() => onClickRobot?.(r)}
            style={{ cursor: onClickRobot ? 'pointer' : 'default' }}
          >
            {/* Selection ring */}
            {isSelected && (
              <circle cx={cx} cy={cy} r={bodyR + 6}
                fill="none" stroke={color} strokeWidth={1.5} strokeOpacity={0.5} strokeDasharray="4 2" />
            )}
            {/* Body */}
            <circle cx={cx} cy={cy} r={bodyR}
              fill={color + '30'} stroke={color} strokeWidth={2}
            />
            {/* Direction arrow */}
            {r.status !== 'offline' && (
              <line x1={cx} y1={cy} x2={ax} y2={ay}
                stroke={color} strokeWidth={2} strokeLinecap="round"
              />
            )}
            {/* ID label */}
            <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle"
              fill={color} fontSize={7} fontFamily="monospace" fontWeight="bold">
              {r.id.replace('AMR-', '')}
            </text>
            {/* Battery mini bar */}
            <rect x={cx - bodyR} y={cy + bodyR + 3} width={bodyR * 2} height={3}
              fill="#21262d" rx={1.5} />
            <rect x={cx - bodyR} y={cy + bodyR + 3}
              width={bodyR * 2 * (r.battery / 100)} height={3}
              fill={r.battery < 25 ? '#f85149' : color} rx={1.5} />
          </g>
        )
      })}
    </svg>
  )
}
