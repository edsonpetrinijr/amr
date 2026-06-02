import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SplitSquareHorizontal, MoveHorizontal, Maximize2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

interface Robot {
  id: number;
  x: number;
  y: number;
  color: string;
}

function MockSimulation({ seed, step, title, color }: { seed: number; step: number, title: string, color: string }) {
  // Generate deterministic-ish positions based on seed and step
  const getRobots = () => {
    return Array.from({ length: 8 }).map((_, i) => ({
      id: i,
      x: 10 + ((i * 10 + step * 0.1 * (seed % 3 + 1)) % 80),
      y: 10 + ((i * 15 + step * 0.15 * (seed % 2 + 1)) % 80),
      color: color
    }));
  };
  
  const robots = getRobots();

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0d1117] border-r border-[#30363d] last:border-0 relative">
      <div className="h-10 border-b border-[#30363d] flex items-center justify-between px-3 bg-[#161b22]">
        <div className="font-mono text-xs text-[#e6edf3] font-semibold">{title}</div>
        <div className="flex gap-2">
          <Badge variant="outline" className="text-[10px] font-mono border-[#30363d] text-[#8b949e]">SEED: {seed}</Badge>
          <Button variant="ghost" size="icon" className="w-6 h-6">
             <Maximize2 className="w-3 h-3 text-[#8b949e]" />
          </Button>
        </div>
      </div>
      <div className="flex-1 relative overflow-hidden flex items-center justify-center p-4">
        
        {/* Highlight divergence point mock */}
        {step > 150 && step < 200 && (
          <div className="absolute top-[40%] left-[40%] w-32 h-32 border border-[#d29922] bg-[#d29922]/5 rounded-full animate-pulse flex items-center justify-center">
            <span className="text-[10px] text-[#d29922] font-mono absolute -top-4 whitespace-nowrap">DIVERGENCE DETECTED</span>
          </div>
        )}

        <div className="aspect-square w-full max-w-[500px] border border-[#30363d] rounded bg-[#161b22] relative overflow-hidden">
          {/* Grid */}
          <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(#30363d 1px, transparent 1px), linear-gradient(90deg, #30363d 1px, transparent 1px)', backgroundSize: '20px 20px', opacity: 0.15 }}></div>
          
          {/* Obstacles */}
          <div className="absolute w-[20%] h-[20%] bg-[#30363d] rounded-sm top-[30%] left-[40%]"></div>
          
          {/* Robots */}
          {robots.map(r => (
            <div 
              key={r.id}
              className="absolute w-2 h-2 rounded-full transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center transition-all duration-75"
              style={{ 
                left: `${r.x}%`, 
                top: `${r.y}%`,
                backgroundColor: r.color,
                boxShadow: `0 0 8px ${r.color}80`
              }}
            >
              <div className="absolute -top-4 text-[9px] font-mono text-[#8b949e] opacity-0 hover:opacity-100 bg-[#0d1117] px-1 rounded border border-[#30363d]">R{r.id}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function Comparison() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [step, setStep] = useState(0);
  const maxSteps = 400;

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isPlaying) {
      interval = setInterval(() => {
        setStep(s => {
          if (s >= maxSteps) {
            setIsPlaying(false);
            return s;
          }
          return s + 1;
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const togglePlay = () => setIsPlaying(!isPlaying);

  return (
    <div className="flex flex-col h-full w-full bg-[#0d1117] text-[#c9d1d9] overflow-hidden">
      
      {/* Header */}
      <div className="h-14 border-b border-[#30363d] flex items-center justify-between px-6 bg-[#161b22] shrink-0">
        <div className="flex items-center gap-3">
          <SplitSquareHorizontal className="w-5 h-5 text-[#8b949e]" />
          <h1 className="font-semibold text-[#e6edf3]">Compare Runs</h1>
          <Badge variant="outline" className="ml-2 font-mono text-xs border-[#30363d]">Swarm-Evade-v4</Badge>
        </div>
        <div className="flex items-center gap-2">
           <Button variant="outline" size="sm" className="font-mono text-xs">Swap Views <MoveHorizontal className="w-3 h-3 ml-2" /></Button>
        </div>
      </div>

      {/* Split View */}
      <div className="flex-1 flex min-h-0">
        <MockSimulation seed={42} step={step} title="Run A: Baseline (Heuristic)" color="#8b949e" />
        <MockSimulation seed={99} step={step} title="Run B: PPO Agent (Epoch 500)" color="#58a6ff" />
      </div>

      {/* Sync Playback & Metrics Table (Bottom Panel) */}
      <div className="h-64 border-t border-[#30363d] bg-[#161b22] shrink-0 flex flex-col">
        {/* Playback */}
        <div className="h-14 border-b border-[#30363d] flex items-center px-4 gap-4 bg-[#0d1117]">
          <Button variant="primary" size="icon" className="w-8 h-8 rounded-full bg-[#238636] hover:bg-[#2ea043] border-none text-white shrink-0" onClick={togglePlay}>
            {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
          </Button>
          <Button variant="outline" size="icon" className="w-8 h-8 rounded-full shrink-0" onClick={() => setStep(0)}>
            <SkipBack className="w-4 h-4 text-[#8b949e]" />
          </Button>
          
          <div className="flex-1 flex items-center gap-4 px-4">
            <span className="text-xs font-mono text-[#8b949e] w-8 text-right">{step}</span>
            <input 
              type="range" 
              min="0" 
              max={maxSteps} 
              value={step}
              onChange={(e) => setStep(Number(e.target.value))}
              className="flex-1 h-1.5 bg-[#30363d] rounded-lg appearance-none cursor-pointer accent-[#238636]"
            />
            <span className="text-xs font-mono text-[#8b949e] w-8">{maxSteps}</span>
          </div>
        </div>

        {/* Metrics Table */}
        <div className="flex-1 overflow-auto p-4">
           <table className="w-full text-sm text-left border-collapse">
            <thead className="text-xs font-mono text-[#8b949e] uppercase bg-[#0d1117] border border-[#30363d]">
              <tr>
                <th className="px-4 py-2 font-medium border-r border-[#30363d]">Metric</th>
                <th className="px-4 py-2 font-medium border-r border-[#30363d] text-center w-1/3">Run A (Baseline)</th>
                <th className="px-4 py-2 font-medium text-center w-1/3">Run B (PPO Agent)</th>
              </tr>
            </thead>
            <tbody className="border border-t-0 border-[#30363d] font-mono text-xs">
              <tr className="border-b border-[#30363d] hover:bg-[#21262d]/50">
                <td className="px-4 py-2 border-r border-[#30363d] text-[#c9d1d9]">Collision Count</td>
                <td className="px-4 py-2 border-r border-[#30363d] text-center text-[#f85149]">14</td>
                <td className="px-4 py-2 text-center text-[#3fb950] font-bold">2</td>
              </tr>
              <tr className="border-b border-[#30363d] hover:bg-[#21262d]/50">
                <td className="px-4 py-2 border-r border-[#30363d] text-[#c9d1d9]">Time to Goal (avg)</td>
                <td className="px-4 py-2 border-r border-[#30363d] text-center">45.2s</td>
                <td className="px-4 py-2 text-center text-[#3fb950] font-bold">38.1s</td>
              </tr>
              <tr className="border-b border-[#30363d] hover:bg-[#21262d]/50">
                <td className="px-4 py-2 border-r border-[#30363d] text-[#c9d1d9]">Efficiency Score</td>
                <td className="px-4 py-2 border-r border-[#30363d] text-center">0.65</td>
                <td className="px-4 py-2 text-center text-[#3fb950] font-bold">0.89</td>
              </tr>
              <tr className="hover:bg-[#21262d]/50">
                <td className="px-4 py-2 border-r border-[#30363d] text-[#c9d1d9]">Failure Rate</td>
                <td className="px-4 py-2 border-r border-[#30363d] text-center text-[#f85149]">15%</td>
                <td className="px-4 py-2 text-center text-[#3fb950] font-bold">0%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}