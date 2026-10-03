import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { Card } from "../components/ui/Card.jsx";
import { MonthGrid } from "../components/calendar/MonthGrid.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [sessions, setSessions] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [selected, setSelected] = useState(null);
  const { pushToast } = useToasts();

  async function load() {
    const from = new Date(year, month, 1);
    const to = new Date(year, month + 1, 0);
    const fmt = (d) =>
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    try {
      const [s, d] = await Promise.all([
        api.get(`/sessions?from=${fmt(from)}&to=${fmt(to)}`),
        api.get("/deadlines"),
      ]);
      setSessions(s);
      setDeadlines(d);
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  useEffect(() => {
    load();
  }, [year, month]);

  return (
    <div className="fade-in">
      <Topbar title="Calendar" subtitle="Exams, deadlines and study sessions." />
      <div className="mb-4 flex items-center justify-between">
        <button
          className="text-sm text-indigo-600"
          onClick={() => {
            const d = new Date(year, month - 1, 1);
            setYear(d.getFullYear());
            setMonth(d.getMonth());
          }}
        >
          Previous
        </button>
        <p className="font-semibold">
          {now.toLocaleString(undefined, { month: "long" }) &&
            new Date(year, month, 1).toLocaleString(undefined, { month: "long", year: "numeric" })}
        </p>
        <button
          className="text-sm text-indigo-600"
          onClick={() => {
            const d = new Date(year, month + 1, 1);
            setYear(d.getFullYear());
            setMonth(d.getMonth());
          }}
        >
          Next
        </button>
      </div>
      <Card>
        <MonthGrid
          year={year}
          month={month}
          sessions={sessions}
          deadlines={deadlines}
          onSelect={(date, daySessions, dayDeadlines) => setSelected({ date, daySessions, dayDeadlines })}
        />
      </Card>
      {selected ? (
        <Card className="mt-4">
          <h2 className="font-semibold">{selected.date}</h2>
          <div className="mt-2 space-y-2 text-sm">
            {selected.dayDeadlines.map((d) => (
              <p key={d.id} className="text-rose-700">
                {d.type}: {d.title}
              </p>
            ))}
            {selected.daySessions.map((s) => (
              <p key={s.id}>
                {s.start_time} {s.topic_name} ({s.status})
              </p>
            ))}
            {!selected.dayDeadlines.length && !selected.daySessions.length ? (
              <p className="text-slate-400">Nothing scheduled.</p>
            ) : null}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
