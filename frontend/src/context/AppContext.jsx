import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ToastContext = createContext(null);

export function AppProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const pushToast = useCallback((message, type = "info") => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { id, message, type }]);
    setTimeout(() => {
      setToasts((current) => current.filter((t) => t.id !== id));
    }, 4200);
  }, []);

  const value = useMemo(() => ({ toasts, pushToast }), [toasts, pushToast]);
  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
}

export function useApp() {
  return useContext(ToastContext);
}
