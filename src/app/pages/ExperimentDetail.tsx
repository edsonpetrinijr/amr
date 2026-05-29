import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, SkipBack, Target, TriangleAlert, Github, Search, ListTree, Activity, Expand, GitBranch, Brain, Wifi, WifiOff, Move } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useSimEngine } from '../../ml/useSimEngine';
import { ObstacleState, SpawnArea } from '../../ml/SimulationEngine';

function useWSStatus() {
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    const id = setInterval(() => {
      setConnected(typeof (window as any).__ML_ENV !== 'undefined');
    }, 1000);
    return () => clearInterval(id);
  }, []);
  return connected;
}

type DragBase = { startX: number; startY: number; origX: number; origY: number };
type DragTarget =
  | ({ kind: 'obstacle'; index: number } & DragBase)
  | ({ kind: 'target' } & DragBase)
  | ({ kind: 'spawn' } & DragBase);

export function ExperimentDetail() {
  const {
    robots: rawRobots, step, maxSteps, speed, isPlaying, mlMode,
    collisions, goalsReached, obstacles, target, spawnArea, numRobots,
    togglePlay, resetSim, setSpeed, seekStep, setMLMode,
    setObstacle, setTarget, setSpawnArea, setNumRobots,
  } = useSimEngine();

  const wsReady = useWSStatus();
  const canvasRef = useRef<HTMLDivElement>(null);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  const dragRef = useRef<DragTarget | null>(null);
  const [editMode, setEditMode] = useState(false);

  const robots = rawRobots.map(r => ({
    ...r,
    color: r.reachedGoal ? '#3fb950' : r.alive ? '#58a6ff' : '#f85149',
  }));

  // Canvas-based robot rendering — handles hundreds of agents efficiently
  useEffect(() => {
    const canvas = renderCanvasRef.current;
    const container = canvasRef.current;
    if (!canvas || !container) return;
    const { width, height } = container.getBoundingClientRect();
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);
    const r = numRobots > 100 ? 1.5 : numRobots > 50 ? 2 : 3;
    for (const robot of robots) {
      const cx = (robot.x / 100) * width;
      const cy = (robot.y / 100) * height;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = robot.color;
      ctx.fill();
      if (numRobots <= 100) {
        ctx.shadowBlur = 6;
        ctx.shadowColor = robot.color;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }
  }, [robots, numRobots]);

  // Convert pixel delta → percentage delta relative to canvas size
  const pxToPct = useCallback((dx: number, dy: number): [number, number] => {
    const el = canvasRef.current;
    if (!el) return [0, 0];
    const rect = el.getBoundingClientRect();
    return [(dx / rect.width) * 100, (dy / rect.height) * 100];
  }, []);

  const onMouseDown = useCallback((e: React.MouseEvent, info: Omit<DragTarget, 'startX' | 'startY'>) => {
    if (!editMode) return;
    e.stopPropagation();
    e.preventDefault();
    dragRef.current = { ...info, startX: e.clientX, startY: e.clientY } as DragTarget;
  }, [editMode]);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const d = dragRef.current;
      if (!d) return;
      const [dpx, dpy] = pxToPct(e.clientX - d.startX, e.clientY - d.startY);
      if (d.kind === 'obstacle') {
        setObstacle(d.index, { x: Math.max(0, Math.min(85, d.origX + dpx)), y: Math.max(0, Math.min(85, d.origY + dpy)) });
      } else if (d.kind === 'target') {
        setTarget({ x: Math.max(2, Math.min(98, d.origX + dpx)), y: Math.max(2, Math.min(98, d.origY + dpy)) });
      } else if (d.kind === 'spawn') {
        setSpawnArea({ x: Math.max(0, Math.min(70, d.origX + dpx)), y: Math.max(0, Math.min(70, d.origY + dpy)) });
      }
    };
    const onUp = () => { dragRef.current = null; };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [pxToPct, setObstacle, setTarget, setSpawnArea]);

  const togglePlay_ = togglePlay;

  const handleTimelineChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    seekStep(Number(e.target.value));
  };

  return (
    <div className="flex h-full w-full bg-[#0d1117] text-[#c9d1d9] overflow-hidden">
      
      {/* LEFT PANEL: Config (250px fixed) */}
      <div className="w-[300px] border-r border-[#30363d] flex flex-col h-full bg-[#161b22] shrink-0">
        <div className="p-4 border-b border-[#30363d] flex justify-between items-center">
          <h2 className="font-semibold text-[#e6edf3]">Configuration</h2>
          <Badge variant="outline" className="font-mono text-[10px]">READ-ONLY</Badge>
        </div>
        
        <div className="p-4 overflow-y-auto space-y-6 flex-1 text-sm">
          <div className="space-y-3">
            <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider">Source</h3>
            <div className="flex items-start gap-2 text-xs font-mono bg-[#0d1117] p-2 rounded-md border border-[#30363d]">
              <Github className="w-4 h-4 text-[#8b949e] shrink-0" />
              <div className="overflow-hidden">
                <div className="text-[#58a6ff] truncate">robotics-lab/swarm-nav</div>
                <div className="text-[#8b949e] truncate flex items-center gap-1 mt-1">
                  <GitBranch className="w-3 h-3" />
                  feature/evasion-v4
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono bg-[#0d1117] p-2 rounded-md border border-[#30363d]">
              <FileCode className="w-4 h-4 text-[#8b949e] shrink-0" />
              <span className="truncate text-[#c9d1d9]">policies/evasion.py</span>
            </div>
          </div>

          {/* ML Control Panel */}
          <div className="space-y-3">
            <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider flex items-center gap-1">
              <Brain className="w-3 h-3" /> ML Control
            </h3>
            <div className="bg-[#0d1117] p-3 rounded-md border border-[#30363d] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#8b949e]">WS Bridge</span>
                <div className="flex items-center gap-1 text-xs font-mono">
                  {wsReady
                    ? <><Wifi className="w-3 h-3 text-[#3fb950]" /><span className="text-[#3fb950]">ready</span></>
                    : <><WifiOff className="w-3 h-3 text-[#f85149]" /><span className="text-[#f85149]">offline</span></>
                  }
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#8b949e]">Mode</span>
                <Badge
                  variant="outline"
                  className={`font-mono text-[10px] cursor-pointer select-none ${mlMode ? 'border-[#58a6ff] text-[#58a6ff]' : 'border-[#30363d] text-[#8b949e]'}`}
                >
                  {mlMode ? 'ML' : 'UI'}
                </Badge>
              </div>
              <Button
                size="sm"
                className={`w-full h-8 text-xs font-mono ${mlMode ? 'bg-[#f85149]/20 border-[#f85149] text-[#f85149] hover:bg-[#f85149]/30' : 'bg-[#58a6ff]/10 border-[#58a6ff] text-[#58a6ff] hover:bg-[#58a6ff]/20'}`}
                variant="outline"
                onClick={() => setMLMode(!mlMode)}
              >
                {mlMode ? 'DISABLE ML MODE' : 'ENABLE ML MODE'}
              </Button>
              {mlMode && (
                <div className="text-[10px] font-mono text-[#8b949e] text-center border border-dashed border-[#30363d] rounded p-2">
                  Python controls sim<br />
                  ws://localhost:8765
                </div>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider">Environment</h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#0d1117] p-2 rounded-md border border-[#30363d] text-center col-span-2">
                <div className="text-xs text-[#8b949e] font-mono mb-2">AGENTS</div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost" size="icon"
                    className="w-6 h-6 text-[#8b949e] hover:text-[#e6edf3] shrink-0"
                    onClick={() => { setNumRobots(numRobots - 1); resetSim(); }}
                    disabled={numRobots <= 1}
                  >−</Button>

                  <input
                    type="range" min={1} max={500} value={numRobots}
                    onChange={e => setNumRobots(Number(e.target.value))}
                    onMouseUp={resetSim}
                    className="flex-1 h-1 accent-[#58a6ff] cursor-pointer"
                  />
                  <Button
                    variant="ghost" size="icon"
                    className="w-6 h-6 text-[#8b949e] hover:text-[#e6edf3] shrink-0"
                    onClick={() => { setNumRobots(numRobots + 1); resetSim(); }}
                    disabled={numRobots >= 500}
                  >+</Button>
                </div>
                <div className="text-2xl font-bold font-mono text-[#58a6ff] mt-1">{numRobots}</div>
                <div className="text-[10px] text-[#8b949e] font-mono">release slider to apply</div>
              </div>
              <div className="bg-[#0d1117] p-2 rounded-md border border-[#30363d] text-center">
                <div className="text-xs text-[#8b949e] font-mono">OBSTACLES</div>
                <div className="text-lg font-semibold text-[#e6edf3]">5</div>
              </div>
              <div className="bg-[#0d1117] p-2 rounded-md border border-[#30363d] text-center col-span-2 flex justify-between items-center">
                <span className="text-xs text-[#8b949e] font-mono">GRID SIZE</span>
                <span className="text-sm font-semibold text-[#e6edf3] font-mono">100x100m</span>
              </div>
               <div className="bg-[#0d1117] p-2 rounded-md border border-[#30363d] text-center col-span-2 flex justify-between items-center">
                <span className="text-xs text-[#8b949e] font-mono">SEED</span>
                <span className="text-sm text-[#e6edf3] font-mono">42089</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CENTER PANEL: 2D Simulation Viewer (Flex 1) */}
      <div className="flex-1 flex flex-col h-full bg-[#0d1117] border-r border-[#30363d] min-w-0">
        <div className="h-12 border-b border-[#30363d] flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#58a6ff]" />
            <h1 className="font-medium text-[#e6edf3] text-sm">Exp: Swarm-Evade-v4</h1>
            {mlMode && <Badge variant="outline" className="font-mono text-[10px] border-[#58a6ff] text-[#58a6ff]">ML CONTROL</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default" className="font-mono bg-[#238636] text-white hover:bg-[#2ea043] border-none">RUNNING</Badge>
            <Button variant="ghost" size="icon" className="w-8 h-8">
              <Expand className="w-4 h-4" />
            </Button>
          </div>
        </div>
        
        {/* Canvas Area */}
        <div className="flex-1 p-6 flex items-center justify-center bg-[#0d1117] overflow-hidden relative">

          <div className="absolute top-4 left-4 flex gap-2">
            <Badge variant="outline" className="bg-[#161b22] font-mono text-xs text-[#8b949e]">Time: {(step * 0.1).toFixed(1)}s</Badge>
            <Badge variant="outline" className="bg-[#161b22] font-mono text-xs text-[#8b949e]">Step: {step}/{maxSteps}</Badge>
          </div>

          {/* Edit mode toggle */}
          <div className="absolute top-4 right-4">
            <Button
              variant="outline" size="sm"
              className={`h-7 text-xs font-mono gap-1 ${editMode ? 'border-[#58a6ff] text-[#58a6ff] bg-[#58a6ff]/10' : 'border-[#30363d] text-[#8b949e]'}`}
              onClick={() => setEditMode(v => !v)}
            >
              <Move className="w-3 h-3" />
              {editMode ? 'EDITING' : 'EDIT LAYOUT'}
            </Button>
          </div>

          <div
            ref={canvasRef}
            className="aspect-square w-full max-w-[600px] bg-[#161b22] border border-[#30363d] rounded-lg relative overflow-hidden ring-1 ring-[#30363d] shadow-sm"
            style={{ cursor: editMode ? 'default' : 'auto' }}
          >
            {/* Grid Lines */}
            <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(#30363d 1px, transparent 1px), linear-gradient(90deg, #30363d 1px, transparent 1px)', backgroundSize: '20px 20px', opacity: 0.2 }} />

            {/* Spawn Area */}
            <div
              className={`absolute border border-dashed rounded-sm transition-colors ${editMode ? 'border-[#58a6ff]/60 bg-[#58a6ff]/5 cursor-grab active:cursor-grabbing hover:bg-[#58a6ff]/10' : 'border-[#58a6ff]/20 bg-[#58a6ff]/5'}`}
              style={{ left: `${spawnArea.x}%`, top: `${spawnArea.y}%`, width: `${spawnArea.w}%`, height: `${spawnArea.h}%` }}
              onMouseDown={e => onMouseDown(e, { kind: 'spawn', origX: spawnArea.x, origY: spawnArea.y })}
            >
              {editMode && (
                <span className="absolute top-1 left-1 text-[9px] font-mono text-[#58a6ff]/60 select-none">SPAWN</span>
              )}
            </div>

            {/* Obstacles */}
            {obstacles.map((o, i) => (
              <div
                key={i}
                className={`absolute rounded-sm transition-colors ${editMode ? 'bg-[#8b949e] cursor-grab active:cursor-grabbing hover:bg-[#c9d1d9] ring-1 ring-[#58a6ff]' : 'bg-[#30363d]'}`}
                style={{ left: `${o.x}%`, top: `${o.y}%`, width: `${o.w}%`, height: `${o.h}%` }}
                onMouseDown={e => onMouseDown(e, { kind: 'obstacle', index: i, origX: o.x, origY: o.y })}
              />
            ))}

            {/* Target */}
            <div
              className={`absolute flex items-center justify-center rounded-full border-2 border-dashed border-[#3fb950] bg-[#3fb950]/10 ${editMode ? 'cursor-grab active:cursor-grabbing hover:bg-[#3fb950]/20 ring-1 ring-[#3fb950]' : 'animate-pulse'}`}
              style={{
                left: `${target.x}%`,
                top: `${target.y}%`,
                width: `${target.radius * 2}%`,
                height: `${target.radius * 2}%`,
                transform: 'translate(-50%, -50%)',
              }}
              onMouseDown={e => onMouseDown(e, { kind: 'target', origX: target.x, origY: target.y })}
            >
              <Target className="w-4 h-4 text-[#3fb950]" />
            </div>

            {/* Robots — canvas for performance */}
            <canvas ref={renderCanvasRef} className="absolute inset-0 w-full h-full pointer-events-none" />

            {/* Edit mode hint */}
            {editMode && (
              <div className="absolute bottom-2 left-0 right-0 flex justify-center pointer-events-none">
                <span className="text-[9px] font-mono text-[#58a6ff]/50 bg-[#0d1117]/70 px-2 py-0.5 rounded">drag obstacles · target · spawn area</span>
              </div>
            )}
          </div>
        </div>

        {/* Playback Controls */}
        <div className="h-24 border-t border-[#30363d] bg-[#161b22] p-4 shrink-0 flex flex-col justify-center gap-3">
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono text-[#8b949e] w-12 text-right">{step}</span>
            <input 
              type="range" 
              min="0" 
              max={maxSteps} 
              value={step}
              onChange={handleTimelineChange}
              className="flex-1 h-1.5 bg-[#30363d] rounded-lg appearance-none cursor-pointer accent-[#58a6ff]"
            />
            <span className="text-xs font-mono text-[#8b949e] w-12">{maxSteps}</span>
          </div>
          
          <div className="flex items-center justify-between px-2">
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" className="h-8 text-xs font-mono" onClick={() => setSpeed(0.5)} disabled={speed === 0.5 || mlMode}>0.5x</Button>
              <Button variant="ghost" size="sm" className="h-8 text-xs font-mono" onClick={() => setSpeed(1)} disabled={speed === 1 || mlMode}>1.0x</Button>
              <Button variant="ghost" size="sm" className="h-8 text-xs font-mono" onClick={() => setSpeed(2)} disabled={speed === 2 || mlMode}>2.0x</Button>
            </div>
            
            <div className="flex items-center gap-3">
              <Button variant="outline" size="icon" className="w-8 h-8 rounded-full" onClick={resetSim}>
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button variant="primary" size="icon" className="w-10 h-10 rounded-full bg-[#238636] hover:bg-[#2ea043] border-none text-white" onClick={togglePlay_} disabled={mlMode}>
                {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-1" />}
              </Button>
            </div>

            <div className="w-[120px] text-right text-xs text-[#8b949e] font-mono">
              FPS: {isPlaying ? (20 * speed).toFixed(0) : '0'}
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Behavior & Logs (320px fixed) */}
      <div className="w-[350px] bg-[#161b22] shrink-0 flex flex-col h-full">
        <div className="p-4 border-b border-[#30363d] flex justify-between items-center bg-[#161b22]">
          <h2 className="font-semibold text-[#e6edf3]">Runtime Logs</h2>
          <Button variant="ghost" size="icon" className="h-6 w-6">
            <Search className="w-3.5 h-3.5 text-[#8b949e]" />
          </Button>
        </div>
        
        {/* Quick Stats Summary */}
        <div className="grid grid-cols-2 gap-px bg-[#30363d] border-b border-[#30363d]">
          <div className="bg-[#161b22] p-3 text-center">
             <div className="text-[10px] text-[#8b949e] font-mono mb-1 flex items-center justify-center gap-1">
               <TriangleAlert className="w-3 h-3 text-[#d29922]" /> COLLISIONS
             </div>
             <div className="text-xl font-bold text-[#e6edf3] font-mono">{collisions}</div>
          </div>
          <div className="bg-[#161b22] p-3 text-center">
             <div className="text-[10px] text-[#8b949e] font-mono mb-1 flex items-center justify-center gap-1">
               <Target className="w-3 h-3 text-[#3fb950]" /> GOALS MET
             </div>
             <div className="text-xl font-bold text-[#e6edf3] font-mono">{goalsReached}</div>
          </div>
        </div>

        {/* Log List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 bg-[#0d1117] min-h-0">
          {Array.from({ length: Math.min(step, 50) }).map((_, i) => {
            const currentLogStep = step - i;
            if (currentLogStep <= 0) return null;
            
            const isCollision = currentLogStep % 145 === 0;
            const isGoal = currentLogStep % 400 === 0;
            const logType = isCollision ? 'warn' : isGoal ? 'success' : 'info';
            
            return (
              <div key={currentLogStep} className="flex gap-2 text-xs font-mono p-2 rounded-md hover:bg-[#21262d] transition-colors border border-transparent hover:border-[#30363d] cursor-pointer">
                <div className="text-[#8b949e] w-12 shrink-0 select-none border-r border-[#30363d] mr-1">
                  {currentLogStep.toString().padStart(4, '0')}
                </div>
                <div className="flex-1 truncate">
                  {isCollision ? (
                    <span className="text-[#d29922]">Collision detected: Agent-2 & Wall</span>
                  ) : isGoal ? (
                    <span className="text-[#3fb950]">Agent-5 reached target zone</span>
                  ) : (
                    <span className="text-[#c9d1d9]">Velocity update vector [{Math.random().toFixed(2)}, {Math.random().toFixed(2)}]</span>
                  )}
                </div>
              </div>
            )
          })}
          {step === 0 && (
             <div className="h-full flex items-center justify-center text-[#8b949e] text-sm font-mono flex-col gap-2 opacity-50">
               <ListTree className="w-8 h-8" />
               Waiting for execution...
             </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FileCode(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="m10 13-2 2 2 2"/><path d="m14 17 2-2-2-2"/></svg>
  )
}
