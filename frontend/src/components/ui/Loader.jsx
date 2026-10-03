export function Loader({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center gap-3 py-12 text-sm text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
      {label}
    </div>
  );
}

export function Skeleton({ className = "h-24" }) {
  return <div className={`animate-pulse rounded-2xl bg-slate-200/80 ${className}`} />;
}
