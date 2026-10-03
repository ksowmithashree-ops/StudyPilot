import { Route, Routes } from "react-router-dom";
import { ToastViewport } from "./components/ui/Toast.jsx";
import { PageShell } from "./components/layout/PageShell.jsx";
import Landing from "./pages/Landing.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Subjects from "./pages/Subjects.jsx";
import Planner from "./pages/Planner.jsx";
import CalendarPage from "./pages/Calendar.jsx";
import ProgressPage from "./pages/Progress.jsx";
import Assistant from "./pages/Assistant.jsx";
import Settings from "./pages/Settings.jsx";

export default function App() {
  return (
    <>
      <ToastViewport />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<PageShell />}>
          <Route index element={<Dashboard />} />
          <Route path="subjects" element={<Subjects />} />
          <Route path="planner" element={<Planner />} />
          <Route path="calendar" element={<CalendarPage />} />
          <Route path="progress" element={<ProgressPage />} />
          <Route path="assistant" element={<Assistant />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </>
  );
}
