import { Outlet } from "react-router-dom";
import { MobileNav, Sidebar } from "./Sidebar.jsx";

export function PageShell() {
  return (
    <div className="flex min-h-screen bg-[radial-gradient(circle_at_top_left,_#e0e7ff,_transparent_28%),radial-gradient(circle_at_top_right,_#ede9fe,_transparent_24%),#f8fafc]">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 pb-24 lg:px-8 lg:pb-10">
          <Outlet />
        </main>
      </div>
      <MobileNav />
    </div>
  );
}
