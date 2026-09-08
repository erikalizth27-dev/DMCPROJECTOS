import { FormEvent, useState } from "react";
import { ApiClientError, crearSiniestro, obtenerLineaTiempo, obtenerSiniestro } from "./api/client";
import type { CrearSiniestro, LineaTiempoSiniestro, Siniestro } from "./types";
import { useAuth } from "./auth/AuthContext";
import { LoginScreen } from "./auth/LoginScreen";

type View = "reportar" | "consultar";

const initialForm: CrearSiniestro = {
  numeroPoliza: "",
  numeroDocumento: "",
  placa: "",
  fechaEvento: "",
  ubicacionEvento: "",
  tipoEvento: "",
  medioContacto: "",
};

const estadoLabels: Record<string, string> = {
  reportado: "Reportado",
  validando_cobertura: "Validando cobertura",
  asistencia_coordinada: "Asistencia coordinada",
  evidencia_pendiente: "Evidencia pendiente",
  en_evaluacion: "En evaluación",
  inspeccion_programada: "Inspección programada",
  presupuesto_recibido: "Presupuesto recibido",
  autorizado: "Autorizado",
  observado: "Observado",
  rechazado: "Rechazado",
  en_reparacion: "En reparación",
  listo_para_entrega: "Listo para entrega",
  indemnizado: "Indemnizado",
  cerrado: "Cerrado",
};

