# Decisiones pendientes — Ciclo 7 Plataforma

## C7-DEC-01 — Servicio y región

**Propuesta:** desplegar el piloto como `siniestro-facil-backend-piloto` en `us-central1`, junto a Cloud SQL y los recursos asíncronos existentes.

**Pendiente:** aprobación del Product Owner.

## C7-DEC-02 — Exposición y autenticación

**Propuesta:** mantener Cloud Run con `--no-allow-unauthenticated` y usar invocación autenticada durante el piloto. La selección de autenticación para usuarios finales queda fuera hasta contar con requisitos aprobados.

**Pendiente:** aprobación del Product Owner.

## C7-DEC-03 — Ambientes

**Propuesta:** crear inicialmente solo el ambiente piloto. No duplicar infraestructura para desarrollo o producción hasta aprobar costos, aislamiento y promoción.

**Pendiente:** aprobación del Product Owner.

## C7-DEC-04 — Identidades y secretos

**Propuesta:** usar cuentas separadas para runtime y migración; almacenar `DATABASE_URL` y demás configuración sensible en Secret Manager; asignar permisos mínimos sobre Cloud SQL, Storage, Pub/Sub y Cloud Tasks.

**Pendiente:** aprobación del Product Owner.

## C7-DEC-05 — Construcción, despliegue y migraciones

**Propuesta:** usar Artifact Registry y Cloud Build. El pipeline ejecutará pruebas, construirá una imagen inmutable, ejecutará Alembic mediante una etapa o job exclusivo y desplegará Cloud Run tras completar la migración.

**Pendiente:** aprobación del Product Owner.

## C7-DEC-06 — Escalado y observabilidad

**Propuesta:** no inventar valores de capacidad, SLO o alerta. Empezar con métricas y logs administrados; aprobar por separado recursos, instancias mínimas/máximas, concurrencia, condiciones y destinatarios de alertas.

**Pendiente:** aprobación del Product Owner.

## Regla de ejecución

No se crearán recursos ni se desplegará el servicio hasta aprobar las decisiones que cambian seguridad, costo o exposición.
