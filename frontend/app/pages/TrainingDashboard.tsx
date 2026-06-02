import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, TriangleAlert, Bot, Wifi, WifiOff, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import { metricsStore, EpisodeMetrics } from '../../ml/metricsStore';

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color: string }) {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex flex-col gap-1">
      <span className="text-[10px] font-mono text-[#8b949e] uppercase tracking-wider">{label}</span>
      <span className="text-2xl font-bold font-mono" style={{ color }}>{value}</span>
      {sub && <span className="text-xs font-mono text-[#8b949e]">{sub}</span>}
    </div>
  );
}

const CHART_TOOLTIP_STYLE = {
  backgroundColor: '#161b22',
  border: '1px solid #30363d',
  borderRadius: 6,
  color: '#c9d1d9',
  fontFamily: 'monospace',
  fontSize: 12,
};

export function TrainingDashboard() {
  const [episodes, setEpisodes] = useState<EpisodeMetrics[]>(() => metricsStore.episodes);
  const [wsReady, setWsReady] = useState(false);

  useEffect(() => {
    const onUpdate = (e: Event) => {
      setEpisodes((e as CustomEvent<EpisodeMetrics[]>).detail);
    };
    metricsStore.addEventListener('update', onUpdate);

    const wsCheck = setInterval(() => {
      setWsReady(typeof (window as any).__ML_ENV !== 'undefined');
    }, 1000);

    return () => {
      metricsStore.removeEventListener('update', onUpdate);
      clearInterval(wsCheck);
    };
  }, []);

  const last = episodes[episodes.length - 1];
  const bestReward = episodes.length ? Math.max(...episodes.map(e => e.totalReward)) : 0;
  const avgGoals = episodes.length
    ? (episodes.reduce((s, e) => s + e.goals, 0) / episodes.length).toFixed(1)
    : '—';

  // Moving average helper
  const withMA = (data: EpisodeMetrics[], key: keyof EpisodeMetrics, window = 5) =>
    data.map((ep, i) => {
      const slice = data.slice(Math.max(0, i - window + 1), i + 1);
      const avg = slice.reduce((s, d) => s + (d[key] as number), 0) / slice.length;
      return { episode: ep.episode, value: ep[key], ma: parseFloat(avg.toFixed(2)) };
    });

  const rewardData = withMA(episodes, 'totalReward');
  const goalsData = withMA(episodes, 'goals');
  const collisionsData = withMA(episodes, 'collisions');
  const aliveData = episodes.map(e => ({ episode: e.episode, value: e.aliveAtEnd }));

  return (
    <div className="flex flex-col h-full bg-[#0d1117] overflow-auto">
      {/* Header */}
      <div className="h-12 border-b border-[#30363d] flex items-center justify-between px-6 shrink-0 bg-[#161b22]">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-[#58a6ff]" />
          <span className="font-medium text-[#e6edf3] text-sm">Training Dashboard</span>
          {episodes.length > 0 && (
            <Badge variant="outline" className="font-mono text-[10px] border-[#58a6ff] text-[#58a6ff]">
              {episodes.length} episodes
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 text-xs font-mono">
            {wsReady
              ? <><Wifi className="w-3 h-3 text-[#3fb950]" /><span className="text-[#3fb950]">bridge ready</span></>
              : <><WifiOff className="w-3 h-3 text-[#f85149]" /><span className="text-[#f85149]">bridge offline</span></>
            }
          </div>
          <Button
            variant="ghost" size="sm"
            className="h-7 text-xs font-mono text-[#8b949e] hover:text-[#f85149]"
            onClick={() => metricsStore.clear()}
            disabled={episodes.length === 0}
          >
            <Trash2 className="w-3 h-3 mr-1" /> Clear
          </Button>
        </div>
      </div>

      {episodes.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-[#8b949e]">
          <Bot className="w-12 h-12 opacity-30" />
          <div className="text-sm font-mono text-center">
            <div>No training data yet.</div>
            <div className="text-xs mt-1 opacity-60">Run <span className="text-[#58a6ff]">python ml/demo.py</span> or <span className="text-[#58a6ff]">python ml/train_ppo.py</span></div>
          </div>
        </div>
      ) : (
        <div className="flex-1 p-6 space-y-6 overflow-auto">
          {/* Stat cards */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard
              label="Episodes"
              value={episodes.length}
              color="#58a6ff"
            />
            <StatCard
              label="Best Reward"
              value={bestReward.toFixed(1)}
              sub={`last: ${last?.totalReward.toFixed(1) ?? '—'}`}
              color="#3fb950"
            />
            <StatCard
              label="Avg Goals / ep"
              value={avgGoals}
              sub={`last: ${last?.goals ?? '—'}`}
              color="#d2a8ff"
            />
            <StatCard
              label="Last Collisions"
              value={last?.collisions ?? '—'}
              sub={`last alive: ${last?.aliveAtEnd ?? '—'}`}
              color="#d29922"
            />
          </div>

          {/* Reward chart */}
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider mb-4">Total Reward per Episode</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={rewardData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="episode" stroke="#8b949e" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                <YAxis stroke="#8b949e" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend wrapperStyle={{ fontSize: 11, fontFamily: 'monospace' }} />
                <Line type="monotone" dataKey="value" name="reward" stroke="#58a6ff" dot={false} strokeWidth={1} opacity={0.4} />
                <Line type="monotone" dataKey="ma" name="MA-5" stroke="#58a6ff" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Goals + Collisions side by side */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
              <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider mb-4">Goals Reached</h3>
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={goalsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis dataKey="episode" stroke="#8b949e" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
                  <YAxis stroke="#8b949e" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  <Line type="monotone" dataKey="value" name="goals" stroke="#3fb950" dot={false} strokeWidth={1} opacity={0.4} />
                  <Line type="monotone" dataKey="ma" name="MA-5" stroke="#3fb950" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
              <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider mb-4">Collisions</h3>
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={collisionsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis dataKey="episode" stroke="#8b949e" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
                  <YAxis stroke="#8b949e" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  <Line type="monotone" dataKey="value" name="collisions" stroke="#d29922" dot={false} strokeWidth={1} opacity={0.4} />
                  <Line type="monotone" dataKey="ma" name="MA-5" stroke="#d29922" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Alive at end */}
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <h3 className="text-xs font-mono text-[#8b949e] uppercase tracking-wider mb-4">Robots Alive at Episode End</h3>
            <ResponsiveContainer width="100%" height={140}>
              <LineChart data={aliveData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="episode" stroke="#8b949e" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                <YAxis stroke="#8b949e" tick={{ fontSize: 11, fontFamily: 'monospace' }} domain={[0, 12]} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Line type="monotone" dataKey="value" name="alive" stroke="#d2a8ff" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
