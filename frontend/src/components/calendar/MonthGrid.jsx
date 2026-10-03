const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function ymd(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function MonthGrid({ year, month, sessions = [], deadlines = [], onSelect }) {
  const first = new Date(year, month, 1);
  const start = first.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < start; i += 1) cells.push(null);
  for (let d = 1; d <= daysInMonth; d += 1) cells.push(new Date(year, month, d));

  const sessionMap = {};
  sessions.forEach((s) => {
    sessionMap[s.date] = sessionMap[s.date] || [];
    sessionMap[s.date].push(s);
  });
  const deadlineMap = {};
  deadlines.forEach((d) => {
    deadlineMap[d.due_date] = deadlineMap[d.due_date] || [];
    deadlineMap[d.due_date].push(d);
  });

  return (
    <div>
      <div className="mb-2 grid grid-cols-7 text-center text-xs font-semibold uppercase tracking-wide text-slate-400">
        {WEEKDAYS.map((d) => (
          <div key={d}>{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-2">
        {cells.map((day, idx) => {
          if (!day) return <div key={`e-${idx}`} />;
          const key = ymd(day);
          const daySessions = sessionMap[key] || [];
          const dayDeadlines = deadlineMap[key] || [];
          return (
            <button
              key={key}
              onClick={() => onSelect?.(key, daySessions, dayDeadlines)}
              className="min-h-[88px] rounded-xl border border-slate-100 bg-white p-2 text-left hover:border-indigo-200"
            >
              <div className="text-sm font-semibold text-slate-700">{day.getDate()}</div>
              <div className="mt-1 space-y-1">
                {dayDeadlines.slice(0, 1).map((d) => (
                  <div key={d.id} className="truncate rounded bg-rose-50 px-1 text-[10px] font-medium text-rose-700">
                    {d.title}
                  </div>
                ))}
                {daySessions.slice(0, 2).map((s) => (
                  <div key={s.id} className="truncate rounded bg-indigo-50 px-1 text-[10px] text-indigo-700">
                    {s.topic_name}
                  </div>
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
