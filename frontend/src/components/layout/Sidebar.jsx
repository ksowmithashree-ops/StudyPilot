import {
  LayoutDashboard,
  BookOpen,
  CalendarDays,
  CheckSquare,
  BarChart3,
  Bot,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/subjects", label: "Subjects", icon: BookOpen },
  { to: "/app/deadlines", label: "Deadlines", icon: CalendarDays },
  { to: "/app/tasks", label: "Tasks", icon: CheckSquare },
  { to: "/app/progress", label: "Progress", icon: BarChart3 },
  { to: "/app/assistant", label: "AI Assistant", icon: Bot },
];

export function Sidebar() {
  return (
    <aside className="hidden md:block w-64 border-r min-h-screen p-4">
      <nav className="space-y-2">
        {navigation.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-100"
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export function MobileNav() {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 border-t bg-white p-2 flex justify-around">
      {navigation.slice(0, 4).map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          className="flex flex-col items-center text-xs"
        >
          <Icon size={18} />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}