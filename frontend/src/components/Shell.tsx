import {
  Activity,
  BarChart3,
  Database,
  FileText,
  LogOut,
  MessageSquare,
  Shield
} from "lucide-react";
import type { ReactNode } from "react";
import type { User } from "../lib/api";

type View = "chat" | "documents" | "operations" | "admin" | "metrics";

const nav = [
  { id: "chat" as const, label: "Chat", icon: MessageSquare },
  { id: "operations" as const, label: "Trading Ops", icon: Activity },
  { id: "documents" as const, label: "Docs", icon: FileText },
  { id: "metrics" as const, label: "Metrics", icon: BarChart3 },
  { id: "admin" as const, label: "Admin", icon: Shield }
];

export function Shell({
  user,
  view,
  setView,
  onLogout,
  children
}: {
  user: User;
  view: View;
  setView: (view: View) => void;
  onLogout: () => void;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#f5f7f8] text-ink">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-white md:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <Database className="h-6 w-6 text-signal" />
          <div>
            <div className="text-sm font-semibold tracking-wide">ATHENA</div>
            <div className="text-xs text-slate-500">AI Engineering Copilot</div>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setView(item.id)}
                className={`flex h-10 w-full items-center gap-3 rounded-md px-3 text-sm font-medium ${
                  view === item.id
                    ? "bg-signal text-white"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="md:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-white px-4 md:px-8">
          <div>
            <div className="text-sm font-semibold">{user.full_name}</div>
            <div className="text-xs text-slate-500">
              {user.role} - {user.email}
            </div>
          </div>
          <button
            className="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm hover:bg-slate-50"
            onClick={onLogout}
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </header>
        <div className="px-4 py-5 md:px-8">{children}</div>
      </main>
    </div>
  );
}
