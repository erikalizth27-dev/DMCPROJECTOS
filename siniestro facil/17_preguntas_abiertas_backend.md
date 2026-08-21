# Preguntas abiertas para completar el planning backend

## Bloqueantes para convertir el backlog en sprint-ready

1. ¿Las decisiones marcadas `[SIMULADO]` en `cierre_de_brechas.md` quedan aprobadas como reglas del piloto?
2. ¿Qué debe ocurrir después de rechazar cobertura: cierre definitivo, apelación o reapertura por supervisor?
3. ¿Cuál es la vigencia predeterminada de un presupuesto si el taller no envía fechas?
4. ¿Quiénes pueden autorizar pagos: operador, ajustador, supervisor o una combinación por monto?
5. ¿El taller o corredor puede crear un siniestro en el piloto, o sólo reportar información sobre uno existente?
6. ¿Qué confirma la entrega del vehículo y permite pasar de `listo_para_entrega` a `cerrado`?
7. ¿Cuál es la capacidad del equipo, duración de sprint y fecha objetivo del piloto?

## Necesarias antes de integrar servicios reales

8. ¿Se aprueba Cloud Run para el backend del piloto o existe una obligación de utilizar GKE?
9. ¿Se utilizará Identity Platform, Identity-Aware Proxy u otro proveedor compatible para usuarios finales, y qué actores tendrán cuentas propias?
10. ¿Qué bucket, región y política de retención de Cloud Storage se usarán para evidencias?
11. ¿Qué proveedores externos se usarán para mensajería, mapas, talleres y pagos, aunque su integración se ejecute desde GCP?
12. ¿Existen APIs actuales para consultar póliza, cobertura, vehículo y deducible?
13. ¿Qué información puede ver cada rol en la vista única del caso?

## Necesarias antes de producción

14. ¿Se aprueban los SLA simulados del piloto?
15. ¿Se aprueban los umbrales y severidades antifraude simulados?
16. ¿Qué normativa, país y política corporativa gobiernan datos personales y retención?
17. ¿Cuál es el volumen máximo esperado para el piloto y el crecimiento proyectado?
18. ¿Cuánto tiempo deben conservarse logs técnicos, auditorías y claves de idempotencia?
19. ¿Qué regiones GCP están autorizadas para cómputo, datos, backups y evidencias?


## Registro de respuesta

Cada respuesta debe indicar responsable, fecha, decisión, documentos afectados y si reemplaza una decisión simulada.
