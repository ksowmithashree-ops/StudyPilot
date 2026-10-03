export function Button({ children, variant = "primary", className = "", ...props }) {
  const styles = {
    primary:
      "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-card hover:from-indigo-500 hover:to-violet-500",
    secondary: "bg-white text-slate-700 border border-slate-200 hover:bg-slate-50",
    ghost: "text-slate-600 hover:bg-slate-100",
    danger: "bg-rose-600 text-white hover:bg-rose-500",
  };
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50 ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
