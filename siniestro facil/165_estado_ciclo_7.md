# Estado Ciclo 7 — Plataforma Backend Siniestro Fácil

## Estado general

- Avance: **5% — preparación completada; decisiones aprobadas**.
- Rama: `agent/ciclo-7-plataforma-backend`.
- Punto de partida: `main` en `53eed88e476c12ae1fdf70a68cbf72fc4473049e`.
- Backend funcional heredado: **6 sprints completados**.
- Suite heredada: **428 pruebas aprobadas**.
- Alembic heredado: `20260903_04 (head)`.
- Objetivo: industrializar, desplegar y validar el backend en GCP sin ampliar el alcance funcional.

## Alcance propuesto

| Incremento | Resultado esperado | Peso |
|---|---|---:|
| Preparación | Alcance, trazabilidad y decisiones | 5% |
| C7-PLAT-01 | Contenedor reproducible y seguro | 15% |
| C7-PLAT-02 | Cloud Run privado y Cloud SQL | 20% |
| C7-PLAT-03 | Secret Manager e IAM mínimo | 15% |
| C7-PLAT-04 | CI/CD y migración controlada | 20% |
| C7-PLAT-05 | Logs, métricas y alertas | 15% |
| C7-PLAT-06 | Aceptación, evidencias y cierre | 10% |

## Restricciones

- No agregar funcionalidades de negocio.
- No almacenar secretos en GitHub ni dentro de imágenes.
- No permitir acceso público antes de aprobar autenticación perimetral.
- No ejecutar migraciones concurrentes desde instancias de la API.
- No inventar SLO, umbrales, presupuestos ni políticas de escalado.
- No fusionar el PR sin autorización explícita del Product Owner.

## Decisiones aprobadas

- C7-DEC-01 a C7-DEC-06: **aprobadas**.
- Evidencia: `169_registro_aprobacion_c7_decisiones.md`.

## Próximo paso

Validar la línea base del Ciclo 7 y comenzar C7-PLAT-01 con el contenedor reproducible y seguro.
