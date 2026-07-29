import { Activity, Gauge, ServerCog, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { api, UsageSummary } from "../lib/api";

function Stat({ label, value, icon: Icon }: { label: string; value: string | number; icon: typeof Activity }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm text-slate-500">{label}</span>
        <Icon className="h-4 w-4 text-signal" />
      </div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}

export function MetricsPage({ token }: { token: string }) {
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  useEffect(() => {
    void api.usage(token).then(setUsage);
  }, [token]);
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Stat label="Prompt tokens" value={usage?.prompt_tokens ?? 0} icon={Activity} />
      <Stat label="Completion tokens" value={usage?.completion_tokens ?? 0} icon={Gauge} />
      <Stat label="AI requests" value={usage?.requests ?? 0} icon={ServerCog} />
      <Stat label="Cache hits" value={usage?.cache_hits ?? 0} icon={Users} />
      <div className="rounded-lg border border-line bg-white p-4 md:col-span-2 xl:col-span-4">
        <div className="text-sm font-semibold">Grafana</div>
        <p className="mt-2 text-sm text-slate-500">Production metrics are exported at /metrics and provisioned into the Athena Grafana dashboard.</p>
      </div>
    </div>
  );
}

export function AdminPage({ token }: { token: string }) {
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    void api.adminUsage(token).then(setUsage).catch((err) => setError(err.message));
  }, [token]);
  if (error) {
    return <div className="rounded-lg border border-line bg-white p-4 text-sm text-risk">{error}</div>;
  }
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Stat label="Active users" value={usage?.active_users ?? 0} icon={Users} />
      <Stat label="Indexed documents" value={usage?.documents_indexed ?? 0} icon={ServerCog} />
      <Stat label="Indexed chunks" value={usage?.chunks_indexed ?? 0} icon={Activity} />
    </div>
  );
}

