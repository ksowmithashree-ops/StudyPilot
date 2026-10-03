import { Badge } from "../ui/Badge.jsx";
import { Button } from "../ui/Button.jsx";

export function TaskRow({ session, onComplete, onMiss, busy }) {
  const tone = session.status === "completed" ? "emerald" : session.status === "missed" ? "rose" : "indigo";
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-100 bg-slate-50/70 p-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: session.subject_color }} />
          <p className="font-semibold text-slate-800">{session.topic_name}</p>
          <Badge tone={tone}>{session.status}</Badge>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          {session.subject_name} · {session.start_time}–{session.end_time} · {session.planned_minutes} min
        </p>
        {session.notes ? <p className="mt-1 text-xs text-slate-400">{session.notes}</p> : null}
      </div>
      {session.status === "planned" ? (
        <div className="flex gap-2">
          <Button disabled={busy} onClick={() => onComplete(session)} className="px-3 py-2">
            Complete
          </Button>
          <Button disabled={busy} variant="secondary" onClick={() => onMiss(session)} className="px-3 py-2">
            Missed
          </Button>
        </div>
      ) : null}
    </div>
  );
}
