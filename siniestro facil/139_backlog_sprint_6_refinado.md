# Backlog refinado — Sprint 6 Backend

## Objetivo

Completar el piloto funcional con pagos controlados, auditoría de extremo a extremo e indicadores sustentados por datos disponibles, preservando revisión humana, segregación de funciones y trazabilidad.

## S6-BE-01 — Preparar y autorizar pagos

| Campo | Definición |
|---|---|
| Historias | HU-16, HU-27 |
| Requisitos | RF-18, RF-22, RF-32 |
| Datos | pago, autorizacion, alerta, politica_alerta, evento_linea_tiempo |
| Seguridad | preparador distinto del autorizador; autorización exclusiva del supervisor |

Criterios:

- Permitir que operador, ajustador o supervisor prepare una solicitud de pago dentro de su alcance.
- Permitir únicamente al supervisor autorizarla.
- Impedir que la misma identidad prepare y autorice.
- Bloquear la autorización mientras exista una alerta crítica pendiente de revisión.
- Registrar monto, estado, autorización y eventos auditables.
- Aplicar concurrencia optimista e idempotencia.
- Ejecutar el flujo mediante el adaptador determinístico simulado aprobado, sin transferir dinero real.

## S6-BE-02 — Consultar auditoría integral del caso

| Campo | Definición |
|---|---|
| Historias | HU-16, HU-24, HU-28 |
| Requisitos | RF-18, RF-23, RF-30 |
| Datos | evento_linea_tiempo, identidad_actor, siniestro y referencias del expediente |

Criterios:

- Entregar una línea de tiempo ordenada del expediente.
- Incluir actor, fecha, tipo de evento y detalle permitido.
- Respetar alcance propio, asignado, autorizado o transversal según rol.
- Restringir detalles sensibles y auditar su consulta.
- Mantener una vista única sin duplicar ni modificar los registros fuente.
- Aplicar paginación sin fijar límites no aprobados.

## S6-BE-03 — Exponer indicadores verificables

| Campo | Definición |
|---|---|
| Historias | HU-29 |
| Requisitos | RF-29 |
| Datos | siniestro, asistencia, evento_linea_tiempo y fuentes aprobadas |
| Acceso | supervisor/dirección según matriz RBAC |

Criterios:

- Calcular tiempo hasta primera asistencia cuando los eventos requeridos existan.
- Calcular tiempo hasta decisión cuando exista una decisión trazable.
- No convertir ausencia de datos en cero.
- Identificar indicadores no disponibles por falta de fuente.
- No inventar fórmula para satisfacción, costo operativo ni pérdidas evitadas.
- Conservar definición, período consultado y procedencia de cada resultado.

## Estabilización transversal

- Ejecutar compilación, suite completa y migraciones.
- Validar PostgreSQL con transacciones y rollback.
- Confirmar RBAC, alcance y segregación de funciones.
- Revisar que secretos, tokens y evidencia binaria no aparezcan en respuestas ni logs.
- Mantener tolerancia ante adaptadores externos no disponibles.
- Registrar evidencia reproducible para cada incremento.

## Fuera de alcance sin autorización adicional

- Transferencias monetarias reales.
- Selección o integración de un proveedor de pagos.
- Fórmulas o fuentes sintéticas para indicadores de negocio.
- Umbrales numéricos de autenticación reciente o rate limiting.
- CI/CD, Cloud Run, observabilidad productiva y modelo externo de IA.

## Definition of Ready

| Incremento | Estado | Condición pendiente |
|---|---|---|
| S6-BE-01 | Listo | S6-DEC-01 aprobada; ejecutar línea base |
| S6-BE-02 | Listo | Ejecutar línea base |
| S6-BE-03 | Listo | S6-DEC-02 aprobada; ejecutar línea base |
| Seguridad | Listo | S6-DEC-03 aprobada; ejecutar línea base |


## Decisiones aprobadas

- S6-DEC-01, S6-DEC-02 y S6-DEC-03 aprobadas por el Product Owner.
- Evidencia: `141_registro_aprobacion_s6_decisiones.md`.


## Estado de ejecución

| Incremento | Estado | Evidencia final |
|---|---|---|
| S6-BE-01 | **Completado** | `149_evidencia_final_s6_be_01_postgresql.md` |
| S6-BE-02 | **Completado** | `154_evidencia_final_s6_be_02_postgresql.md` |
| S6-BE-03 | Pendiente | — |
