import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { ExperimentsPage } from "./ExperimentsPage";

vi.mock("../api", async (original) => ({
  ...(await original<typeof import("../api")>()),
  getExperiments: vi.fn(),
  getExperiment: vi.fn(),
  createExperiment: vi.fn(),
  updateExperiment: vi.fn(),
  appendExperimentResult: vi.fn(),
}));
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
const experiment: api.Experiment = {
  id: "e1",
  name: "Clasificador",
  status: "draft",
  creator_id: "u1",
  created_at: "2026-03-30T10:00:00Z",
  updated_at: "2026-03-30T10:00:00Z",
};
const page = (items = [experiment]): api.ExperimentsResponse => ({
  items,
  total: items.length,
  page: 1,
  per_page: 10,
  pages: 1,
});

describe("ExperimentsPage", () => {
  it("renders bounded loading, empty, and viewer read-only states", async () => {
    let resolve!: (value: api.ExperimentsResponse) => void;
    vi.mocked(api.getExperiments).mockReturnValueOnce(
      new Promise((done) => {
        resolve = done;
      }),
    );
    const view = render(<ExperimentsPage canMutate={false} />);
    expect(screen.getByLabelText("Cargando experimentos")).toBeInTheDocument();
    resolve(page([]));
    expect(
      await screen.findByText(/Cuando el equipo cree uno/),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Crear experimento/ }),
    ).not.toBeInTheDocument();
    view.unmount();

    vi.mocked(api.getExperiments).mockResolvedValueOnce(page());
    vi.mocked(api.getExperiment).mockResolvedValueOnce({
      ...experiment,
      results: [],
    });
    render(<ExperimentsPage canMutate={false} />);
    fireEvent.click(
      (await screen.findAllByRole("button", { name: "Ver detalle" }))[0],
    );
    expect(
      await screen.findByText("Todavía no hay resultados registrados."),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Iniciar experimento" }),
    ).not.toBeInTheDocument();
  });

  it("creates an experiment and refreshes the first page", async () => {
    vi.mocked(api.getExperiments).mockResolvedValue(page([]));
    vi.mocked(api.createExperiment).mockResolvedValue(experiment);
    render(<ExperimentsPage canMutate />);
    fireEvent.click(
      await screen.findByRole("button", { name: "Crear experimento" }),
    );
    fireEvent.change(screen.getByLabelText("Nombre del experimento"), {
      target: { value: "  Modelo nuevo  " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crear" }));
    await waitFor(() =>
      expect(api.createExperiment).toHaveBeenCalledWith("Modelo nuevo"),
    );
    await waitFor(() => expect(api.getExperiments).toHaveBeenCalledTimes(2));
  });

  it("starts a draft and exposes localized errors", async () => {
    vi.mocked(api.getExperiments).mockResolvedValue(page());
    vi.mocked(api.getExperiment).mockResolvedValue({
      ...experiment,
      results: [],
    });
    vi.mocked(api.updateExperiment).mockRejectedValueOnce(
      new Error("La transición de estado no es válida."),
    );
    render(<ExperimentsPage canMutate />);
    fireEvent.click(
      (await screen.findAllByRole("button", { name: "Ver detalle" }))[0],
    );
    fireEvent.click(
      await screen.findByRole("button", { name: "Iniciar experimento" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "La transición de estado no es válida.",
    );
    expect(api.updateExperiment).toHaveBeenCalledWith("e1", "running");
  });

  it("appends a typed result, closes the lifecycle, and presents provenance", async () => {
    const running = { ...experiment, status: "running" as const };
    vi.mocked(api.getExperiments).mockResolvedValue(page([running]));
    vi.mocked(api.getExperiment).mockResolvedValue({
      ...running,
      results: [
        {
          id: "r1",
          status: "completed",
          creator_id: "u1",
          created_at: "2026-03-30T11:00:00Z",
          input_summary: "datos",
          output_summary: "predicción",
          metrics: [
            {
              id: "m1",
              creator_id: "u1",
              name: "exactitud",
              value_type: "number",
              number_value: 0.92,
              text_value: null,
              boolean_value: null,
              json_value: null,
              unit: "%",
              step: 2,
              recorded_at: "2026-03-30T11:00:00Z",
            },
          ],
        },
      ],
    });
    vi.mocked(api.appendExperimentResult).mockResolvedValue(
      {} as api.ExperimentResult,
    );
    vi.mocked(api.updateExperiment).mockResolvedValue({
      ...running,
      status: "completed",
    });
    render(<ExperimentsPage canMutate />);
    fireEvent.click(
      (await screen.findAllByRole("button", { name: "Ver detalle" }))[0],
    );
    expect(await screen.findByText("exactitud")).toBeInTheDocument();
    expect(screen.getByText(/Número · paso 2/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Resumen de salida"), {
      target: { value: "listo" },
    });
    fireEvent.change(screen.getByLabelText("Métrica opcional"), {
      target: { value: "pérdida" },
    });
    fireEvent.change(screen.getByLabelText("Valor"), {
      target: { value: "0.1" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Registrar resultado" }),
    );
    await waitFor(() =>
      expect(api.appendExperimentResult).toHaveBeenCalledWith("e1", {
        status: "completed",
        output_summary: "listo",
        metrics: [{ name: "pérdida", type: "number", value: 0.1 }],
      }),
    );
    expect(api.updateExperiment).toHaveBeenCalledWith("e1", "completed");
  });
});
