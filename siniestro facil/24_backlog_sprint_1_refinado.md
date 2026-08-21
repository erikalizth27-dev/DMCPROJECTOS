# Backlog refinado — Sprint 1 Backend

## Objetivo propuesto

Permitir registrar un siniestro elegible de forma idempotente, detectar posibles duplicados y consultar una vista inicial del caso respetando el alcance del usuario.

## Duración

- 2 semanas.
- La capacidad definitiva se confirma en la planificación con el equipo.
- Los tamaños son relativos y no equivalen todavía a días ni puntos de velocidad.

## Alcance comprometible

### S1-BE-01 — Registrar siniestro con datos mínimos

| Campo | Definición |
|---|---|
| Historias | HU-01, HU-03, HU-08 |
| Prioridad | Obligatoria |
| Tamaño | L |
| Endpoint | `POST /api/v1/siniestros` |
| Tablas | asegurado, reportante, poliza, vehiculo, siniestro, evento_linea_tiempo |
| Dependencias | Modelo físico disponible; consulta de pólizas real o adaptador simulado |

Actividades:

- Validar `numeroPoliza` o `numeroDocumento`.
- Validar placa, fecha, ubicación, tipo de evento y contacto.
- Verificar alcance vehicular del piloto.
- Aplicar `Idempotency-Key` y huella del contenido.
- Crear el caso en estado `reportado`.
- Registrar el evento inicial en la misma transacción.
- Responder HTTP 201, 409 o 422 según el contrato.

Pruebas mínimas:

- Creación válida por póliza.
- Creación válida por documento.
- Datos mínimos incompletos.
- Caso fuera del alcance.
- Reintento con igual clave e igual contenido.
- Igual clave con contenido diferente.
- Rollback si falla el evento de auditoría.

### S1-BE-02 — Detectar posible duplicado

| Campo | Definición |
|---|---|
| Historia | HU-10 |
| Prioridad | Obligatoria |
| Tamaño | M |
| Endpoint | `POST /api/v1/siniestros` |
| Tablas | siniestro, vehiculo, poliza |
| Regla provisional | Misma placa y mismo día del evento |

Actividades:

- Buscar coincidencias antes de crear el expediente.
- No fusionar ni descartar automáticamente.
- Devolver HTTP 409 con código de negocio y referencia permitida por el rol.
- Permitir una decisión posterior del operador, fuera de este incremento.

Pruebas mínimas:

- Coincidencia exacta de placa y día.
- Misma placa en día diferente.
- Placa diferente el mismo día.
- Dos solicitudes concurrentes.
- Respuesta sin exposición de información no autorizada.

### S1-BE-03 — Consultar vista inicial del siniestro

| Campo | Definición |
|---|---|
| Historias | HU-06, HU-28 |
| Prioridad | Obligatoria |
| Tamaño | M |
| Endpoint | `GET /api/v1/siniestros/{siniestroId}` |
| Tablas | siniestro, poliza, vehiculo, cobertura, reportante |
| Dependencia | Principal autenticado proporcionado por adaptador temporal |

Actividades:

- Consultar caso por identificador.
- Aplicar autorización por rol y alcance.
- Ocultar información no permitida al asegurado.
- Devolver estado actual y siguiente paso.
- Registrar consulta sensible cuando corresponda.
- No distinguir externamente entre recurso inexistente y recurso no visible.

Pruebas mínimas:

- Asegurado consulta su caso.
- Asegurado intenta consultar otro caso.
- Operador consulta caso asignado.
- Taller sin orden válida.
- Supervisor consulta transversal auditada.
- Caso inexistente.

### S1-BE-04 — Reporte por tercero autorizado

| Campo | Definición |
|---|---|
| Historia | HU-04 |
| Prioridad | Condicional |
| Tamaño | M |
| Endpoint | `POST /api/v1/siniestros` |
| Tablas | reportante, asegurado, siniestro |
| Bloqueo | Aprobación formal de la definición de tercero autorizado |

Actividades:

- Registrar reportante diferente del asegurado.
- Conservar contacto y relación declarada cuando el modelo sea ampliado.
- Impedir autorizaciones de pago o cobertura por el solo hecho de reportar.
- Auditar el canal y el actor que realizó el reporte.

No se compromete hasta resolver el atributo para la relación declarada o decidir documentarla fuera de la tabla `reportante`.

## Alcance adicional si existe capacidad

### S1-BE-05 — Transición inicial de estado

- Historia relacionada: HU-08.
- Tamaño: M.
- Endpoint: `POST /api/v1/siniestros/{siniestroId}/estado`.
- Estados iniciales: `reportado` → `validando_cobertura` o `rechazado`.
- Requiere versión conocida, motivo, RBAC y confirmación humana para rechazo.

### S1-BE-06 — Auditoría de comandos y consultas

- Historias relacionadas: HU-16, HU-28.
- Tamaño: M.
- Registra actor, acción, fecha, recurso, resultado y `correlationId`.
- No registra tokens, documentos completos, contraseñas ni evidencia binaria.

## Orden recomendado

1. S1-BE-01.
2. S1-BE-02.
3. S1-BE-03.
4. S1-BE-04 únicamente si se cierra su bloqueo.
5. S1-BE-05 y S1-BE-06 según capacidad demostrada.

## Definition of Ready — evaluación actual

| Incremento | Estado | Razón |
|---|---|---|
| S1-BE-01 | Casi listo | Falta confirmar adaptador de pólizas |
| S1-BE-02 | Condicional | Regla de deduplicación todavía provisional |
| S1-BE-03 | Condicional | Falta cerrar detalle visible por rol e identidad temporal |
| S1-BE-04 | Bloqueado | Falta decisión sobre relación declarada del tercero |
| S1-BE-05 | Casi listo | Falta definir control de versión persistido |
| S1-BE-06 | Casi listo | Falta aprobar retención de auditoría |

## Criterio de éxito del sprint

El sprint se considera exitoso si S1-BE-01, S1-BE-02 y S1-BE-03 cumplen sus criterios, las pruebas pasan contra PostgreSQL y no se amplía alcance con decisiones todavía no aprobadas.

