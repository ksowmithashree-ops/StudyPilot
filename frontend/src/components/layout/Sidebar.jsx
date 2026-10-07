import {
  LayoutDashboard,
  BookOpen,
  CalendarDays,
  CheckSquare,
  BarChart3,
  Bot,
} from "lucide-react";

const navigation = [
  {
    to: "/app",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    to: "/app/subjects",
    label: "Subjects",
    icon: BookOpen,
  },
  {
    to: "/app/deadlines",
    label: "Deadlines",
    icon: CalendarDays,
  },
  {
    to: "/app/tasks",
    label: "Tasks",
    icon: CheckSquare,
  },
  {
    to: "/app/progress",
    label: "Progress",
    icon: BarChart3,
  },
  {
    to: "/app/assistant",
    label: "AI Assistant",
    icon: Bot,
  },
];

export default navigation;