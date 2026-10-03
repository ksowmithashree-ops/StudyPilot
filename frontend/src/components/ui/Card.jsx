export function Card({ children, className = "" }) {
  return (
    <div className={`rounded-2xl border border-white/80 bg-white/90 p-5 shadow-card backdrop-blur ${className}`}>
      {children}
    </div>
  );
}
