# Preguntas abiertas para completar el planning backend

## Decisiones recomendadas registradas

Las respuestas propuestas a las siete preguntas iniciales están en `19_decisiones_recomendadas_piloto.md` y ya fueron propagadas a las especificaciones backend. Permanecen como línea base recomendada hasta que el Product Owner las apruebe explícitamente.

## Necesarias antes de integrar servicios reales

1. ¿Se aprueba Cloud Run para el backend del piloto o existe una obligación de utilizar GKE?
2. ¿Se utilizará Identity Platform, Identity-Aware Proxy u otro proveedor compatible para usuarios finales, y qué actores tendrán cuentas propias?
3. ¿Qué bucket, región y política de retención de Cloud Storage se usarán para evidencias?
4. ¿Qué proveedores externos se usarán para mensajería, mapas, talleres y pagos, aunque su integración se ejecute desde GCP?
5. ¿Existen APIs actuales para consultar póliza, cobertura, vehículo y deducible?
6. **RESUELTA PARCIALMENTE:** en alertas, operador/ajustador ven resumen e investigador/supervisor ven detalle. La vista única general conserva definición de campos pendiente.

## Decisiones aprobadas el 25 de agosto de 2026

- AR-01: autorización para solicitar asistencia por alcance.
- AR-02: preparación y autorización de pagos como comandos separados.
- AR-03: alertas con resumen operativo y detalle restringido.

## Necesarias antes de producción

7. ¿Se aprueban los SLA simulados del piloto?
8. ¿Se aprueban los umbrales y severidades antifraude simulados?
9. ¿Qué normativa, país y política corporativa gobiernan datos personales y retención?
10. ¿Cuál es el volumen máximo esperado para el piloto y el crecimiento proyectado?
11. ¿Cuánto tiempo deben conservarse logs técnicos, auditorías y claves de idempotencia?
12. ¿Qué regiones GCP están autorizadas para cómputo, datos, backups y evidencias?



## Registro de respuesta

Cada respuesta debe indicar responsable, fecha, decisión, documentos afectados y si reemplaza una decisión simulada.
