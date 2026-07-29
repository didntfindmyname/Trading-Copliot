import { FileUp, RefreshCw } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api, DocumentItem } from "../lib/api";

export function DocumentsPage({ token }: { token: string }) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");

  async function load() {
    const response = await api.documents(token);
    setDocuments(response.items);
  }

  useEffect(() => {
    void load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    await api.uploadDocument(token, file, title || file.name);
    setFile(null);
    setTitle("");
    await load();
  }

  async function index(id: string) {
    await api.indexDocument(token, id);
    await load();
  }

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="grid gap-3 rounded-lg border border-line bg-white p-4 md:grid-cols-[1fr_1fr_auto]">
        <input className="h-10 rounded-md border border-line px-3 text-sm" placeholder="Document title" value={title} onChange={(event) => setTitle(event.target.value)} />
        <input className="h-10 rounded-md border border-line px-3 text-sm" type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        <button className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-signal px-4 text-sm font-semibold text-white">
          <FileUp className="h-4 w-4" />
          Upload
        </button>
      </form>
      <section className="overflow-hidden rounded-lg border border-line bg-white">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold">Document Inventory</div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">File</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Chunks</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr className="border-t border-line" key={doc.id}>
                  <td className="px-4 py-3 font-medium">{doc.title}</td>
                  <td className="px-4 py-3 text-slate-500">{doc.filename}</td>
                  <td className="px-4 py-3">{doc.status}</td>
                  <td className="px-4 py-3">{doc.chunk_count}</td>
                  <td className="px-4 py-3">
                    <button onClick={() => index(doc.id)} className="inline-flex h-8 items-center gap-2 rounded-md border border-line px-3 text-xs hover:bg-slate-50">
                      <RefreshCw className="h-3.5 w-3.5" />
                      Index
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

