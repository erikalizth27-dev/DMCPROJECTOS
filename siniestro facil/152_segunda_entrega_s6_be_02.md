# Segunda entrega S6-BE-02 — PostgreSQL

## Alcance implementado

- Repositorio PostgreSQL para consultar `evento_linea_tiempo`.
- Identidad persistida validada contra subject, tenant, tipo de actor y rol.
- Alcance del asegurado por póliza propia.
- Alcance de operador, ajustador e investigador mediante asignación activa.
- Acceso transversal exclusivo del supervisor.
- Denegación privada para taller u otros alcances no demostrables.
- Orden estable por `id_evento`.
- Paginación por cursor, recuperando un registro adicional para determinar continuidad.
- Clasificación de eventos sensibles de fraude, relaciones y consultas sensibles.
- Registro persistente de los accesos ampliados a eventos sensibles.
- Endpoint conectado al repositorio cuando `DATABASE_URL` está configurada.

## Pruebas añadidas

Se añadieron **7 pruebas estructurales** del repositorio PostgreSQL. Total esperado: **405 pruebas**.

## Migración

No se requiere migración: se reutilizan `evento_linea_tiempo`, `identidad_actor`, `asignacion_siniestro`, `poliza` y `siniestro`.

## Pendiente

- Ejecutar compilación y regresión completa.
- Ejecutar validación PostgreSQL real con rollback y comprobación de residuos.
