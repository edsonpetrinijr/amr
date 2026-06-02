import { createBrowserRouter } from "react-router"
import { Layout } from "./components/Layout"
import { Dashboard } from "./pages/Dashboard"
import { Field } from "./pages/Field"
import { Devices } from "./pages/Devices"
import { Calibration } from "./pages/Calibration"
import { Tasks } from "./pages/Tasks"
import { Callbuttons } from "./pages/Callbuttons"
import { SettingsPage } from "./pages/Settings"

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "field", Component: Field },
      { path: "devices", Component: Devices },
      { path: "calibration", Component: Calibration },
      { path: "calibration/:robotId", Component: Calibration },
      { path: "tasks", Component: Tasks },
      { path: "callbuttons", Component: Callbuttons },
      { path: "settings", Component: SettingsPage },
    ],
  },
])

