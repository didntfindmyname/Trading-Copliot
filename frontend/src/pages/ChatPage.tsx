import { Send, Sparkles } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api, AskResponse } from "../lib/api";

type ChatTurn = { role: "user" | "assistant"; content: string; response?: AskResponse };

export function ChatPage({ token }: { token: string }) {
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [question, setQuestion] = useState("How do we recover a failed market data ingestion job?");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const prefill = localStorage.getItem("athena_prefill_question");
    if (prefill) {
      setQuestion(prefill);
      localStorage.removeItem("athena_prefill_question");
    }
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    const asked = question;
    setTurns((prev) => [...prev, { role: "user", content: asked }]);
    setQuestion("");
    setLoading(true);
    try {
      const response = await api.ask(token, asked, conversationId);
      setConversationId(response.conversation_id);
      setTurns((prev) => [...prev, { role: "assistant", content: response.answer, response }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section className="min-h-[72vh] rounded-lg border border-line bg-white">
        <div className="flex h-12 items-center gap-2 border-b border-line px-4">
          <Sparkles className="h-4 w-4 text-signal" />
          <h2 className="text-sm font-semibold">Engineering Chat</h2>
        </div>
        <div className="h-[58vh] space-y-4 overflow-y-auto p-4">
          {turns.length === 0 && (
            <div className="rounded-md border border-dashed border-line p-4 text-sm text-slate-500">
              Ask about indexed runbooks, code, incident notes, deployment procedures, or research docs.
            </div>
          )}
          {turns.map((turn, index) => (
            <div key={index} className={turn.role === "user" ? "text-right" : "text-left"}>
              <div className={`inline-block max-w-[86%] rounded-md px-3 py-2 text-sm ${turn.role === "user" ? "bg-ink text-white" : "bg-slate-100 text-ink"}`}>
                <p className="whitespace-pre-wrap">{turn.content}</p>
              </div>
            </div>
          ))}
          {loading && <div className="text-sm text-slate-500">Thinking across indexed sources...</div>}
        </div>
        <form className="flex gap-2 border-t border-line p-3" onSubmit={submit}>
          <input className="h-10 flex-1 rounded-md border border-line px-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button className="inline-flex h-10 items-center gap-2 rounded-md bg-signal px-4 text-sm font-semibold text-white">
            <Send className="h-4 w-4" />
            Ask
          </button>
        </form>
      </section>
      <aside className="rounded-lg border border-line bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold">Latest Citations</h3>
        {turns.filter((turn) => turn.response).slice(-1).map((turn) => (
          <div key={turn.response?.conversation_id} className="space-y-2">
            {turn.response?.citations.map((citation) => (
              <div className="rounded-md border border-line p-3 text-sm" key={citation.chunk_id}>
                <div className="font-medium">{citation.title}</div>
                <div className="text-xs text-slate-500">score {citation.score.toFixed(3)}</div>
              </div>
            ))}
            <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
              <div className="rounded-md bg-slate-100 p-2">Prompt {turn.response?.prompt_tokens}</div>
              <div className="rounded-md bg-slate-100 p-2">Completion {turn.response?.completion_tokens}</div>
              <div className="col-span-2 rounded-md bg-slate-100 p-2">Eval {turn.response?.evaluation_score}</div>
            </div>
          </div>
        ))}
      </aside>
    </div>
  );
}
