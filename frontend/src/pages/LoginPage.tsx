import { Lock, LogIn } from "lucide-react";
import { FormEvent, useState } from "react";
import { api } from "../lib/api";

export function LoginPage({ onToken }: { onToken: (token: string) => void }) {
  const [email, setEmail] = useState("researcher@athena.local");
  const [password, setPassword] = useState("AthenaResearch123!");
  const [fullName, setFullName] = useState("Research User");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      if (mode === "register") {
        await api.register(email, password, fullName);
      }
      const token = await api.login(email, password);
      onToken(token.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-[#eef3f3] px-4">
      <form onSubmit={submit} className="w-full max-w-sm rounded-lg border border-line bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-md bg-signal text-white">
            <Lock className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Athena Copilot</h1>
            <p className="text-sm text-slate-500">Quant engineering workspace</p>
          </div>
        </div>
        <div className="mb-4 grid grid-cols-2 rounded-md border border-line p-1 text-sm">
          <button type="button" onClick={() => setMode("login")} className={`h-8 rounded ${mode === "login" ? "bg-signal text-white" : ""}`}>
            Login
          </button>
          <button type="button" onClick={() => setMode("register")} className={`h-8 rounded ${mode === "register" ? "bg-signal text-white" : ""}`}>
            Register
          </button>
        </div>
        {mode === "register" && (
          <label className="mb-3 block text-sm">
            Full name
            <input className="mt-1 h-10 w-full rounded-md border border-line px-3" value={fullName} onChange={(event) => setFullName(event.target.value)} />
          </label>
        )}
        <label className="mb-3 block text-sm">
          Email
          <input className="mt-1 h-10 w-full rounded-md border border-line px-3" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="mb-4 block text-sm">
          Password
          <input className="mt-1 h-10 w-full rounded-md border border-line px-3" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <div className="mb-3 rounded-md bg-red-50 px-3 py-2 text-sm text-risk">{error}</div>}
        <button className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink text-sm font-semibold text-white hover:bg-steel">
          <LogIn className="h-4 w-4" />
          Continue
        </button>
      </form>
    </div>
  );
}

