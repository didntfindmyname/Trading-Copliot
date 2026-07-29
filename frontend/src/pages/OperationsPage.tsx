import { AlertTriangle, Bot, CheckCircle2, Play, RefreshCw, ServerCog } from "lucide-react";
import { useEffect, useState } from "react";
import { api, OperationsSnapshot, WorkflowActionResponse } from "../lib/api";

function StatusPill({ status }: { status: string }) {
  const cls =
    status === "healthy"
      ? "bg-emerald-50 text-emerald-700"
      : status === "degraded" || status === "high"
        ? "bg-red-50 text-risk"
        : "bg-amber-50 text-amber-700";
  return <span className={`rounded px-2 py-1 text-xs font-semibold ${cls}`}>{status}</span>;
}

function ActionButton({
  label,
  action,
  target,
  onRun
}: {
  label: string;
  action: string;
  target: string;
  onRun: (action: string, target: string) => void;
}) {
  return (
    <button
      onClick={() => onRun(action, target)}
      className="inline-flex h-8 items-center gap-2 rounded-md border border-line px-3 text-xs hover:bg-slate-50"
    >
      <Play className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}

export function OperationsPage({
  token,
  onAskAi
}: {
  token: string;
  onAskAi: (question: string) => void;
}) {
  const [snapshot, setSnapshot] = useState<OperationsSnapshot | null>(null);
  const [lastAction, setLastAction] = useState<WorkflowActionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      setSnapshot(await api.operationsSnapshot(token));
    } finally {
      setLoading(false);
    }
  }

  async function run(action: string, target: string) {
    const response = await api.runOperationAction(
      token,
      action,
      target,
      "Operator validated simulated incident in portfolio demo"
    );
    setLastAction(response);
    await load();
  }

  async function askIncident(incidentId: string) {
    const response = await api.incidentPrompt(token, incidentId);
    localStorage.setItem("athena_prefill_question", response.question);
    onAskAi(response.question);
  }

  useEffect(() => {
    void load();
    const interval = window.setInterval(() => void load(), 30000);
    return () => window.clearInterval(interval);
  }, [token]);

  return (
    <div className="space-y-4">
      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-line bg-white p-4">
          <div className="mb-2 flex items-center justify-between text-sm text-slate-500">
            Overall
            <ServerCog className="h-4 w-4 text-signal" />
          </div>
          <div className="text-2xl font-semibold">{snapshot?.overall_status ?? "loading"}</div>
        </div>
        <div className="rounded-lg border border-line bg-white p-4">
          <div className="mb-2 text-sm text-slate-500">Market session</div>
          <div className="text-2xl font-semibold">{snapshot?.market_open ? "open" : "closed"}</div>
        </div>
        <div className="rounded-lg border border-line bg-white p-4">
          <div className="mb-2 text-sm text-slate-500">Open incidents</div>
          <div className="text-2xl font-semibold">{snapshot?.incidents.length ?? 0}</div>
        </div>
        <button
          onClick={load}
          className="inline-flex min-h-28 items-center justify-center gap-2 rounded-lg border border-line bg-white p-4 text-sm font-semibold hover:bg-slate-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </section>

      {lastAction && (
        <div className="rounded-lg border border-line bg-white p-4 text-sm">
          <div className="flex items-center gap-2 font-semibold text-signal">
            <CheckCircle2 className="h-4 w-4" />
            {lastAction.message}
          </div>
          <div className="mt-1 text-slate-500">{lastAction.audit_note}</div>
        </div>
      )}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="overflow-hidden rounded-lg border border-line bg-white">
          <div className="border-b border-line px-4 py-3 text-sm font-semibold">Exchange Feeds</div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Venue</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Drops</th>
                  <th className="px-4 py-3">Stale</th>
                  <th className="px-4 py-3">Heartbeat</th>
                </tr>
              </thead>
              <tbody>
                {snapshot?.feeds.map((feed) => (
                  <tr className="border-t border-line" key={feed.venue}>
                    <td className="px-4 py-3 font-medium">{feed.venue}</td>
                    <td className="px-4 py-3">
                      <StatusPill status={feed.status} />
                    </td>
                    <td className="px-4 py-3">{feed.latency_ms} ms</td>
                    <td className="px-4 py-3">{feed.dropped_messages}</td>
                    <td className="px-4 py-3">{feed.stale_symbols}</td>
                    <td className="px-4 py-3">{feed.heartbeat_age_seconds}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-lg border border-line bg-white p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <AlertTriangle className="h-4 w-4 text-risk" />
            Incident Queue
          </div>
          <div className="space-y-3">
            {snapshot?.incidents.map((incident) => (
              <div className="rounded-md border border-line p-3" key={incident.id}>
                <div className="mb-2 flex items-center justify-between gap-2">
                  <div className="text-sm font-semibold">{incident.id}</div>
                  <StatusPill status={incident.severity} />
                </div>
                <div className="text-sm">{incident.title}</div>
                <p className="mt-2 text-xs leading-5 text-slate-500">{incident.suggested_action}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <ActionButton label="Ack" action="ack_incident" target={incident.id} onRun={run} />
                  <ActionButton
                    label="Health Check"
                    action="run_health_check"
                    target={incident.service}
                    onRun={run}
                  />
                  <button
                    onClick={() => askIncident(incident.id)}
                    className="inline-flex h-8 items-center gap-2 rounded-md bg-ink px-3 text-xs text-white hover:bg-steel"
                  >
                    <Bot className="h-3.5 w-3.5" />
                    Ask AI
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="overflow-hidden rounded-lg border border-line bg-white">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold">Background Workers</div>
        <div className="grid gap-3 p-4 md:grid-cols-3">
          {snapshot?.workers.map((worker) => (
            <div className="rounded-md border border-line p-3" key={worker.name}>
              <div className="mb-2 flex items-center justify-between">
                <div className="text-sm font-semibold">{worker.name}</div>
                <StatusPill status={worker.status} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
                <div>Queue: {worker.queue}</div>
                <div>Depth: {worker.queue_depth}</div>
                <div>Failed: {worker.failed_jobs}</div>
                <div>Rate: {worker.processed_per_minute}/m</div>
              </div>
              <div className="mt-3 flex gap-2">
                <ActionButton label="Restart" action="restart_worker" target={worker.name} onRun={run} />
                <ActionButton label="Replay Gap" action="replay_gap" target={worker.queue} onRun={run} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
