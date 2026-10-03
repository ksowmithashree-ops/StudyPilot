import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import { Card } from "../components/ui/Card.jsx";
import { Loader, Skeleton } from "../components/ui/Loader.jsx";
import { ProgressBar } from "../components/ui/ProgressBar.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { TodayPlan } from "../components/planner/TodayPlan.jsx";
import { OverloadBanner } from "../components/planner/OverloadBanner.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const { pushToast } = useToasts();
  const navigate = useNavigate();

  async function load() {
    setLoading(true);
    try {
      setData(await api.get("/dashboard"));
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function generate() {
    setBusy(true);
    try {
      const result = await api.post("/planner/generate", { days: 7 });
      const top = result.top_priorities?.[0];
      pushToast(`Plan ready. Priority: ${top?.topic || "today’s work"}`, "success");
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
        moved
          ? `${session.topic_name} rescheduled to ${moved.date} at ${moved.start_time}`
          : `${session.topic_name} marked missed`,
        "success"
      );
      await load();
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading && !data) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-16" />
        <Skeleton className="h-40" />
        <Loader />
      </div>
    );
  }

  const stats = data?.stats || {};
  const readiness = data?.readiness?.[0];

  return (
    <div className="fade-in">
      <Topbar
        title={`Hi, ${data?.user?.name || "student"}`}
        subtitle="Today’s plan, deadlines, and exam readiness in one place."
      />
      <OverloadBanner show={data?.overload} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Study hours", `${((stats.planned_minutes || 0) / 60).toFixed(1)}h planned`],
          ["Completed", `${stats.completed_tasks || 0} tasks`],
          ["Pending", `${stats.pending_tasks || 0} tasks`],
          ["Available", `${((stats.available_minutes || 0) / 60).toFixed(1)}h today`],
        ].map(([label, value]) => (
          <Card key={label}>
            <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
            <p className="mt-1 text-xl font-bold">{value}</p>
          </Card>
        ))}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">Today’s plan</h2>
            <button onClick={generate} disabled={busy} className="text-sm font-semibold text-indigo-600">
              {busy ? "Working…" : "Generate AI Plan"}
            </button>
          </div>
          <TodayPlan
            sessions={data?.today_plan}
            onComplete={complete}
            onMiss={miss}
            busy={busy}
            onGenerate={generate}
          />
        </Card>
        <div className="space-y-4">
          <Card>
            <h2 className="font-semibold">Exam readiness</h2>
            {readiness ? (
              <div className="mt-3">
                <p className="text-3xl font-extrabold text-indigo-700">{readiness.readiness}%</p>
                <p className="text-sm text-slate-500">
                  {readiness.title} · {readiness.days_left} days left
                </p>
                <div className="mt-3">
                  <ProgressBar value={readiness.readiness} />
                </div>
              </div>
            ) : (
              <p className="mt-2 text-sm text-slate-500">Add an exam deadline to see readiness.</p>
            )}
          </Card>
          <Card>
            <h2 className="font-semibold">Upcoming deadlines</h2>
            <div className="mt-3 space-y-2">
              {(data?.deadlines || []).map((d) => (
                <div key={d.id} className="flex items-center justify-between text-sm">
                  <span>{d.title}</span>
                  <span className="text-slate-400">{d.due_date}</span>
                </div>
              ))}
            </div>
          </Card>
          <Card>
            <h2 className="font-semibold">Priority topics</h2>
            <div className="mt-3 space-y-2">
              {(data?.top_priorities || []).map((item) => (
                <div key={item.topic}>
                  <div className="flex justify-between text-sm">
                    <span>{item.topic}</span>
                    <span className="text-slate-400">{item.progress_pct}%</span>
                  </div>
                  <ProgressBar value={item.progress_pct} />
                </div>
              ))}
            </div>
            <button onClick={() => navigate("/app/planner")} className="mt-3 text-sm font-semibold text-indigo-600">
              Open planner
            </button>
          </Card>
        </div>
      </div>
    </div>
  );
}
