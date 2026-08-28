# Backlog refinado Sprint 2 — Backend Siniestro Fácil

## Objetivo del sprint

Completar la segunda etapa funcional del piloto: cobertura, evolución controlada del caso y evidencia inmutable.

## Alcance comprometible

| ID | Incremento | Historias / requisitos | Estimación inicial | DoR |
|---|---|---|---:|---|
| S2-BE-01 | Verificar cobertura y deducible | HU-09; RF-05, RF-18, RF-32 | 5 puntos | Condicionado por S2-DEC-01 |
| S2-BE-02 | Cambiar estado con concurrencia y auditoría | RF-09, RF-10, RF-18; regla transversal DM-02 | 8 puntos | Listo |
| S2-BE-03 | Registrar evidencia original e inmutable | HU-05; RF-07, RF-08, RF-18, RF-23 | 8 puntos | Condicionado por S2-DEC-02 |

Estimación inicial total: **21 puntos**. El compromiso definitivo se registra después de resolver las dos decisiones pendientes.

## Orden de ejecución

1. Validar la línea base de 90 pruebas desde la rama nueva.
2. Implementar contratos y modelos compartidos.
3. Implementar S2-BE-02, que no depende de proveedores externos.
4. Implementar S2-BE-01 con el proveedor de pólizas aprobado.
5. Implementar S2-BE-03 primero con persistencia de metadatos y luego con Cloud Storage aprobado.
6. Ejecutar pruebas integrales, migraciones controladas y limpieza de datos sintéticos.
7. Registrar evidencia, actualizar trazabilidad, crear acta y abrir PR.

## Criterios de salida

- Todas las pruebas previas continúan aprobadas.
- Cada comando modificador aplica idempotencia o concurrencia según corresponda.
- No existe transición fuera de la máquina de estados.
- Toda decisión de cobertura sensible y toda transición quedan auditadas.
- El original de una evidencia no se sobrescribe.
- Los accesos sensibles respetan RBAC y quedan auditados.
- Las migraciones Alembic llegan a un único `head`.
- La validación real contra PostgreSQL y, cuando se autorice, Cloud Storage no deja datos sintéticos residuales.
- Evidencia final reproducible desde Cloud Shell.
- PR listo para revisión, sin fusión automática.

## Fuera de alcance de Sprint 2

- Asistencia y proveedores con Pub/Sub (Sprint 3).
- Inspección, presupuestos y autorizaciones (Sprint 4).
- Fraude y revisión humana especializada (Sprint 5).
- Pagos, indicadores y estabilización final (Sprint 6).
- CI/CD, Cloud Run y observabilidad, que permanecen diferidos hasta autorización.
