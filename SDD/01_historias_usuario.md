# 01 — Historias de Usuario
## Proyecto: Crédito Ágil 360 — Banco Andino Digital

> Todas las historias se derivan exclusivamente de las entrevistas (CEO, Riesgos de Crédito, Canales Digitales) contenidas en `01_banca_credito_agil_360.md`. Cada historia indica su **fuente** (entrevista y pregunta). No se incorporan reglas, actores ni funcionalidades no mencionadas.

Formato: **Como** [actor], **quiero** [acción], **para** [beneficio].

---

### Bloque A — Inicio y continuidad de la solicitud (multicanal)

**HU-01.** Como cliente, quiero iniciar una solicitud de crédito desde la app móvil, la web, una agencia o el contact center, para poder solicitar el crédito por el canal que prefiera.
*Fuente: Canales P1; CEO P6.*

**HU-02.** Como cliente, quiero continuar mi solicitud en un canal distinto al que la inicié, sin perder la información ya registrada, para no tener que empezar de nuevo.
*Fuente: CEO P6; Canales P1, P4.*

**HU-03.** Como cliente, quiero que la solicitud tenga un identificador único que se conserve sin importar el canal, para que se trate siempre del mismo trámite.
*Fuente: Canales P4.*

**HU-04.** Como cliente, quiero recuperar mi proceso después de autenticarme, para retomarlo en cualquier momento.
*Fuente: Canales P4.*

---

### Bloque B — Datos del cliente

**HU-05.** Como cliente existente, quiero que el sistema no me vuelva a solicitar datos de contacto verificados, dirección, información laboral reciente y cuentas de abono ya disponibles y vigentes, para agilizar mi solicitud.
*Fuente: Canales P3.*

**HU-06.** Como cliente, quiero poder confirmar o actualizar la información que el banco ya tiene registrada, para evitar que se use información desactualizada en mi evaluación.
*Fuente: Canales P3.*

---

### Bloque C — Estado, transparencia y notificaciones

**HU-07.** Como cliente, quiero ver una línea de tiempo con el estado de mi solicitud y las acciones pendientes, para saber qué debo hacer y en qué etapa estoy.
*Fuente: Canales P2, P5; CEO P6.*

**HU-08.** Como cliente, quiero que los estados se muestren con mensajes simples y claros (no ambiguos, por ejemplo evitar "solicitud observada"), para entender exactamente qué se espera de mí.
*Fuente: CEO P6; Canales P5.*

**HU-09.** Como cliente, quiero recibir notificaciones de confirmación de inicio, recordatorio de información pendiente, cambio relevante de estado, aprobación con vigencia, contrato disponible y desembolso, para estar informado sin tener que llamar al banco.
*Fuente: Canales P6; CEO P1, P3.*

**HU-10.** Como cliente, quiero elegir los canales por los que recibo notificaciones (dentro de la app, correo o SMS), para recibirlas por el medio de mi preferencia.
*Fuente: Canales P6.*

**HU-11.** Como cliente, quiero que las notificaciones no incluyan datos sensibles en su contenido, para proteger mi información.
*Fuente: Canales P6.*

---

### Bloque D — Documentos, evaluación y decisión

**HU-12.** Como cliente, quiero adjuntar documentos (por ejemplo boletas o constancias) cuando la solicitud lo requiera, para que el banco valide mi información.
*Fuente: Canales P2; Riesgos P9.*

**HU-13.** Como analista de riesgos, quiero que el sistema extraiga campos de boletas o constancias mediante IA, conservando el documento de origen y un nivel de confianza por campo extraído, sin que el sistema complete datos que no encuentra, para agilizar la revisión.
*Fuente: Riesgos P9; CEO P8.*

**HU-14.** Como analista de riesgos, quiero que los campos extraídos con un nivel de confianza por debajo del umbral acordado se marquen para revisión manual, para asegurar la calidad de la información usada en la evaluación.
*Fuente: Riesgos P9.*

**HU-15.** Como analista de riesgos, quiero consultar identidad, ingresos, comportamiento interno, endeudamiento, alertas y score del solicitante, para evaluar su elegibilidad.
*Fuente: Riesgos P1, P2.*

**HU-16.** Como motor de reglas, quiero aplicar las políticas de elegibilidad vigentes a cada solicitud, para producir un resultado de aprobado, rechazado, observado o enviado a revisión manual.
*Fuente: Riesgos P1, P4.*

**HU-17.** Como cliente preaprobado, quiero recibir una decisión prácticamente inmediata, para acceder al crédito sin demoras.
*Fuente: CEO P1, P3.*

**HU-18.** Como analista de riesgos, quiero que un resultado aprobado incluya monto máximo, plazo permitido, tasa, condiciones y fecha de vigencia, para comunicar una oferta concreta al cliente.
*Fuente: Riesgos P4.*

