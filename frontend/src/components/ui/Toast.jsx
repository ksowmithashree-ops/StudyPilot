import { useApp } from "../../context/AppContext.jsx";

export function ToastViewport() {
  const { toasts } = useApp();
  return (
    <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-[min(92vw,360px)] flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto rounded-xl px-4 py-3 text-sm font-medium text-white shadow-lg fade-in ${
            toast.type === "error" ? "bg-rose-600" : toast.type === "success" ? "bg-emerald-600" : "bg-indigo-600"
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
