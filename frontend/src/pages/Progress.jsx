import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { Card } from "../components/ui/Card.jsx";
import { Loader } from "../components/ui/Loader.jsx";
import { HoursChart } from "../components/charts/HoursChart.jsx";
import { SubjectChart } from "../components/charts/SubjectChart.jsx";
import { TasksChart } from "../components/charts/TasksChart.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function ProgressPage() {
  const [data, setData] = useState(null);
  const [readiness, setReadiness] = useState([]);
  const { pushToast } = useToasts();

  useEffect(() => {
    Promise.all([api.get("/progress"), api.get("/readiness")])
      .then(([p, r]) => {
        setData(p);
        setReadiness(r);
      })
      .catch((err) => pushToast(err.message, "error"));
  }, []);

  if (!data) return <Loader label="Loading progress..." />;

  return (
    <div className="fade-in">
      <Topbar title="Progress" subtitle="Study hours, subject mastery and completed tasks." />
      <div className="grid gap-4 lg:grid-cols-3">
        {readiness.map((exam) => (
          <Card key={exam.deadline_id}>
            <p className="text-xs uppercase tracking-wide text-slate-400">{exam.title}</p>
            <p className="mt-1 text-3xl font-extrabold text-indigo-700">{exam.readiness}%</p>
            <p className="text-sm text-slate-500">{exam.days_left} days left</p>
          </Card>
        ))}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-2 font-semibold">Study hours</h2>
          <HoursChart data={data.hours} />
        </Card>
        <Card>
          <h2 className="mb-2 font-semibold">Completed tasks</h2>
          <TasksChart data={data.tasks} />
        </Card>
        <Card className="lg:col-span-2">
          <h2 className="mb-2 font-semibold">Subject progress</h2>
          <SubjectChart data={data.subjects} />
        </Card>
      </div>
    </div>
  );
}
