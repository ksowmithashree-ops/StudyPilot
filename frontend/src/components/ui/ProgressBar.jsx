export function ProgressBar({ value }) {
  const pct = Math.max(0, Math.min(100, value || 0));
  return (
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
