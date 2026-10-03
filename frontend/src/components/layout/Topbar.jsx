import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { api } from "../../api/client.js";

export function Topbar({ title, subtitle }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState([]);

  async function load() {
    try {
      const data = await api.get("/notifications");
      setNotes(data.items || []);
    } catch {
      setNotes([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const unread = notes.filter((n) => !n.read).length;

  async function markAll() {
    await api.patch("/notifications", {});
    load();
  }

  return (
    <header className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      <div className="relative">
        <button
          onClick={() => {
            setOpen((v) => !v);
            load();
          }}
          className="relative rounded-xl border border-slate-200 bg-white p-2.5 text-slate-600"
        >
          <Bell className="h-5 w-5" />
          {unread ? (
            <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] text-white">
              {unread}
            </span>
          ) : null}
        </button>
        {open ? (
          <div className="absolute right-0 z-20 mt-2 w-80 rounded-2xl border border-slate-100 bg-white p-3 shadow-xl">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-semibold">Notifications</p>
              <button onClick={markAll} className="text-xs text-indigo-600">
                Mark read
              </button>
            </div>
            <div className="max-h-72 space-y-2 overflow-y-auto">
              {notes.length === 0 ? <p className="text-sm text-slate-400">No notifications yet.</p> : null}
              {notes.map((note) => (
                <div key={note.id} className="rounded-xl bg-slate-50 p-2">
                  <p className="text-sm font-medium">{note.title}</p>
                  <p className="text-xs text-slate-500">{note.body}</p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}