**HU-19.** Como analista de riesgos, quiero que un rechazo registre las razones internas de la decisión, aunque no todas se muestren literalmente al cliente, para mantener un sustento auditable.
*Fuente: Riesgos P4.*

**HU-20.** Como cliente, quiero revisar las condiciones del crédito (monto, plazo, tasa) y aceptar el contrato, para formalizar el desembolso.
*Fuente: Canales P2.*

---

### Bloque E — Revisión manual y excepciones

**HU-21.** Como analista de riesgos, quiero que las solicitudes con inconsistencias entre ingresos declarados y observados, alertas de identidad, exposición cercana al límite, documentos ilegibles, información incompleta o marcadas como excepcionales por una campaña se envíen a revisión manual, para asegurar una evaluación adecuada.
*Fuente: Riesgos P6.*

**HU-22.** Como analista de riesgos, quiero poder recomendar una excepción registrando su justificación y los documentos considerados, para que un supervisor la evalúe según el nivel de riesgo.
*Fuente: Riesgos P7.*

**HU-23.** Como supervisor, quiero aprobar o rechazar dentro del sistema las excepciones recomendadas por un analista (no por correo fuera del sistema), para mantener un control formal y registrado.
*Fuente: Riesgos P7.*

---

### Bloque F — Trazabilidad, auditoría e integridad

**HU-24.** Como gerente de Riesgos, quiero poder reconstruir cualquier decisión (datos usados, fuente, hora, versión de reglas vigente, score obtenido, excepciones aplicadas, usuario interviniente), para fines de auditoría.
*Fuente: Riesgos P5.*

**HU-25.** Como gerente de Riesgos, quiero que si un dato cambia después de tomada una decisión, la decisión histórica no se reescriba, para preservar la trazabilidad.
*Fuente: Riesgos P5.*

**HU-26.** Como gerente de Riesgos, quiero que el sistema distinga una nueva solicitud de un reintento del mismo proceso, para evitar duplicar información o evaluaciones.
*Fuente: Riesgos P8.*

**HU-27.** Como gerente de Riesgos, quiero poder gestionar las reglas de elegibilidad (por campaña, apetito de riesgo, segmento, comportamiento de cartera y regulación) incluyendo su vigencia, para no depender de sistemas dispersos, hojas de cálculo y manuales operativos.
*Fuente: Riesgos P3.*

---

### Bloque G — Continuidad ante fallos

**HU-28.** Como cliente, quiero que si una integración falla mientras completo mi solicitud, no se pierda la información ya registrada, para no repetir el proceso desde el inicio.
*Fuente: Canales P7.*

**HU-29.** Como cliente, quiero que el sistema me indique con claridad si debo reintentar solo una acción puntual, en lugar de toda la solicitud, para evitar solicitudes duplicadas por reintentos.
*Fuente: Canales P7.*

---

### Bloque H — Asesores, contact center y soporte

**HU-30.** Como asesor autorizado, quiero ver el mismo estado de la solicitud que ve el cliente, sin acceder a información innecesaria, para ayudarlo sin importar el canal.
*Fuente: Canales P4.*

**HU-31.** Como agente de contact center, quiero consultar el estado de una solicitud y registrar una incidencia, sin poder modificar una decisión de riesgos, para atender al cliente dentro de mis atribuciones.
*Fuente: Canales P9.*

**HU-32.** Como cliente, quiero que los formularios sean cortos, con lenguaje claro y validaciones inmediatas, y que sean compatibles con lectores de pantalla, para completar mi solicitud sin barreras.
*Fuente: Canales P9.*

---

### Bloque I — Analítica y medición de negocio

**HU-33.** Como área de Canales Digitales, quiero capturar eventos por etapa (ingreso, abandono, error, documento rechazado, reintento, tiempo de respuesta y conversión), para analizar y mejorar el recorrido del cliente.
*Fuente: Canales P10.*

**HU-34.** Como área de Canales Digitales, quiero que los eventos de navegación no se mezclen con información financiera más sensible de lo necesario, para proteger los datos del cliente.
*Fuente: Canales P10.*

**HU-35.** Como CEO, quiero medir conversión de ofertas a desembolsos, tiempo medio desde la solicitud hasta la decisión, abandono por etapa, mora temprana y volumen de solicitudes que requieren intervención manual, para evaluar el éxito del producto.
*Fuente: CEO P4.*

---

### Bloque J — Disponibilidad y volumen

**HU-36.** Como cliente, quiero que la aplicación esté disponible y responda de forma consistente durante campañas con alto tráfico, para poder completar mi solicitud sin fallas.
*Fuente: Canales P8; Riesgos P10.*

---

## Trazabilidad
Todas las historias (HU-01 a HU-36) citan la entrevista y pregunta de origen. No se incluyen historias sin referencia explícita en el input. Ver `discrepancias.md` para vacíos que impiden precisar historias adicionales (p. ej. flujo de trabajadores independientes o clientes nuevos, mencionado en CEO P5 solo como alcance futuro, no detallado).
