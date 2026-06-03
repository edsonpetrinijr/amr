import { createHashRouter } from "react-router"
import { Layout } from "./components/Layout"
import { Dashboard } from "./pages/Dashboard"
import { Field } from "./pages/Field"
import { Devices } from "./pages/Devices"
import { Calibration } from "./pages/Calibration"
import { Tasks } from "./pages/Tasks"
import { Callbuttons } from "./pages/Callbuttons"
import { SettingsPage } from "./pages/Settings"

// Hash history (not browser history): the packaged Electron app is served from a
// `file://` URL whose pathname is the on-disk index.html path, which matches no
// route and leaves the window BLANK. Hash routing ('#/...') is independent of the
// file path, so it resolves correctly offline in production *and* in the browser.
export const router = createHashRouter([
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

