import { useApp } from "../context/AppContext.jsx";

export function useToasts() {
  return useApp();
}
