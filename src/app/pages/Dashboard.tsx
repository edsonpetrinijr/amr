import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import { Button } from "../components/ui/button"
import { GitCommit, Play, GitBranch, Terminal, ExternalLink, GitMerge, RotateCcw, Combine, Circle, CheckCircle2, XCircle, Clock } from "lucide-react"
import { Link } from "react-router"
import { cn } from "@/app/utils"

const recentExperiments = [
  {
    id: "exp-8921",
    name: "Swarm-Evade-v4",
    repo: "robotics-lab/swarm-nav",
    status: "success",
    time: "2h ago",
  },
  {
    id: "exp-8920",
    name: "Target-Search-Heuristic",
    repo: "aeronet/behaviors",
    status: "failed",
    time: "5h ago",
  },
  {
    id: "exp-8919",
    name: "Formation-Alpha",
    repo: "robotics-lab/swarm-nav",
    status: "success",
    time: "1d ago",
  },
]

const activeRuns = [
  {
    id: "run-449",
    expId: "exp-8922",
    name: "Obstacle-Dense-Test",
    agents: 24,
    progress: 78,
    status: "running",
  },
  {
    id: "run-448",
    expId: "exp-8922",
    name: "Baseline-Comparison",
    agents: 12,
    progress: 100,
    status: "completed",
  }
]

export function Dashboard() {
  return (
    <div className="flex-1 overflow-auto bg-[#0d1117] p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#e6edf3]">Dashboard</h1>
          <p className="text-[#8b949e] text-sm mt-1">Overview of multi-agent execution environment.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/comparisons">
            <Button variant="outline" className="flex items-center gap-2">
              <Combine className="w-4 h-4" />
              Compare Runs
            </Button>
          </Link>
          <Link to="/experiment/new">
            <Button variant="primary" className="flex items-center gap-2">
              <Play className="w-4 h-4" />
              Run Swarm Simulation
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Terminal className="w-4 h-4 text-[#8b949e]" />
                Recent Experiments
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-[#30363d]">
                {recentExperiments.map((exp) => (
                  <div key={exp.id} className="p-4 hover:bg-[#21262d]/50 transition-colors flex items-center justify-between">
                    <div className="flex items-start gap-4">
                      <div className="mt-1">
                        {exp.status === 'success' ? (
                          <CheckCircle2 className="w-4 h-4 text-[#3fb950]" />
                        ) : (
                          <XCircle className="w-4 h-4 text-[#f85149]" />
                        )}
                      </div>
                      <div>
                        <Link to={`/experiment/${exp.id}`} className="text-[#58a6ff] hover:underline font-medium text-sm">
                          {exp.name}
                        </Link>
                        <div className="flex items-center gap-3 mt-1.5 text-xs text-[#8b949e] font-mono">
                          <span className="flex items-center gap-1">
                            <GitBranch className="w-3 h-3" />
                            {exp.repo}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {exp.time}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" title="Run again">
                        <RotateCcw className="w-4 h-4 text-[#8b949e]" />
                      </Button>
                      <Link to={`/experiment/${exp.id}`}>
                        <Button variant="outline" size="sm" className="text-xs font-mono">
                          View Log
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#8b949e]" />
                Active Runs
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              {activeRuns.map(run => (
                <div key={run.id} className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="font-mono text-[#c9d1d9] truncate pr-2">{run.name}</span>
                    <Badge variant={run.status === 'running' ? 'default' : 'success'} className="shrink-0 text-[10px] py-0 px-2 uppercase tracking-wider">
                      {run.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#8b949e] mb-1">
                    <Circle className="w-3 h-3 fill-current" />
                    {run.agents} agents
                  </div>
                  <div className="w-full bg-[#30363d] rounded-full h-1.5 overflow-hidden">
                    <div 
                      className={cn("h-full rounded-full transition-all duration-500", 
                        run.status === 'running' ? "bg-[#58a6ff]" : "bg-[#3fb950]"
                      )}
                      style={{ width: `${run.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
             <CardHeader className="py-3">
              <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-2">
              <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                <GitBranch className="w-3 h-3 mr-2" />
                New Experiment (GitHub Repo)
              </Button>
              <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                <GitMerge className="w-3 h-3 mr-2" />
                Link External Policy File
              </Button>
              <Button variant="outline" className="w-full justify-start text-xs font-mono h-8">
                <ExternalLink className="w-3 h-3 mr-2" />
                Open Metric Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function Activity(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}
