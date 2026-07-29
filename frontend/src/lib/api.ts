const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

export type DocumentItem = {
  id: string;
  title: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
};

export type Citation = {
  document_id: string;
  chunk_id: string;
  title: string;
  score: number;
};

export type AskResponse = {
  conversation_id: string;
  answer: string;
  citations: Citation[];
  prompt_tokens: number;
  completion_tokens: number;
  evaluation_score: number;
};

export type UsageSummary = {
  prompt_tokens: number;
  completion_tokens: number;
  requests: number;
  cache_hits: number;
  active_users?: number;
  documents_indexed?: number;
  chunks_indexed?: number;
};

export type FeedStatus = {
  venue: string;
  asset_class: string;
  status: string;
  latency_ms: number;
  dropped_messages: number;
  stale_symbols: number;
  heartbeat_age_seconds: number;
};

export type WorkerStatus = {
  name: string;
  queue: string;
  status: string;
  queue_depth: number;
  failed_jobs: number;
  processed_per_minute: number;
  last_restart_at: string | null;
};

export type Incident = {
  id: string;
  severity: string;
  title: string;
  service: string;
  status: string;
  detected_at: string;
  suggested_action: string;
};

export type OperationsSnapshot = {
  generated_at: string;
  market_open: boolean;
  overall_status: string;
  feeds: FeedStatus[];
  workers: WorkerStatus[];
  incidents: Incident[];
};

export type WorkflowActionResponse = {
  action_id: string;
  status: string;
  message: string;
  audit_note: string;
  created_at: string;
};

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof body.detail === "string" ? body.detail : "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  login(email: string, password: string) {
    return request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },
  register(email: string, password: string, fullName: string) {
    return request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName })
    });
  },
  me(token: string) {
    return request<User>("/auth/me", {}, token);
  },
  documents(token: string) {
    return request<{ items: DocumentItem[]; total: number }>("/documents", {}, token);
  },
  uploadDocument(token: string, file: File, title: string) {
    const body = new FormData();
    body.append("file", file);
    body.append("title", title);
    return request<DocumentItem>("/documents", { method: "POST", body }, token);
  },
  indexDocument(token: string, documentId: string) {
    return request<DocumentItem>(`/documents/${documentId}/index`, { method: "POST" }, token);
  },
  ask(token: string, question: string, conversationId?: string) {
    return request<AskResponse>(
      "/ai/ask",
      {
        method: "POST",
        body: JSON.stringify({ question, conversation_id: conversationId, stream: false, top_k: 5 })
      },
      token
    );
  },
  usage(token: string) {
    return request<UsageSummary>("/usage/me", {}, token);
  },
  adminUsage(token: string) {
    return request<UsageSummary>("/admin/usage", {}, token);
  },
  operationsSnapshot(token: string) {
    return request<OperationsSnapshot>("/operations/snapshot", {}, token);
  },
  runOperationAction(token: string, action: string, target: string, reason: string) {
    return request<WorkflowActionResponse>(
      "/operations/actions",
      {
        method: "POST",
        body: JSON.stringify({ action, target, reason })
      },
      token
    );
  },
  incidentPrompt(token: string, incidentId: string) {
    return request<{ question: string }>(`/operations/incidents/${incidentId}/prompt`, {}, token);
  }
};
