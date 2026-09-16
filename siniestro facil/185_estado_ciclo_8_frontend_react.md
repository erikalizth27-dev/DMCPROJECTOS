# Estado Ciclo 8 — Frontend React

Fecha de cierre: 2026-09-16  
Estado: completado

## Objetivo

Construir y desplegar el frontend de Siniestro Fácil en React, con autenticación, trazabilidad a las historias de usuario y comunicación segura con el backend privado.

## Alcance entregado

- Interfaz responsive para teléfono y escritorio.
- Autenticación con Identity Platform.
- Sesión en memoria y renovación automática.
- BFF público con validación JWT y CORS restringido.
- Creación de reportes con póliza o documento.
- Consulta autorizada del estado, siguiente paso e historial.
- Paginación de la línea de tiempo.
- Carga directa de JPG, PNG y PDF al bucket privado.
- Verificación del archivo y registro del SHA-256.
- Actualización automática del historial tras adjuntar evidencia.
- Prueba E2E autenticada y no destructiva.

## Trazabilidad

| Elemento | Fuente | Estado |
|---|---|---|
| Reportar desde teléfono | HU-01 | Completado |
| Datos mínimos | HU-03 | Completado |
| Adjuntar evidencia | HU-05 | Completado |
| Estado y siguiente paso | HU-06 | Completado |
| Contratos API | `12_api_backend_openapi.yaml` | Validado |
| Autenticación y autorización | `13_seguridad_rbac.md` | Validado |

## Producción validada

| Componente | Revisión | Digest |
|---|---|---|
| Frontend | `siniestro-facil-frontend-prod-00009-kl2` | `sha256:84eb29c9705b089460a527d833041e053cd27cda105dfba1752aadd7ae2558ac` |
| BFF | `siniestro-facil-bff-prod-00004-mrc` | `sha256:b9532ca0662d9feabab50a04819895b041251c85cea2cdccee46c7a032f1447f` |
| Backend | `siniestro-facil-backend-prod-00007-znt` | `sha256:e352217aba2f04d9889e9312c329daef284e8fae929fbcd51c3819bcc4fa0b27` |

Los tres componentes sirvieron 100 % del tráfico durante la validación.

## Evidencia integral

El caso productivo de prueba `#14` confirmó:

1. inicio de sesión;
2. creación del reporte;
3. consulta autorizada;
4. presentación del estado y siguiente paso;
5. carga de una evidencia PNG;
6. registro de metadatos en PostgreSQL;
7. evento `Evidencia Registrada` visible en el historial.

La prueba Playwright posterior confirmó autenticación, consulta e historial con resultado `1 passed`.

## Calidad

- `npm audit`: 0 vulnerabilidades.
- `npm run typecheck`: aprobado.
- `npm run build`: aprobado.
- Prueba E2E autenticada: aprobada.
- No se almacenan credenciales ni tokens en el repositorio.
- Bucket de evidencias privado.
- Backend privado; acceso mediante el BFF.

## Cambios de estabilización

- PR #27: URL base reproducible de Cloud Build.
- PR #28: seed sintético compatible con el esquema vigente.
- PR #29: CORS para ambos dominios productivos.
- PR #30: corrección del registro de evidencias.
- PR #31: actualización automática del historial.
- PR #32: prueba E2E autenticada.

## Estado final

El alcance funcional del Ciclo 8 está completado y validado en producción. No quedan pendientes bloqueantes del frontend. Las futuras mejoras deben gestionarse como nuevo alcance.
