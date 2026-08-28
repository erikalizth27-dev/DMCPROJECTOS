# Estado actual — Sprint 1 Backend

## Avance general

**65% completado**.

El Sprint 1 tiene una duración planificada de dos semanas y un compromiso aprobado de 18 puntos.

| Fase | Peso | Estado | Acumulado |
|---|---:|---|---:|
| Preparación, alcance y Definition of Ready | 5% | Completada | 5% |
| Fundaciones de persistencia y pruebas | 10% | Completadas; 63/63 pruebas aprobadas | 15% |
| S1-BE-01 — Registrar siniestro | 30% | Completado; persistencia y auditoría atómicas validadas | 45% |
| S1-BE-02 — Detectar posibles duplicados | 20% | Completado; placa y día validados en Cloud SQL | 65% |
| S1-BE-03 — Consultar vista inicial | 20% | Pendiente | 65% |
| Validación integrada con PostgreSQL | 10% | Pendiente | 65% |
| Evidencias, documentación y cierre | 5% | Pendiente | 65% |

## Compromiso

| Incremento | Estimación | Estado inicial |
|---|---:|---|
| S1-BE-01 | 8 puntos | Listo |
| S1-BE-02 | 5 puntos | Listo |
| S1-BE-03 | 5 puntos | Listo |
| **Total** | **18 puntos** | **Comprometido** |

## Línea base técnica

- Rama: `agent/sprint-1-backend`.
- Punto de partida: `4e38db7`.
- Compilación de `src`, `tests` y `alembic`: correcta.
- Pytest: 53/53 pruebas aprobadas.
- Duración reportada: 0.52 segundos.
- Entorno de validación: Google Cloud Shell, Python 3.12.3.

## Avance de fundaciones

- Siete modelos SQLAlchemy alineados con el esquema `siniestro_facil`.
- Fábrica de sesiones y contexto transaccional con commit/rollback.
- Adaptador en memoria de pólizas conforme a S1-DEC-01.
- Diez pruebas nuevas para búsquedas, vigencia, metadatos y transacciones.

Cloud Shell confirmó compilación correcta y 63/63 pruebas aprobadas en 1.02 s.

## Avance S1-BE-01

- Caso de uso de registro implementado.
- Elegibilidad por póliza/documento, placa y vigencia.
- Reintento idempotente y conflicto por cambio de contenido.
- Endpoint `POST /api/v1/siniestros` integrado con FastAPI.
- Respuestas 201, 409 y 422 alineadas al contrato.
- Doce pruebas nuevas de servicio y API.
- Repositorio PostgreSQL activado mediante `DATABASE_URL`.
- Migración Alembic `20260828_01` aplicada en Cloud SQL.
- Siniestro, evento inicial y respuesta idempotente gobernados por una transacción.
- Manejo de colisiones concurrentes mediante clave idempotente persistente.
- Usuario `siniestro_app` validado con acceso a 24 tablas y privilegios mínimos.
- Suite completa: 77/77 pruebas aprobadas en 0.99 s.

S1-BE-01 queda completado y el avance general alcanza 45%.

## Avance S1-BE-02

- Regla aprobada: coincidencia por placa y día del evento.
- Respuesta `409 POSSIBLE-DUPLICATE` sin identificador del caso previo.
- Revisión humana obligatoria; no existe fusión ni descarte automático.
- Bloqueo transaccional por placa y día para solicitudes concurrentes.
- Revalidación de idempotencia después de adquirir el bloqueo.
- Suite completa: 81/81 pruebas aprobadas en 1.01 s.
- Prueba integrada contra Cloud SQL completada.
- Caso sintético `15` eliminado y ausencia de residuos confirmada.

S1-BE-02 queda completado y el avance general alcanza 65%.

## Próximo incremento

Implementar S1-BE-03: consultar la vista inicial del siniestro con RBAC,
privacidad por alcance, siguiente paso y auditoría de acceso sensible.
