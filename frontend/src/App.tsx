import { useEffect, useState } from "react";
import { Shell } from "./components/Shell";
import { api, User } from "./lib/api";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage, MetricsPage } from "./pages/Dashboards";
import { DocumentsPage } from "./pages/DocumentsPage";
import { LoginPage } from "./pages/LoginPage";
import { OperationsPage } from "./pages/OperationsPage";

type View = "chat" | "documents" | "operations" | "admin" | "metrics";

export function App() {
  const [token, setToken] = useState(() => localStorage.getItem("athena_token") ?? "");
  const [user, setUser] = useState<User | null>(null);
  const [view, setView] = useState<View>("chat");

  useEffect(() => {
    if (!token) return;
    localStorage.setItem("athena_token", token);
    void api.me(token).then(setUser).catch(() => {
      localStorage.removeItem("athena_token");
      setToken("");
    });
  }, [token]);

  if (!token || !user) {
    return <LoginPage onToken={setToken} />;
  }

  return (
    <Shell
      user={user}
      view={view}
      setView={setView}
      onLogout={() => {
        localStorage.removeItem("athena_token");
        setToken("");
        setUser(null);
      }}
    >
      {view === "chat" && <ChatPage token={token} />}
      {view === "operations" && <OperationsPage token={token} onAskAi={() => setView("chat")} />}
      {view === "documents" && <DocumentsPage token={token} />}
      {view === "metrics" && <MetricsPage token={token} />}
      {view === "admin" && <AdminPage token={token} />}
    </Shell>
  );
}
