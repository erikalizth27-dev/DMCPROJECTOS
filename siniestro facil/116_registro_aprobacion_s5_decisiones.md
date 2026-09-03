# Registro de aprobación — Decisiones Sprint 5

## Identificación

- Fecha: 3 de septiembre de 2026.
- Aprobador: Product Owner.
- Rama: `agent/sprint-5-backend`.
- Estado: **APROBADO**.

## S5-DEC-01 — Tratamiento de alertas por severidad

Durante el piloto:

- Crítica: bloquea el pago hasta revisión humana.
- Alta: deriva el caso a investigación.
- Media o baja: aumenta la prioridad.
- Ninguna alerta confirma fraude ni rechaza automáticamente.

Los umbrales definitivos de producción permanecen pendientes.

## S5-DEC-02 — Relaciones entre casos

- Solo se usan coincidencias exactas de valores normalizados disponibles.
- Las coincidencias generan candidatos para revisión humana.
- Los expedientes no se fusionan automáticamente.
- No se infieren ni completan datos ausentes.

## S5-DEC-03 — Adaptador de reglas o modelos

- Se utiliza temporalmente un adaptador determinístico simulado.
- Se conservan versión, entradas y explicación.
- No se integra un modelo externo de IA durante Sprint 5.
- Toda recomendación sensible permanece revisable por una persona.

## Impacto

- S5-BE-01, S5-BE-02 y S5-BE-03 cumplen la Definition of Ready.
- Se habilita la implementación de fundaciones antifraude.
- No se aprueban umbrales monetarios ni una política definitiva de producción.
