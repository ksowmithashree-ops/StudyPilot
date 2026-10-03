import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { Card } from "../components/ui/Card.jsx";
import { EmptyState } from "../components/ui/EmptyState.jsx";
import { Loader } from "../components/ui/Loader.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { TaskRow } from "../components/planner/TaskRow.jsx";
import { OverloadBanner } from "../components/planner/OverloadBanner.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function Planner() {
  const [sessions, setSessions] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const { pushToast } = useToasts();

  async function load() {
    setLoading(true);
    try {
      const from = new Date();
      const to = new Date();
      to.setDate(to.getDate() + 7);
      const [s, d] = await Promise.all([
        api.get(`/sessions?from=${from.toISOString().slice(0, 10)}&to=${to.toISOString().slice(0, 10)}`),
        api.get("/dashboard"),
      ]);
      setSessions(s);
      setDashboard(d);
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const byDate = useMemo(() => {
    const groups = {};
    sessions.forEach((s) => {
      groups[s.date] = groups[s.date] || [];
      groups[s.date].push(s);
    });
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [sessions]);

  async function generate() {
    setBusy(true);
    try {
      const result = await api.post("/planner/generate", { days: 7 });
      pushToast(`Generated ${result.sessions.length} sessions. Top: ${result.top_priorities?.[0]?.topic}`, "success");
      await load();
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function optimize() {
    setBusy(true);
    try {
      await api.post("/planner/optimize", {});
      pushToast("Schedule optimized to fit available hours", "success");
      await load();
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function complete(session) {
    setBusy(true);
    try {
      await api.post(`/sessions/${session.id}/complete`, {});
      pushToast(`Completed ${session.topic_name}`, "success");
      await load();
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function miss(session) {
    setBusy(true);
    try {
      const result = await api.post(`/sessions/${session.id}/miss`, {});
      const moved = result.rescheduled;
      pushToast(
        moved ? `Rescheduled to ${moved.date} ${moved.start_time}` : "Marked missed",
        "success"
      );
      await load();
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fade-in">
      <Topbar title="Study Planner" subtitle="Generate a 7-day plan that never exceeds your available time." />
      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={generate} disabled={busy}>
          Generate AI Plan
        </Button>
        <Button variant="secondary" onClick={optimize} disabled={busy}>
          Optimize overload
        </Button>
      </div>
      <OverloadBanner show={dashboard?.overload} />
      {loading ? (
        <Loader label="Loading plan..." />
      ) : byDate.length === 0 ? (
        <EmptyState
          title="No planned sessions"
          body="Click Generate AI Plan. Normalization should land first because of low progress and the DBMS exam."
          action={
            <Button onClick={generate} disabled={busy}>
              Generate AI Plan
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          {byDate.map(([day, items]) => (
            <Card key={day}>
              <h2 className="mb-3 font-semibold">{day}</h2>
              <div className="space-y-3">
                {items.map((session) => (
                  <TaskRow
                    key={session.id}
                    session={session}
                    onComplete={complete}
                    onMiss={miss}
                    busy={busy}
                  />
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