function Icon({ name }: { name: "shield" | "file" | "search" | "arrow" }) {
  const paths = {
    shield: <path d="M12 3 5 6v5c0 4.7 2.9 8.2 7 10 4.1-1.8 7-5.3 7-10V6l-7-3Z" />,
    file: <path d="M7 3h7l4 4v14H7V3Zm7 0v5h5M10 12h5M10 16h5" />,
    search: <path d="m20 20-4.6-4.6M18 11a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z" />,
    arrow: <path d="m9 18 6-6-6-6" />,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>;
}

interface Guidance {
  title: string;
  description: string;
}

const guidanceByState: Partial<Record<Siniestro["estadoActual"], Guidance>> = {
  reportado: {
    title: "Validaremos la cobertura",
    description: "Mantén disponible el medio de contacto registrado por si necesitamos confirmar información.",
  },
  validando_cobertura: {
    title: "La cobertura está en revisión",
    description: "Puedes seguir consultando este caso; aquí aparecerá cualquier cambio o solicitud.",
  },
  asistencia_coordinada: {
    title: "Sigue las indicaciones de la asistencia",
    description: "La respuesta del proveedor y los cambios del caso aparecerán en el historial.",
  },
  evidencia_pendiente: {
    title: "Prepara la evidencia solicitada",
    description: "Conserva los archivos originales de las fotografías y documentos para adjuntarlos cuando se soliciten.",
  },
  en_evaluacion: {
    title: "El caso está siendo evaluado",
    description: "Consulta el historial para conocer cuándo se programe la inspección o se registre una decisión.",
  },
  inspeccion_programada: {
    title: "Revisa la coordinación de la inspección",
    description: "Mantén disponible el medio de contacto registrado para recibir las indicaciones correspondientes.",
  },
  presupuesto_recibido: {
    title: "El presupuesto está en revisión",
    description: "La aprobación, observación o rechazo se mostrará en el estado y en el historial.",
  },
  autorizado: {
    title: "La atención fue autorizada",
    description: "Consulta el historial para conocer el avance de la reparación o indemnización.",
  },
  observado: {
    title: "El caso requiere información adicional",
    description: "Revisa el historial y mantén disponible tu medio de contacto para atender la observación.",
  },
  rechazado: {
    title: "Revisa la decisión registrada",
    description: "Consulta el historial del caso para ver la información que puede mostrarse a tu perfil.",
  },
  en_reparacion: {
    title: "La reparación está en curso",
    description: "Los cambios informados por el proceso aparecerán en el historial.",
  },
  listo_para_entrega: {
    title: "El vehículo está listo para entrega",
    description: "Sigue las indicaciones registradas para completar la entrega.",
  },
  indemnizado: {
    title: "La indemnización fue registrada",
    description: "Consulta el historial para revisar el avance final del caso.",
  },
  cerrado: {
    title: "El caso está cerrado",
    description: "El historial permanece disponible para consultar los movimientos visibles.",
  },
};

function NextStepCard({ claim }: { claim: Siniestro }) {
  const fallback = claim.siguientePaso?.replaceAll("_", " ") ?? "Consulta el historial del caso";
  const guidance = guidanceByState[claim.estadoActual] ?? {
    title: fallback,
    description: "Consulta el historial para conocer las actualizaciones disponibles.",
  };

  return (
    <section className="next-step-card" aria-labelledby="next-step-title">
      <span aria-hidden="true">→</span>
      <div>
        <p>Qué hacer ahora</p>
        <h3 id="next-step-title">{guidance.title}</h3>
        <p>{guidance.description}</p>
      </div>
    </section>
  );
}

function App() {
  const { session, signOut } = useAuth();
  const [view, setView] = useState<View>("reportar");
  const [form, setForm] = useState<CrearSiniestro>(initialForm);
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState<Siniestro | null>(null);
  const [timeline, setTimeline] = useState<LineaTiempoSiniestro | null>(null);
  const [notice, setNotice] = useState<{ tone: "error" | "success"; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [timelineBusy, setTimelineBusy] = useState(false);
  const [timelineError, setTimelineError] = useState<string | null>(null);

  if (!session) {
    return <LoginScreen />;
  }

  const accessToken: string = session.idToken;

  function updateField(field: keyof CrearSiniestro, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
    setNotice(null);
  }

  async function submitReport(event: FormEvent) {
    event.preventDefault();
    setNotice(null);

    if (!form.numeroPoliza?.trim() && !form.numeroDocumento?.trim()) {
      setNotice({ tone: "error", text: "Ingresa el número de póliza o el documento." });
      return;
    }

    setBusy(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).filter(([, value]) => value !== ""),
      ) as unknown as CrearSiniestro;
      payload.fechaEvento = new Date(form.fechaEvento).toISOString();
      const created = await crearSiniestro(payload, accessToken);
      setResult(created);
      setCaseId(String(created.id));
      setNotice({ tone: "success", text: `Reporte #${created.id} registrado correctamente.` });
    } catch (error) {
      setNotice({
        tone: "error",
        text: error instanceof ApiClientError ? error.message : "Ocurrió un error inesperado.",
      });
    } finally {
      setBusy(false);
    }
  }

  async function searchCase(event: FormEvent) {
    event.preventDefault();
    setNotice(null);
    setTimelineError(null);
    const id = Number(caseId);
    if (!Number.isInteger(id) || id < 1) {
      setNotice({ tone: "error", text: "Ingresa un número de caso válido." });
      return;
    }

    setBusy(true);
    try {
      const [found, history] = await Promise.all([
        obtenerSiniestro(id, accessToken),
        obtenerLineaTiempo(id, accessToken),
      ]);
      setResult(found);
      setTimeline(history);
    } catch (error) {
      setResult(null);
      setTimeline(null);
      setNotice({
        tone: "error",
        text: error instanceof ApiClientError ? error.message : "No fue posible consultar el caso.",
      });
    } finally {
      setBusy(false);
    }
  }

  async function loadMoreTimeline() {
    if (!result || !timeline?.siguienteCursor || timelineBusy) {
      return;
    }

    setTimelineBusy(true);
    setTimelineError(null);
    try {
      const nextPage = await obtenerLineaTiempo(
        result.id,
        accessToken,
        timeline.siguienteCursor,
      );
      const eventsById = new Map(
        [...timeline.eventos, ...nextPage.eventos].map((event) => [event.id, event]),
      );
      setTimeline({
        ...nextPage,
        eventos: [...eventsById.values()],
      });
    } catch (error) {
      setTimelineError(
        error instanceof ApiClientError
          ? error.message
          : "No fue posible cargar más movimientos.",
      );
    } finally {
      setTimelineBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Siniestro Fácil, inicio">
          <span className="brand-mark"><Icon name="shield" /></span>
          <span>Siniestro <strong>Fácil</strong></span>
        </a>
        <div className="account"><span>{session.user.email}</span><button type="button" onClick={signOut}>Salir</button></div>
      </header>

      <main>
        <section className="intro">
          <p className="eyebrow">Seguro vehicular</p>
          <h1>Estamos aquí para ayudarte.</h1>
          <p>Reporta lo ocurrido con la información que tengas. Puedes completar las evidencias después.</p>
        </section>

        <nav className="view-tabs" aria-label="Acciones principales">
          <button className={view === "reportar" ? "active" : ""} onClick={() => { setView("reportar"); setNotice(null); }}>
            <Icon name="file" /> Reportar siniestro
          </button>
          <button className={view === "consultar" ? "active" : ""} onClick={() => { setView("consultar"); setNotice(null); }}>
            <Icon name="search" /> Consultar mi caso
          </button>
        </nav>

        <div className="workspace">
          {view === "reportar" ? (
            <form className="panel form-panel" onSubmit={submitReport}>
              <div className="section-heading">
                <span className="step">1</span>
                <div><h2>Datos del reporte</h2><p>Completa los datos mínimos para iniciar la atención.</p></div>
              </div>

              <fieldset>
                <legend>Identificación</legend>
                <p className="field-hint">Ingresa al menos uno de estos datos.</p>
                <div className="field-grid">
                  <label>Número de póliza<input value={form.numeroPoliza} onChange={(e) => updateField("numeroPoliza", e.target.value)} autoComplete="off" /></label>
                  <label>Número de documento<input value={form.numeroDocumento} onChange={(e) => updateField("numeroDocumento", e.target.value)} autoComplete="off" /></label>
                </div>
              </fieldset>

              <fieldset>
                <legend>¿Qué ocurrió?</legend>
                <div className="field-grid">
                  <label>Placa del vehículo<input required value={form.placa} onChange={(e) => updateField("placa", e.target.value.toUpperCase())} /></label>
                  <label>Fecha y hora del evento<input required type="datetime-local" value={form.fechaEvento} onChange={(e) => updateField("fechaEvento", e.target.value)} /></label>
                  <label className="wide">Ubicación aproximada<input required value={form.ubicacionEvento} onChange={(e) => updateField("ubicacionEvento", e.target.value)} /></label>
                  <label>Tipo de evento<input required value={form.tipoEvento} onChange={(e) => updateField("tipoEvento", e.target.value)} placeholder="Ej. colisión" /></label>
                  <label>Medio de contacto<input required value={form.medioContacto} onChange={(e) => updateField("medioContacto", e.target.value)} placeholder="Correo o teléfono" /></label>
                </div>
              </fieldset>

              {notice && <div className={`notice ${notice.tone}`} role="status">{notice.text}</div>}
              <button className="primary-action" disabled={busy}>
                {busy ? "Registrando…" : "Crear reporte"} <Icon name="arrow" />
              </button>
            </form>
          ) : (
            <section className="panel lookup-panel">
              <div className="section-heading">
                <span className="step">2</span>
                <div><h2>Consulta tu caso</h2><p>Revisa el estado actual y el siguiente paso.</p></div>
              </div>
              <form className="lookup-form" onSubmit={searchCase}>
                <label>Número de caso<input inputMode="numeric" value={caseId} onChange={(e) => setCaseId(e.target.value)} placeholder="Ej. 1001" /></label>
                <button className="primary-action" disabled={busy}>{busy ? "Consultando…" : "Consultar"}</button>
              </form>
              {notice && <div className={`notice ${notice.tone}`} role="status">{notice.text}</div>}
              {result && (
                <article className="case-card">
                  <div><span className="case-label">Caso</span><strong>#{result.id}</strong></div>
                  <span className="status-chip">{estadoLabels[result.estadoActual] ?? result.estadoActual}</span>
                  <dl>
                    <div><dt>Evento</dt><dd>{result.tipoEvento}</dd></div>
                    <div><dt>Fecha</dt><dd>{new Intl.DateTimeFormat("es", { dateStyle: "medium", timeStyle: "short" }).format(new Date(result.fechaEvento))}</dd></div>
                    {result.siguientePaso && <div><dt>Siguiente paso</dt><dd>{(guidanceByState[result.estadoActual]?.title ?? result.siguientePaso.replaceAll("_", " "))}</dd></div>}
                  </dl>
                  <NextStepCard claim={result} />
                  <section className="timeline" aria-labelledby="timeline-title">
                    <div className="timeline-heading">
                      <h3 id="timeline-title">Historial del caso</h3>
                      <span>{timeline?.eventos.length ?? 0} eventos</span>
                    </div>
                    {timeline && timeline.eventos.length > 0 ? (
                      <ol>
                        {timeline.eventos.map((event) => (
                          <li key={event.id}>
                            <span className="timeline-dot" aria-hidden="true" />
                            <div>
                              <strong>{event.tipoEvento.replaceAll("_", " ")}</strong>
                              <time dateTime={event.fecha}>
                                {new Intl.DateTimeFormat("es", { dateStyle: "medium", timeStyle: "short" }).format(new Date(event.fecha))}
                              </time>
                            </div>
                          </li>
                        ))}
                      </ol>
                    ) : (
                      <p className="timeline-empty">Todavía no hay movimientos visibles para este caso.</p>
                    )}
                    {timelineError && (
                      <p className="timeline-error" role="alert">{timelineError}</p>
                    )}
                    {timeline?.siguienteCursor != null && (
                      <button
                        className="timeline-more"
                        type="button"
                        onClick={loadMoreTimeline}
                        disabled={timelineBusy}
                      >
                        {timelineBusy ? "Cargando movimientos…" : "Cargar más movimientos"}
                      </button>
                    )}
                  </section>
                </article>
              )}
            </section>
          )}

          <aside className="support-card">
            <span className="support-icon">!</span>
            <div><h2>Primero, cuida tu seguridad</h2><p>Si hay personas heridas o existe un peligro inmediato, contacta a los servicios de emergencia antes de continuar.</p></div>
          </aside>
        </div>
      </main>

      <footer><span>Seguro Horizonte</span><span>Atención de siniestros vehiculares</span></footer>
    </div>
  );
}

export default App;
