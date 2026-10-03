import { EmptyState } from "../ui/EmptyState.jsx";
import { TaskRow } from "./TaskRow.jsx";

export function TodayPlan({ sessions, onComplete, onMiss, busy, onGenerate }) {
  if (!sessions?.length) {
    return (
      <EmptyState
        title="No sessions yet today"
        body="Generate an AI plan to fill today with high-priority topics like Normalization."
        action={
          onGenerate ? (
            <button
              onClick={onGenerate}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Generate AI Plan
            </button>
          ) : null
        }
      />
    );
  }
  return (
    <div className="space-y-3">
      {sessions.map((session) => (
        <TaskRow key={session.id} session={session} onComplete={onComplete} onMiss={onMiss} busy={busy} />
      ))}
    </div>
  );
}
