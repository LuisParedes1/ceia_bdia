import { type FormEvent, useState } from "react";
import { Download, Upload } from "lucide-react";
import * as api from "../api";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";

const status: Record<api.DocumentStatus, string> = {
  pending: "Pendiente",
  processing: "Procesando",
  ready: "Disponible",
  failed: "Fallido",
};
const message = (reason: unknown) =>
  reason instanceof Error
    ? reason.message
    : "No se pudo completar la solicitud.";

export function DocumentsPage({ canMutate }: { canMutate: boolean }) {
  const [documents, setDocuments] = useState<api.Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState("");
  const [citations, setCitations] = useState<api.Citation[]>([]);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const replace = (id: string, patch: Partial<api.Document>) =>
    setDocuments((items) =>
      items.map((item) => (item.id === id ? { ...item, ...patch } : item)),
    );
  const upload = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    setBusy("upload");
    setError("");
    try {
      const uploaded = await api.uploadDocument(file);
      setDocuments((items) => [uploaded, ...items]);
      setFile(null);
    } catch (reason) {
      setError(message(reason));
    } finally {
      setBusy("");
    }
  };
  const ingest = async (document: api.Document) => {
    setBusy(document.id);
    setError("");
    replace(document.id, { ingestion_status: "processing" });
    try {
      replace(document.id, await api.ingestDocument(document.id));
    } catch (reason) {
      replace(document.id, { ingestion_status: "failed" });
      setError(message(reason));
    } finally {
      setBusy("");
    }
  };
  const download = async (document: api.Document) => {
    setError("");
    try {
      const url = URL.createObjectURL(await api.downloadDocument(document.id));
      const anchor = window.document.createElement("a");
      anchor.href = url;
      anchor.download = document.name;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (reason) {
      setError(message(reason));
    }
  };
  const retrieve = async (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    setBusy("retrieve");
    setError("");
    try {
      setCitations((await api.retrieveDocuments(query.trim())).citations);
    } catch (reason) {
      setError(message(reason));
      setCitations([]);
    } finally {
      setBusy("");
    }
  };
  return (
    <section className="workspace-page">
      <div className="page-header">
        <div>
          <h1>Documentos</h1>
          <p className="muted">
            Archivos privados y evidencia recuperable del espacio actual.
          </p>
        </div>
      </div>
      {canMutate && (
        <form className="notice inline-form" onSubmit={upload}>
          <label htmlFor="document-file">Archivo PDF, TXT o MD</label>
          <input
            id="document-file"
            type="file"
            accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
            required
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <Button type="submit" disabled={!file || busy === "upload"}>
            <Upload />
            {busy === "upload" ? "Subiendo…" : "Subir archivo"}
          </Button>
        </form>
      )}
      {error && (
        <p className="notice error" role="alert">
          {error}
        </p>
      )}
      <div className="document-grid" aria-live="polite">
        {documents.length ? (
          documents.map((document) => (
            <article className="member-card document-card" key={document.id}>
              <strong>{document.name}</strong>
              <Badge>{status[document.ingestion_status]}</Badge>
              {document.size_bytes && (
                <span className="muted">
                  {Math.ceil(document.size_bytes / 1024)} KB
                </span>
              )}
              <div>
                <Button
                  variant="outline"
                  onClick={() => void download(document)}
                >
                  <Download />
                  Descargar original
                </Button>
                {canMutate && document.ingestion_status !== "processing" && (
                  <Button
                    onClick={() => void ingest(document)}
                    disabled={busy === document.id}
                  >
                    {document.ingestion_status === "ready"
                      ? "Reprocesar"
                      : "Ingerir"}
                  </Button>
                )}
              </div>
            </article>
          ))
        ) : (
          <p className="notice">
            No hay documentos cargados en esta sesión.
            {canMutate
              ? " Subí uno para comenzar."
              : " La carga está disponible para integrantes autorizados."}
          </p>
        )}
      </div>
      <form className="notice inline-form" onSubmit={retrieve}>
        <label htmlFor="retrieval-query">
          Buscar evidencia en documentos ingeridos
        </label>
        <input
          id="retrieval-query"
          value={query}
          maxLength={1000}
          required
          onChange={(event) => setQuery(event.target.value)}
        />
        <Button type="submit" disabled={busy === "retrieve"}>
          {busy === "retrieve" ? "Buscando…" : "Buscar"}
        </Button>
      </form>
      {citations.length ? (
        <section aria-label="Fragmentos recuperados" className="citation-list">
          {citations.map((item) => (
            <article className="notice" key={item.chunk_id}>
              <strong>
                {item.document_name} · fragmento {item.ordinal + 1}
              </strong>
              <p>{item.content}</p>
            </article>
          ))}
        </section>
      ) : (
        query &&
        busy !== "retrieve" && (
          <p className="muted">No hay fragmentos para mostrar.</p>
        )
      )}
    </section>
  );
}
