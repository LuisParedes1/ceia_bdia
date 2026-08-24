import { type FormEvent, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import * as api from "../api";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "../components/ui/dialog";
import { Field, FieldGroup } from "../components/ui/field";
import { Skeleton } from "../components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

const statusLabel: Record<api.ExperimentStatus, string> = {
  draft: "Borrador",
  running: "En ejecución",
  completed: "Completado",
  failed: "Fallido",
};
const typeLabel: Record<api.MetricType, string> = {
  number: "Número",
  text: "Texto",
  boolean: "Sí/no",
  json: "JSON",
};
const date = (value: string) =>
  new Intl.DateTimeFormat("es-AR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
const metricValue = (metric: api.Metric) => {
  const value = metric[`${metric.value_type}_value` as keyof api.Metric];
  if (metric.value_type === "boolean") return value ? "Sí" : "No";
  if (metric.value_type === "json") return JSON.stringify(value);
  return String(value ?? "—");
};

function ExperimentDialog({
  experiment,
  canMutate,
  onClose,
  onChanged,
}: {
  experiment: api.Experiment | null;
  canMutate: boolean;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [detail, setDetail] = useState<api.Experiment | null>(null);
  const [error, setError] = useState("");
  const [output, setOutput] = useState("");
  const [resultStatus, setResultStatus] = useState<"completed" | "failed">(
    "completed",
  );
  const [metricName, setMetricName] = useState("");
  const [metricType, setMetricType] = useState<api.MetricType>("number");
  const [metricRaw, setMetricRaw] = useState("");
  useEffect(() => {
    if (!experiment) return;
    api
      .getExperiment(experiment.id)
      .then(setDetail)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "No se pudo cargar el experimento.",
        ),
      );
  }, [experiment]);
  if (!experiment) return null;
  const transition = async (status: api.ExperimentStatus) => {
    try {
      await api.updateExperiment(experiment.id, status);
      onChanged();
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "No se pudo actualizar el experimento.",
      );
    }
  };
  const submitResult = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      let value: api.MetricInput["value"] = metricRaw;
      if (metricType === "number") value = Number(metricRaw);
      if (metricType === "boolean") value = metricRaw === "true";
      if (metricType === "json") value = JSON.parse(metricRaw) as object;
      const metrics = metricName
        ? [{ name: metricName, type: metricType, value }]
        : [];
      await api.appendExperimentResult(experiment.id, {
        status: resultStatus,
        output_summary: output || undefined,
        metrics,
      });
      await api.updateExperiment(experiment.id, resultStatus);
      onChanged();
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Revisá el valor de la métrica.",
      );
    }
  };
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        aria-describedby="experiment-description"
        className="experiment-dialog"
      >
        <div className="dialog-header">
          <DialogTitle>{experiment.name}</DialogTitle>
          <DialogDescription id="experiment-description">
            Estado, resultados y procedencia registrada.
          </DialogDescription>
        </div>
        {!detail && !error && <p>Cargando detalle…</p>}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {detail && (
          <>
            <dl className="details-list">
              <div>
                <dt>Estado</dt>
                <dd>
                  <Badge>{statusLabel[detail.status]}</Badge>
                </dd>
              </div>
              <div>
                <dt>Creado</dt>
                <dd>{date(detail.created_at)}</dd>
              </div>
            </dl>
            {detail.results?.length ? (
              detail.results.map((result) => (
                <article className="result-card" key={result.id}>
                  <strong>Resultado {statusLabel[result.status]}</strong>
                  <span className="muted">
                    Registrado {date(result.created_at)}
                  </span>
                  {result.input_summary && (
                    <p>
                      <b>Entrada:</b> {result.input_summary}
                    </p>
                  )}
                  {result.output_summary && (
                    <p>
                      <b>Salida:</b> {result.output_summary}
                    </p>
                  )}
                  {result.metrics.map((metric) => (
                    <div className="metric" key={metric.id}>
                      <b>{metric.name}</b>
                      <span>
                        {metricValue(metric)} {metric.unit ?? ""}
                      </span>
                      <small>
                        {typeLabel[metric.value_type]}
                        {metric.step === null ? "" : ` · paso ${metric.step}`} ·{" "}
                        {date(metric.recorded_at)}
                      </small>
                    </div>
                  ))}
                </article>
              ))
            ) : (
              <p className="notice">Todavía no hay resultados registrados.</p>
            )}
            {canMutate && detail.status === "draft" && (
              <Button onClick={() => void transition("running")}>
                Iniciar experimento
              </Button>
            )}
            {canMutate && detail.status === "running" && (
              <form onSubmit={submitResult}>
                <FieldGroup>
                  <Field>
                    <label htmlFor="result-status">Resultado</label>
                    <select
                      id="result-status"
                      value={resultStatus}
                      onChange={(event) =>
                        setResultStatus(
                          event.target.value as "completed" | "failed",
                        )
                      }
                    >
                      <option value="completed">Completado</option>
                      <option value="failed">Fallido</option>
                    </select>
                  </Field>
                  <Field>
                    <label htmlFor="result-output">Resumen de salida</label>
                    <input
                      id="result-output"
                      value={output}
                      onChange={(event) => setOutput(event.target.value)}
                    />
                  </Field>
                  <Field>
                    <label htmlFor="metric-name">Métrica opcional</label>
                    <input
                      id="metric-name"
                      value={metricName}
                      onChange={(event) => setMetricName(event.target.value)}
                    />
                  </Field>
                  {metricName && (
                    <div className="metric-fields">
                      <Field>
                        <label htmlFor="metric-type">Tipo</label>
                        <select
                          id="metric-type"
                          value={metricType}
                          onChange={(event) =>
                            setMetricType(event.target.value as api.MetricType)
                          }
                        >
                          {Object.entries(typeLabel).map(([value, label]) => (
                            <option value={value} key={value}>
                              {label}
                            </option>
                          ))}
                        </select>
                      </Field>
                      <Field>
                        <label htmlFor="metric-value">Valor</label>
                        {metricType === "boolean" ? (
                          <select
                            id="metric-value"
                            value={metricRaw}
                            onChange={(event) =>
                              setMetricRaw(event.target.value)
                            }
                            required
                          >
                            <option value="">Seleccionar</option>
                            <option value="true">Sí</option>
                            <option value="false">No</option>
                          </select>
                        ) : (
                          <input
                            id="metric-value"
                            value={metricRaw}
                            onChange={(event) =>
                              setMetricRaw(event.target.value)
                            }
                            required
                          />
                        )}
                      </Field>
                    </div>
                  )}
                  <Button type="submit">Registrar resultado</Button>
                </FieldGroup>
              </form>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

export function ExperimentsPage({ canMutate }: { canMutate: boolean }) {
  const [page, setPage] = useState(1),
    [result, setResult] = useState<api.ExperimentsResponse | null>(null);
  const [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [reload, setReload] = useState(0);
  const [name, setName] = useState(""),
    [creating, setCreating] = useState(false),
    [selected, setSelected] = useState<api.Experiment | null>(null);
  useEffect(() => {
    api
      .getExperiments(page)
      .then(setResult)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "No se pudieron cargar los experimentos.",
        ),
      )
      .finally(() => setLoading(false));
  }, [page, reload]);
  const create = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      await api.createExperiment(name.trim());
      setName("");
      setCreating(false);
      setPage(1);
      setReload((value) => value + 1);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "No se pudo crear el experimento.",
      );
    }
  };
  return (
    <section className="experiments-page">
      <div className="page-header">
        <div>
          <h1>Experimentos</h1>
          <p className="muted">
            Seguimiento de ejecuciones, resultados y métricas.
          </p>
        </div>
        {canMutate && (
          <Button onClick={() => setCreating(true)}>
            <Plus />
            Crear experimento
          </Button>
        )}
      </div>
      {creating && (
        <form className="notice inline-form" onSubmit={create}>
          <label htmlFor="experiment-name">Nombre del experimento</label>
          <input
            id="experiment-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={200}
            required
            autoFocus
          />
          <Button type="submit">Crear</Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setCreating(false)}
          >
            Cancelar
          </Button>
        </form>
      )}
      {loading ? (
        <div
          className="desktop-table-loading"
          aria-label="Cargando experimentos"
        >
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </div>
      ) : error ? (
        <section className="notice error" role="alert">
          <p>{error}</p>
          <Button
            variant="outline"
            onClick={() => {
              setError("");
              setLoading(true);
              setReload((value) => value + 1);
            }}
          >
            Reintentar
          </Button>
        </section>
      ) : result?.items.length ? (
        <>
          <div className="desktop-table">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Actualizado</TableHead>
                  <TableHead>Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>
                      <Badge>{statusLabel[item.status]}</Badge>
                    </TableCell>
                    <TableCell>{date(item.updated_at)}</TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        onClick={() => setSelected(item)}
                      >
                        Ver detalle
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="member-cards">
            {result.items.map((item) => (
              <article className="member-card" key={item.id}>
                <strong>{item.name}</strong>
                <Badge>{statusLabel[item.status]}</Badge>
                <span className="muted">{date(item.updated_at)}</span>
                <Button variant="outline" onClick={() => setSelected(item)}>
                  Ver detalle
                </Button>
              </article>
            ))}
          </div>
          <nav className="pagination" aria-label="Paginación de experimentos">
            <span>
              {result.total} experimentos · Página {result.page} de{" "}
              {result.pages}
            </span>
            <div>
              <Button
                aria-label="Página anterior"
                variant="outline"
                disabled={page <= 1}
                onClick={() => {
                  setLoading(true);
                  setPage(page - 1);
                }}
              >
                <ChevronLeft />
              </Button>
              <Button
                aria-label="Página siguiente"
                variant="outline"
                disabled={page >= result.pages}
                onClick={() => {
                  setLoading(true);
                  setPage(page + 1);
                }}
              >
                <ChevronRight />
              </Button>
            </div>
          </nav>
        </>
      ) : (
        <section className="notice">
          No hay experimentos todavía.
          {canMutate
            ? " Creá el primero para comenzar."
            : " Cuando el equipo cree uno, aparecerá aquí."}
        </section>
      )}
      <ExperimentDialog
        key={selected?.id ?? "closed"}
        experiment={selected}
        canMutate={canMutate}
        onClose={() => setSelected(null)}
        onChanged={() => setReload((value) => value + 1)}
      />
    </section>
  );
}
