import { NavLink } from "react-router-dom";
import { Bot, CalendarDays, Gauge, LayoutDashboard, LineChart, Settings, Sparkles, BookOpen } from "lucide-react";

const links = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/subjects", label: "My Subjects", icon: BookOpen },
  { to: "/app/planner", label: "Study Planner", icon: Sparkles },
  { to: "/app/calendar", label: "Calendar", icon: CalendarDays },
  { to: "/app/progress", label: "Progress", icon: LineChart },
  { to: "/app/assistant", label: "AI Assistant", icon: Bot },
  { to: "/app/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-indigo-100 bg-white/80 p-4 lg:block">
      <div className="mb-8 flex items-center gap-2 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white">
          <Gauge className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-bold text-slate-900">StudyPilot</p>
          <p className="text-xs text-slate-400">Adaptive planner</p>
        </div>
      </div>
      <nav className="space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-50"
              }`
            }
          >
            <link.icon className="h-4 w-4" />
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export function MobileNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 flex gap-1 overflow-x-auto border-t border-slate-200 bg-white/95 p-2 lg:hidden">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) =>
            `flex min-w-[4.5rem] flex-col items-center rounded-xl py-2 text-[11px] font-medium ${
              isActive ? "text-indigo-600" : "text-slate-500"
            }`
          }
        >
          <link.icon className="mb-1 h-4 w-4" />
          {link.label.split(" ")[0]}
        </NavLink>
      ))}
    </nav>
  );
}
