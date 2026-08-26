# Política obligatoria de migraciones PostgreSQL

## Estado

**APROBADA COMO LÍNEA BASE TÉCNICA DEL SPRINT 0.** Alembic es el mecanismo
obligatorio para todo cambio incremental posterior al esquema inicial.

## Alcance

Aplica a cambios en:

- tablas, columnas y tipos;
- claves primarias y foráneas;
- constraints e índices;
- datos de catálogo requeridos por una versión;
- funciones, triggers y vistas del esquema `siniestro_facil`.

## Reglas obligatorias

1. No modificar `postgresql/01_schema.sql` para desplegar cambios incrementales
   sobre una base existente.
2. Cada cambio crea una revisión nueva en `backend/alembic/versions/`.
3. No editar una revisión que ya fue aplicada a Cloud SQL.
4. Cada revisión declara `revision`, `down_revision`, `upgrade` y `downgrade`.
5. `upgrade` debe ser transaccional e idempotente cuando pueda coexistir con un
   cambio manual previamente controlado.
6. `downgrade` debe documentar pérdida potencial de datos y no se ejecuta en una
   base compartida sin respaldo y autorización explícita.
7. Los nombres de constraints e índices deben ser estables y explícitos.
8. Toda revisión incluye pruebas automatizadas y una validación posterior.
9. La contraseña y `DATABASE_URL` nunca se almacenan en GitHub.
10. La ejecución en Cloud SQL registra revisión, resultado y evidencia sin
    secretos.

## Secuencia de desarrollo

1. Actualizar SPEC y modelo lógico.
2. Crear revisión Alembic.
3. Crear o actualizar prueba estructural y de comportamiento.
4. Ejecutar compilación y suite local.
5. Revisar SQL generado o contenido de la revisión.
6. Aplicar en ambiente autorizado mediante Cloud SQL Proxy.
7. Ejecutar validación posterior.
8. Registrar evidencia y actualizar trazabilidad.

## Comandos de control

```bash
alembic history
alembic current
alembic upgrade head
```

`alembic downgrade` no forma parte del procedimiento normal de despliegue.

## Línea base actual

| Elemento | Valor |
|---|---|
| Esquema inicial | PR #1 fusionado en `main` |
| Primera revisión incremental | `20260825_01` |
| Estado Cloud SQL | Aplicada y validada |
| Tabla de versión | `siniestro_facil.alembic_version` |

## Criterios de rechazo

Un cambio de datos no está listo para revisión si:

- sólo modifica el DDL inicial;
- no incluye revisión Alembic;
- reutiliza o reescribe una revisión aplicada;
- carece de prueba o validación posterior;
- contiene credenciales;
- ejecuta una operación destructiva sin advertencia, respaldo y autorización.
