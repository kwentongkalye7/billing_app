import { Outlet, NavLink } from "react-router-dom";
import { useAuthStore } from "../hooks/useAuth";
import { cn } from "../utils/cn";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/clients", label: "Clients" },
  { to: "/engagements", label: "Engagements" },
  { to: "/statements", label: "Statements" },
  { to: "/payments", label: "Payments" },
  { to: "/reports", label: "Reports" },
];

export const DashboardLayout = () => {
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold">Unified Billing App</h1>
            <p className="text-sm text-slate-500">Manual-first statements, payments, and audit trails.</p>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="text-right">
              <div className="font-medium">{user?.display_name}</div>
              <div className="text-slate-500">Role: {user?.role}</div>
            </div>
            <button
              onClick={() => logout()}
              className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-6xl gap-6 px-6 py-6">
        <nav className="w-56 flex-shrink-0 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "block rounded-lg px-4 py-2 text-sm font-medium transition",
                  isActive ? "bg-primary text-white" : "bg-white text-slate-700 hover:bg-slate-200"
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 space-y-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
