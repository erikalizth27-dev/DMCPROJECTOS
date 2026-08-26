# Estado actual — Sprint 1 Backend

## Avance general

**12% completado**.

El Sprint 1 tiene una duración planificada de dos semanas y un compromiso aprobado de 18 puntos.

| Fase | Peso | Estado | Acumulado |
|---|---:|---|---:|
| Preparación, alcance y Definition of Ready | 5% | Completada | 5% |
| Fundaciones de persistencia y pruebas | 10% | Implementadas; pendientes de validación en Cloud Shell | 12% |
| S1-BE-01 — Registrar siniestro | 30% | Pendiente | 5% |
| S1-BE-02 — Detectar posibles duplicados | 20% | Pendiente | 5% |
| S1-BE-03 — Consultar vista inicial | 20% | Pendiente | 5% |
| Validación integrada con PostgreSQL | 10% | Pendiente | 5% |
| Evidencias, documentación y cierre | 5% | Pendiente | 5% |

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

El bloque alcanzará 15% cuando Cloud Shell confirme compilación y 63/63 pruebas.

## Próximo incremento

Validar las fundaciones en Cloud Shell y comenzar S1-BE-01.
