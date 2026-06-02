import React, { useState } from 'react';
import { Settings, Save, Github, RefreshCw, Hash, Sliders, Map, MapPin } from 'lucide-react';
import { globalEngine } from '../../ml/SimulationEngine';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

export function SwarmConfig() {
  const [seed, setSeed] = useState(42089);
  const [agents, setAgents] = useState(12);
  const [density, setDensity] = useState(25);

  const generateSeed = () => {
    setSeed(Math.floor(Math.random() * 100000));
  };

  return (
    <div className="flex-1 overflow-auto bg-[#0d1117] p-8 text-[#c9d1d9] font-sans">
      <div className="max-w-4xl mx-auto">
        
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-[#e6edf3]">Swarm Configuration</h1>
            <p className="text-[#8b949e] text-sm mt-1">Define execution parameters for the next multi-agent run.</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="flex items-center gap-2">
              <Save className="w-4 h-4" />
              Save Preset
            </Button>
            <Button variant="primary" className="flex items-center gap-2 bg-[#238636] hover:bg-[#2ea043] border-none text-white" onClick={() => globalEngine.setNumRobots(agents)}>
              <RefreshCw className="w-4 h-4" />
              Apply & Run
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Policy & Source */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Github className="w-4 h-4 text-[#8b949e]" />
                Behavior Policy Source
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-mono text-[#8b949e] uppercase">Repository URL</label>
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    defaultValue="https://github.com/robotics-lab/swarm-nav" 
                    className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-sm font-mono text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff]"
                  />
                  <Button variant="outline">Fetch</Button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-mono text-[#8b949e] uppercase">Branch / Commit</label>
                  <select className="w-full bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-sm font-mono text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff] appearance-none cursor-pointer">
                    <option>main</option>
                    <option>feature/evasion-v4</option>
                    <option>bugfix/collision-detection</option>
                    <option>c9a8b72</option>
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-xs font-mono text-[#8b949e] uppercase">Policy File</label>
                  <select className="w-full bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-sm font-mono text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff] appearance-none cursor-pointer">
                    <option>policies/baseline.py</option>
                    <option>policies/evasion.py</option>
                    <option>policies/formation.py</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Seed Control */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Hash className="w-4 h-4 text-[#8b949e]" />
                Reproducibility
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-mono text-[#8b949e] uppercase">Environment Seed</label>
                <div className="flex gap-2">
                  <input 
                    type="number" 
                    value={seed}
                    onChange={(e) => setSeed(Number(e.target.value))}
                    className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-sm font-mono text-[#58a6ff] font-bold focus:outline-none focus:border-[#58a6ff]"
                  />
                  <Button variant="outline" size="icon" onClick={generateSeed}>
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-xs text-[#8b949e] mt-1">Controls initial placement and RNG for deterministic execution.</p>
              </div>
            </CardContent>
          </Card>

          {/* Environment Presets */}
          <Card className="lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Map className="w-4 h-4 text-[#8b949e]" />
                Environment Parameters
              </CardTitle>
              <Badge variant="outline" className="text-[#8b949e] border-[#30363d] text-xs font-mono">2D GRID - 100x100m</Badge>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                {/* Agent Count */}
                <div className="space-y-6">
                  <div className="flex justify-between items-center border-b border-[#30363d] pb-2">
                    <div className="flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-[#8b949e]" />
                      <span className="text-sm font-medium">Agent Population (N)</span>
                    </div>
                    <span className="font-mono text-xl text-[#58a6ff]">{agents}</span>
                  </div>
                  
                  <div className="space-y-3">
                     <input 
                      type="range" 
                      min="1" 
                      max="100" 
                      value={agents}
                      onChange={(e) => setAgents(Number(e.target.value))}
                      className="w-full h-1.5 bg-[#30363d] rounded-lg appearance-none cursor-pointer accent-[#58a6ff]"
                    />
                    <div className="flex justify-between text-xs font-mono text-[#8b949e]">
                      <span>1</span>
                      <span>50</span>
                      <span>100</span>
                    </div>
                  </div>
                </div>

                {/* Obstacle Density */}
                <div className="space-y-6">
                  <div className="flex justify-between items-center border-b border-[#30363d] pb-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-[#8b949e]" />
                      <span className="text-sm font-medium">Obstacle Density (%)</span>
                    </div>
                    <span className="font-mono text-xl text-[#d29922]">{density}%</span>
                  </div>
                  
                  <div className="space-y-3">
                     <input 
                      type="range" 
                      min="0" 
                      max="50" 
                      value={density}
                      onChange={(e) => setDensity(Number(e.target.value))}
                      className="w-full h-1.5 bg-[#30363d] rounded-lg appearance-none cursor-pointer accent-[#d29922]"
                    />
                    <div className="flex justify-between text-xs font-mono text-[#8b949e]">
                      <span>Sparse</span>
                      <span>Moderate</span>
                      <span>Dense</span>
                    </div>
                  </div>
                </div>
                
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}