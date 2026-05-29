import React from "react"
import { createBrowserRouter } from "react-router"
import { Layout } from "./components/Layout"
import { Dashboard } from "./pages/Dashboard"
import { ExperimentDetail } from "./pages/ExperimentDetail"
import { Comparison } from "./pages/Comparison"
import { SwarmConfig } from "./pages/SwarmConfig"
import { TrainingDashboard } from "./pages/TrainingDashboard"

// Dummy placeholders for other routes
function Placeholder({ title }: { title: string }) {
  return (
    <div className="flex-1 flex items-center justify-center bg-[#0d1117] text-[#8b949e]">
      <h2 className="text-xl font-mono">{title}</h2>
    </div>
  )
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "experiments", Component: () => <Placeholder title="Experiments List" /> },
      { path: "experiment/:id", Component: ExperimentDetail },
      { path: "runs", Component: () => <Placeholder title="Runs History" /> },
      { path: "configs", Component: SwarmConfig },
      { path: "comparisons", Component: Comparison },
      { path: "training", Component: TrainingDashboard },
      { path: "settings", Component: () => <Placeholder title="Settings" /> },
    ],
  },
])
