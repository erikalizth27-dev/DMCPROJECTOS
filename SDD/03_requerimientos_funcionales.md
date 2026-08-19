# 03 — Requerimientos Funcionales
## Proyecto: Crédito Ágil 360

> Cada requerimiento funcional (RF) agrupa una o más historias de usuario y cita su fuente en las entrevistas. No se agregan funcionalidades adicionales a las mencionadas.

| ID | Requerimiento funcional | Historias relacionadas | Fuente |
|---|---|---|---|
| RF-01 | El sistema debe permitir crear una solicitud de crédito desde los canales app móvil, web, agencia y contact center. | HU-01 | Canales P1; CEO P6 |
| RF-02 | El sistema debe asignar un identificador único de solicitud, independiente del canal de origen, y permitir su continuidad entre canales tras autenticación del cliente. | HU-02, HU-03, HU-04 | Canales P4; CEO P6 |
| RF-03 | El sistema debe prellenar y evitar volver a solicitar datos de contacto verificados, dirección, información laboral reciente y cuentas de abono ya disponibles y vigentes del cliente. | HU-05 | Canales P3 |
| RF-04 | El sistema debe permitir al cliente confirmar o actualizar los datos prellenados antes de continuar con la solicitud. | HU-06 | Canales P3 |
| RF-05 | El sistema debe mostrar al cliente una línea de tiempo con el estado actual de la solicitud y las acciones pendientes, traduciendo los estados internos a mensajes simples y claros. | HU-07, HU-08 | Canales P2, P5; CEO P6 |
| RF-06 | El sistema debe representar el estado de la solicitud usando, al menos, los siguientes estados orientados al cliente: borrador, información pendiente, en evaluación, requiere documento, requiere validación, aprobado, no aprobado, pendiente de aceptación, listo para desembolso, desembolsado y cancelado. | HU-07, HU-08 | Canales P5 |
| RF-07 | El sistema debe generar notificaciones para los eventos: confirmación de inicio, recordatorio de información pendiente, cambio relevante de estado, aprobación con vigencia, contrato disponible y desembolso. | HU-09 | Canales P6; CEO P1, P3 |
| RF-08 | El sistema debe permitir al cliente seleccionar los canales de notificación permitidos entre app, correo y SMS, y respetar dicha preferencia al notificar. | HU-10 | Canales P6 |
| RF-09 | El sistema no debe incluir datos sensibles en el contenido de las notificaciones enviadas. | HU-11 | Canales P6 |
| RF-10 | El sistema debe permitir adjuntar documentos (por ejemplo, boletas o constancias) asociados a una solicitud, cuando el proceso lo requiera. | HU-12 | Canales P2; Riesgos P9 |
| RF-11 | El sistema debe extraer campos de los documentos adjuntados mediante IA, registrando el documento de origen y un nivel de confianza por cada campo extraído, sin completar campos que no logre identificar. | HU-13 | Riesgos P9; CEO P8 |
| RF-12 | El sistema debe marcar para revisión manual los campos extraídos con nivel de confianza por debajo del umbral acordado. | HU-14 | Riesgos P9 |
| RF-13 | El sistema debe consultar, para cada solicitud, identidad, edad, residencia, situación laboral, ingresos, obligaciones vigentes, comportamiento de pago, exposición total, producto solicitado, monto, plazo y canal de origen, usando fuentes internas para clientes existentes y documentos/fuentes externas para clientes nuevos. | HU-15 | Riesgos P1, P2 |
| RF-14 | El sistema debe ejecutar un motor de reglas que aplique las políticas de elegibilidad vigentes y produzca uno de los siguientes resultados: aprobado, rechazado, observado o enviado a revisión manual. | HU-16 | Riesgos P1, P4 |
| RF-15 | El sistema debe entregar una decisión prácticamente inmediata para los clientes identificados como preaprobados. | HU-17 | CEO P1, P3 |
| RF-16 | El sistema debe registrar en un resultado "aprobado" el monto máximo, plazo permitido, tasa, condiciones y fecha de vigencia. | HU-18 | Riesgos P4 |
| RF-17 | El sistema debe registrar en un resultado "rechazado" las razones internas de la decisión y distinguir cuáles son visibles para el cliente. | HU-19 | Riesgos P4 |
| RF-18 | El sistema debe permitir al cliente revisar las condiciones del crédito y aceptar el contrato como paso previo al desembolso. | HU-20 | Canales P2 |
| RF-19 | El sistema debe enviar automáticamente a revisión manual las solicitudes que presenten: inconsistencias entre ingresos declarados y observados, alertas de identidad, exposición cercana al límite, documentos ilegibles, información incompleta, o marca de excepción de campaña. | HU-21 | Riesgos P6 |
| RF-20 | El sistema debe permitir a un analista registrar una recomendación de excepción con su justificación y los documentos considerados. | HU-22 | Riesgos P7 |
| RF-21 | El sistema debe permitir a un supervisor aprobar o rechazar, dentro del propio sistema, una excepción recomendada, registrando el usuario que autoriza. | HU-23 | Riesgos P7 |
| RF-22 | El sistema debe permitir reconstruir cualquier decisión indicando los datos usados, su fuente, la hora, la versión de reglas vigente en ese momento, el score obtenido, las excepciones aplicadas y el usuario interviniente. | HU-24 | Riesgos P5 |
| RF-23 | El sistema no debe modificar una decisión histórica cuando un dato subyacente cambie posteriormente. | HU-25 | Riesgos P5 |
| RF-24 | El sistema debe distinguir una nueva solicitud de un reintento del mismo proceso, evitando evaluaciones o desembolsos duplicados sobre la misma solicitud. | HU-26 | Riesgos P8, P10 |
| RF-25 | El sistema debe permitir administrar reglas de elegibilidad (por campaña, apetito de riesgo, segmento, comportamiento de cartera y regulación), incluyendo su fecha de vigencia. | HU-27 | Riesgos P3 |
| RF-26 | El sistema debe conservar la información ya registrada por el cliente cuando una integración falle durante el proceso de solicitud. | HU-28 | Canales P7 |
| RF-27 | El sistema debe permitir reintentar únicamente la acción afectada por un fallo de integración, sin obligar a repetir toda la solicitud. | HU-29 | Canales P7 |
| RF-28 | El sistema debe permitir a un asesor autorizado consultar el mismo estado de solicitud visible para el cliente, restringido a la información necesaria. | HU-30 | Canales P4 |
| RF-29 | El sistema debe permitir a un agente de contact center consultar el estado de una solicitud y registrar una incidencia, sin permitir modificar una decisión de riesgos. | HU-31 | Canales P9 |
| RF-30 | El sistema debe presentar formularios con lenguaje claro, extensión reducida, validaciones inmediatas y compatibilidad con lectores de pantalla. | HU-32 | Canales P9 |
| RF-31 | El sistema debe registrar eventos por etapa del recorrido: ingreso, abandono, error, documento rechazado, reintento, tiempo de respuesta y conversión. | HU-33 | Canales P10 |
| RF-32 | El sistema debe mantener separados los eventos de navegación de la información financiera más sensible del cliente. | HU-34 | Canales P10 |
| RF-33 | El sistema debe calcular y exponer los indicadores: conversión de ofertas a desembolsos, tiempo medio desde la solicitud hasta la decisión, abandono por etapa, mora temprana y volumen de solicitudes con intervención manual. | HU-35 | CEO P4 |

## Alcance del MVP según lo declarado por el CEO
- RF aplicables prioritariamente a **créditos personales para clientes existentes con ingresos recurrentes** (CEO P5). La atención a clientes nuevos y trabajadores independientes queda fuera del alcance inicial declarado y debe tratarse como capacidad futura.
- Se prioriza un alcance reducido de extremo a extremo (solicitud → decisión → desembolso) antes que una cobertura amplia sin capacidad real de desembolso (CEO P9).

## Fuera de alcance / no confirmado por las entrevistas
Ver `discrepancias.md` para requerimientos que no pueden formularse por falta de información (fuentes externas exactas, reglas de deduplicación, política de retención, SLA por etapa, límites de actualización de datos).
