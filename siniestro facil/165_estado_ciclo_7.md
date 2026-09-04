# Estado Ciclo 7 — Plataforma Backend Siniestro Fácil

## Estado general

- Avance: **20% — C7-PLAT-01 completado**.
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

## Línea base validada

- Compilación: aprobada.
- Suite: **428 pruebas aprobadas**.
- Alembic: `20260903_04 (head)`.
- Cloud SQL Proxy: operativo.
- Advertencia Starlette: conocida y no bloqueante.

## Primera entrega C7-PLAT-01

- Contenedor Python 3.12 creado.
- Usuario no privilegiado configurado.
- Puerto Cloud Run y terminación por señales configurados.
- Contexto de construcción protegido con `.dockerignore`.
- Contrato automatizado y validador integral del contenedor añadidos.
- Evidencia: `170_primera_entrega_c7_plat_01.md`.

## Validación final C7-PLAT-01

- Imagen Docker: construida correctamente.
- Usuario: `10001:10001`.
- Secretos embebidos: no detectados.
- Liveness y readiness con Cloud SQL: aprobados.
- Alembic dentro de la imagen: `20260903_04 (head)`.
- Evidencia: `171_evidencia_final_c7_plat_01_cloudshell.md`.
- Estado: **completado**.

## Próximo paso

Iniciar C7-PLAT-02: habilitar servicios requeridos, crear Artifact Registry, publicar una imagen inmutable y preparar Cloud Run privado.
