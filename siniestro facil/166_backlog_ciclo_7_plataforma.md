# Backlog — Ciclo 7 Plataforma Backend

## Objetivo

Preparar el backend Siniestro Fácil para ejecución controlada en GCP, conservando seguridad, trazabilidad, reproducibilidad y las decisiones funcionales aprobadas en los seis sprints.

## C7-PLAT-01 — Contenedor seguro

- Crear `Dockerfile` y `.dockerignore`.
- Ejecutar con usuario sin privilegios.
- Escuchar en la variable `PORT`.
- Excluir `.env`, credenciales, cachés, pruebas y artefactos locales.
- Validar `/health/live`, `/health/ready` y terminación ordenada.
- Generar evidencia reproducible de compilación y ejecución.

## C7-PLAT-02 — Despliegue privado

- Crear repositorio Docker en Artifact Registry.
- Construir y publicar una imagen identificada por commit.
- Desplegar en Cloud Run sin acceso anónimo.
- Conectar Cloud SQL mediante el conector administrado.
- Configurar límites y escalado únicamente después de aprobación.
- Ejecutar smoke tests autenticados y documentar el resultado.

## C7-PLAT-03 — Secretos e identidad

- Crear una cuenta de servicio exclusiva para el backend.
- Aplicar privilegio mínimo por recurso.
- Guardar configuración sensible en Secret Manager.
- Mantener separadas las identidades de runtime y migración.
- Verificar que secretos no aparezcan en imagen, respuestas o logs.

## C7-PLAT-04 — CI/CD y migraciones

- Ejecutar compilación y suite completa en cada cambio.
- Verificar estructura e historial Alembic.
- Construir y escanear la imagen.
- Ejecutar migraciones una sola vez mediante un job o etapa controlada.
- Desplegar solamente después de pruebas y migración aprobadas.
- Conservar aprobación manual para el ambiente piloto mientras no exista otra decisión.

## C7-PLAT-05 — Observabilidad

- Emitir logs estructurados con `correlationId`.
- Redactar datos personales, secretos y detalles sensibles.
- Recopilar métricas técnicas de Cloud Run, Cloud SQL, Pub/Sub y Cloud Tasks.
- Crear alertas solo con condiciones y destinatarios aprobados.
- Documentar tableros, consultas y procedimiento básico de diagnóstico.

## C7-PLAT-06 — Aceptación y cierre

- Validar salud, autenticación, RBAC, alcance e idempotencia.
- Recorrer los flujos de los Sprints 1–6 con datos sintéticos.
- Validar Pub/Sub, Cloud Tasks, Cloud Storage y Cloud SQL.
- Confirmar rollback o limpieza de los datos de prueba.
- Registrar evidencias, matriz final, runbook y acta de cierre.

## Fuera de alcance

- Nuevas funciones de negocio.
- Transferencias monetarias reales.
- Modelo externo de IA.
- Acceso público sin autenticación aprobada.
- Valores inventados de SLO, rate limiting, escalado o retención.

## Definition of Ready

| Incremento | Estado | Condición |
|---|---|---|
| C7-PLAT-01 | Parcial | Aprobar runtime y parámetros del contenedor |
| C7-PLAT-02 | Pendiente | Aprobar región, servicio y acceso |
| C7-PLAT-03 | Pendiente | Aprobar IAM y nombres de secretos |
| C7-PLAT-04 | Pendiente | Aprobar mecanismo CI/CD y estrategia de migración |
| C7-PLAT-05 | Pendiente | Definir destinatarios y umbrales |
| C7-PLAT-06 | Pendiente | Completar incrementos anteriores |
