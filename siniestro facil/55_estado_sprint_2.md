# Estado Sprint 2 — Backend Siniestro Fácil

## Estado general

- Avance: **100% — Sprint 2 cerrado**
- Rama: `agent/sprint-2-backend`
- Punto de partida: `main` después del cierre de Sprint 1 (`bfc1356`)
- Duración de referencia: 2 semanas
- Estado: S2-BE-01, S2-BE-02 y S2-BE-03 completados; integración y cierre aprobados
- Validación inicial: **90/90 pruebas**, Alembic `20260828_02 (head)`
- Evidencia: `57_evidencia_linea_base_sprint_2_cloudshell.md`

## Objetivo

Entregar cobertura, transiciones de estado y gestión de evidencia inmutable, manteniendo trazabilidad, idempotencia, concurrencia optimista y privacidad por rol.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones abiertas | 5% | 5% |
| Fundaciones | Contratos, modelos y pruebas base | 10% | 15% |
| S2-BE-01 | Verificación de cobertura y deducible | 20% | 35% |
| S2-BE-02 | Transiciones de estado auditables | 25% | 60% |
| S2-BE-03 | Evidencia inmutable y metadatos | 25% | 85% |
| Integración | PostgreSQL, almacenamiento y pruebas integrales | 10% | 95% |
| Cierre | Evidencias, acta y PR listo para revisión | 5% | 100% |

## Incrementos propuestos

### S2-BE-01 — Cobertura y deducible

- Consultar cobertura aplicable y deducible.
- Mantener temporalmente el adaptador simulado si la API real aún no existe.
- Registrar el resultado en la línea de tiempo.
- No producir un rechazo definitivo sin decisión humana.

### S2-BE-02 — Transiciones de estado

- Exigir rol autorizado, motivo y versión conocida del siniestro.
- Aplicar la máquina de estados aprobada.
- Incrementar `siniestro.version` atómicamente.
- Responder HTTP 409 ante versión desactualizada.
- Registrar cada transición en auditoría.

### S2-BE-03 — Evidencia inmutable

- Registrar evidencia vinculada al siniestro.
- Conservar hash, metadatos, fecha, fuente y referencia al objeto.
- Preservar el original y diferenciar versiones derivadas.
- Aplicar idempotencia, RBAC y auditoría de accesos sensibles.
- Integrar Cloud Storage solamente después de aprobar bucket, región y retención.

## Avance de S2-BE-02

- Caso de uso de transición implementado.
- Endpoint `POST /api/v1/siniestros/{siniestroId}/estado` implementado.
- RBAC, alcance privado, versión esperada y auditoría atómica incorporados.
- Ocho pruebas unitarias y API añadidas.
- Validación automática: **98/98 pruebas aprobadas**.
- Evidencia: `58_evidencia_pruebas_s2_be_02_cloudshell.md`.
- Validación PostgreSQL: transición, versión, auditoría, conflicto 409 y rollback aprobados.
- Evidencia: `59_evidencia_s2_be_02_postgresql.md`.
- Estado del incremento: **completado**.

## Avance de S2-BE-01

- `S2-DEC-01` aprobada y registrada.
- Caso de uso de verificación de cobertura implementado.
- Adaptador simulado reutilizado sin integración externa.
- Deducible, versión y resultado de validación incluidos.
- Cobertura no activa deriva a revisión humana, nunca a rechazo automático.
- Seis pruebas unitarias añadidas; **104/104 pruebas aprobadas**.
- Evidencia: `61_evidencia_primera_entrega_s2_be_01.md`.
- Repositorio PostgreSQL, persistencia, auditoría atómica y endpoint implementados.
- Seis pruebas API/repositorio adicionales; **110/110 pruebas aprobadas**.
- Evidencia: `62_evidencia_segunda_entrega_s2_be_01.md`.
- Validación PostgreSQL completada: cobertura, deducible, transición, versión, auditoría, conflicto 409 y rollback aprobados.
- Evidencia: `63_evidencia_s2_be_01_postgresql.md`.
- Estado del incremento: **completado**.

## Avance de S2-BE-03

- Configuración de almacenamiento aprobada y codificada.
- SHA-256 de contenido original implementado.
- Claves únicas bajo `siniestros/{id}/originales/`.
- URI `gs://` y generación registradas.
- Sobrescritura de originales prohibida.
- Siete pruebas nuevas; **117/117 pruebas aprobadas**.
- Evidencia: `65_evidencia_primera_entrega_s2_be_03.md`.
- Bucket real creado y validado con acceso uniforme, prevención pública y versionado.
- Evidencia: `66_evidencia_bucket_s2_be_03.md`.
- Cloud Storage validado con dos generaciones, SHA-256 y limpieza total.
- Evidencia: `67_evidencia_cloud_storage_s2_be_03.md`.
- Modelo y repositorio PostgreSQL implementados.
- Idempotencia persistente y migración `20260901_01` añadidas.
- RBAC, privacidad, evidencia derivada y auditoría atómica implementados.
- Endpoint `POST /api/v1/siniestros/{id}/evidencias` implementado.
- Trece pruebas nuevas; **130/130 pruebas aprobadas**.
- Evidencia: `68_evidencia_130_pruebas_s2_be_03.md`.
- Migración `20260901_01` aplicada; permisos temporales revocados.
- Regresión posterior: **130/130 pruebas aprobadas**.
- Evidencia: `69_evidencia_migracion_regresion_s2_be_03.md`.
- Validación PostgreSQL final completada: persistencia de URI y SHA-256, auditoría atómica, repetición idempotente, conflicto 409, inmutabilidad y rollback aprobados.
- Limpieza comprobada sin registros sintéticos residuales.
- Evidencia: `70_evidencia_final_s2_be_03_postgresql.md`.
- Estado del incremento: **completado**.

## Decisiones pendientes para Definition of Ready

- **S2-DEC-01 — APROBADA:** continuar temporalmente con el adaptador simulado de pólizas durante Sprint 2. Evidencia: `60_registro_aprobacion_s2_dec_01.md`.
- **S2-DEC-02 — APROBADA:** bucket `project-77c17016-86bc-4fc4-a97-siniestro-evidencias` en `us-central1`, acceso uniforme, versionado, sin acceso público y sin retention lock. Evidencia: `64_registro_aprobacion_s2_dec_02.md`.

## Línea base de calidad

La validación inicial del Sprint 2 aprobó **90/90 pruebas** y confirmó Alembic en `20260828_02 (head)`. Sprint 2 debe preservar esas pruebas y añadir pruebas unitarias, API, persistencia e integración para cada incremento.

## Cierre integral

- Suite integral: **130/130 pruebas aprobadas**.
- Alembic: `20260901_01 (head)`.
- Bucket: región, acceso uniforme, prevención pública y versionado validados.
- Evidencia integral: `71_evidencia_validacion_integral_sprint_2.md`.
- Matriz de cierre: `72_matriz_cierre_trazabilidad_sprint_2.md`.
- Acta: `73_acta_cierre_sprint_2.md`.
- Estado final: **100%**.

## Restricciones

- No se ejecutan migraciones ni cambios en GCP sin validación previa y pasos explícitos en Cloud Shell.
- No se almacenan secretos en Git.
- El PR de Sprint 2 no se fusiona sin autorización explícita del Product Owner.
