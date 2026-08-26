# Registro de aprobación — S1-DEC-01 y S1-DEC-02

## Decisión

El Product Owner aprueba el 25 de agosto de 2026:

### S1-DEC-01 — Adaptador simulado de pólizas

Se utilizará un adaptador simulado para consultar póliza, cobertura, vehículo y deducible durante Sprint 1, hasta disponer de la API real.

- La interfaz deberá permitir reemplazar el adaptador sin cambiar el dominio ni el contrato público.
- Sólo utilizará datos sintéticos.
- No representa una integración productiva.
- Los errores y resultados deberán respetar el contrato OpenAPI aprobado.

### S1-DEC-02 — Detección provisional de duplicados

Un reporte será señalado como posible duplicado cuando coincidan la placa y la fecha del evento.

- La coincidencia requiere revisión humana.
- No se fusionarán, eliminarán ni descartarán casos automáticamente.
- La respuesta respetará RBAC y no expondrá información de otro caso sin autorización.
- La regla podrá sustituirse mediante control de cambios cuando exista una definición definitiva.

## Impacto

- S1-BE-01 y S1-BE-02 cumplen su Definition of Ready.
- S1-BE-03 ya estaba listo.
- El compromiso completo de Sprint 1 —18 puntos— queda listo para iniciar.
- No se configura infraestructura ni se ejecutan operaciones en GCP.
