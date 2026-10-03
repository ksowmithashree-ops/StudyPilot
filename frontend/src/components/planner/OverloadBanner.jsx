import { AlertTriangle } from "lucide-react";

export function OverloadBanner({ show }) {
  if (!show) return null;
  return (
    <div className="mb-4 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
      Planned study time exceeded your available hours. StudyPilot capped the day and deferred lower-priority work.
    </div>
  );
}
