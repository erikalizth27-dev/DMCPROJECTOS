# Backlog refinado — Sprint 4 Backend

## Objetivo

Implementar el tramo verificable desde la programación de inspección hasta la decisión formal sobre el presupuesto, conservando identidad, alcance, versión y auditoría.

## S4-BE-01 — Programar y consultar inspección

| Campo | Definición |
|---|---|
| Historias | HU-17, HU-18 |
| Requisitos | RF-11, RF-18 |
| Caso de uso | CU-05 |
| Datos | inspeccion, siniestro, asignacion_siniestro, evento_linea_tiempo |

Criterios:

- Permitir a operador o ajustador autorizado programar la inspección.
- Vincularla con un siniestro visible para el actor.
- Pasar el caso a `inspeccion_programada` mediante transición válida.
- Aplicar versión optimista y auditoría atómica.
- Consultar la inspección sin revelar casos fuera de alcance.

## S4-BE-02 — Registrar orden, diagnóstico y presupuesto

| Campo | Definición |
|---|---|
| Historias | HU-14, HU-19 |
| Requisitos | RF-15, RF-18 |
| Caso de uso | CU-05 |
| Datos | inspeccion, presupuesto, proveedor, siniestro, evento_linea_tiempo |

Criterios:

- Registrar la recepción de la orden por un taller autorizado.
- Registrar presupuesto y diagnóstico.
- Vincularlos con inspección, taller y siniestro.
- Registrar la vigencia conforme a S4-DEC-01.
- Pasar el caso a `presupuesto_recibido`.
- Aplicar idempotencia, RBAC, versión y auditoría atómica.

## S4-BE-03 — Decidir presupuesto y registrar cambios

| Campo | Definición |
|---|---|
| Historias | HU-13, HU-20 |
| Requisitos | RF-14, RF-16, RF-18 |
| Casos de uso | CU-05, CU-06 |
| Datos | presupuesto, autorizacion, cambio_presupuesto, evento_linea_tiempo |

Criterios:

- Registrar formalmente aprobación, observación o rechazo.
- Registrar actor, fecha, decisión y justificación disponible.
- Aplicar los roles definidos en S4-DEC-02.
- No inventar umbrales monetarios.
- Registrar observaciones, repuestos alternativos y ampliaciones.
- Conservar el presupuesto original y el historial de cambios.
- Aplicar idempotencia, concurrencia y auditoría atómica.

## Fuera de alcance

- Ejecución completa de la reparación.
- Pagos, indemnización y cierre.
- Integración productiva con sistemas de talleres.
- Fraude y alertas.
- CI/CD, Cloud Run y observabilidad productiva.

## Definition of Ready

| Incremento | Estado | Condición pendiente |
|---|---|---|
| S4-BE-01 | Listo | Especificaciones y reglas existentes son suficientes |
| S4-BE-02 | Listo | S4-DEC-01 aprobada |
| S4-BE-03 | Listo | S4-DEC-02 y S4-DEC-03 aprobadas |
