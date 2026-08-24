import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { DocumentsPage } from "./DocumentsPage";

vi.mock("../api", async (original) => ({
  ...(await original<typeof import("../api")>()),
  uploadDocument: vi.fn(),
  ingestDocument: vi.fn(),
  retrieveDocuments: vi.fn(),
  downloadDocument: vi.fn(),
}));
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("DocumentsPage", () => {
  it("keeps viewers read-only and offers bounded retrieval", async () => {
    vi.mocked(api.retrieveDocuments).mockResolvedValue({
      citations: [
        {
          chunk_id: "c1",
          document_id: "d1",
          document_name: "guia.md",
          ordinal: 0,
          content: "Evidencia segura",
        },
      ],
    });
    render(<DocumentsPage canMutate={false} />);
    expect(screen.queryByLabelText(/Archivo PDF/)).not.toBeInTheDocument();
    expect(screen.getByText(/integrantes autorizados/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/Buscar evidencia/), {
      target: { value: "resumen" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));
    expect(await screen.findByText("Evidencia segura")).toBeInTheDocument();
    expect(api.retrieveDocuments).toHaveBeenCalledWith("resumen");
  });

  it("uploads and ingests an allowed document", async () => {
    const document: api.Document = {
      id: "d1",
      name: "guia.md",
      ingestion_status: "pending",
      size_bytes: 10,
    };
    vi.mocked(api.uploadDocument).mockResolvedValue(document);
    vi.mocked(api.ingestDocument).mockResolvedValue({
      ...document,
      ingestion_status: "ready",
      chunk_count: 1,
    });
    render(<DocumentsPage canMutate />);
    const file = new File(["texto"], "guia.md", { type: "text/markdown" });
    const input = screen.getByLabelText(/Archivo PDF/);
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.submit(input.closest("form")!);
    expect(await screen.findByText("guia.md")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Ingerir" }));
    await waitFor(() => expect(api.ingestDocument).toHaveBeenCalledWith("d1"));
    expect(await screen.findByText("Disponible")).toBeInTheDocument();
  });
});
