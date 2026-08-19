# 02 — Criterios de Aceptación
## Proyecto: Crédito Ágil 360

> Criterios expresados en formato Dado/Cuando/Entonces, en correspondencia directa con cada historia de usuario del archivo `01_historias_usuario.md`. Solo se detallan criterios sustentados en el texto de las entrevistas; donde el detalle exacto (umbrales, tiempos, listas completas) no está definido, se marca como **[PENDIENTE — ver discrepancias.md]**.

---

**HU-01 — Inicio multicanal**
- Dado que un cliente accede por app, web, agencia o contact center, cuando inicia una solicitud, entonces el sistema debe permitir crearla desde cualquiera de esos cuatro canales.

**HU-02 — Continuidad entre canales**
- Dado que un cliente inició una solicitud en un canal, cuando la retoma en otro canal, entonces debe encontrar la información ya registrada sin tener que volver a ingresarla.

**HU-03 — Identificador único**
- Dado que existe una solicitud, cuando se consulta desde cualquier canal, entonces debe identificarse con un único identificador de solicitud, independiente del canal de origen.

**HU-04 — Recuperación tras autenticación**
- Dado un cliente con una solicitud en curso, cuando se autentica en cualquier canal, entonces debe poder recuperar el estado exacto de su proceso.

**HU-05 — No repetir datos ya disponibles**
- Dado un cliente existente con datos de contacto, dirección, información laboral o cuenta de abono vigentes, cuando inicia una solicitud, entonces el sistema no debe solicitar nuevamente esos datos.

**HU-06 — Confirmar o actualizar datos**
- Dado un dato ya registrado del cliente, cuando se le presenta durante la solicitud, entonces el cliente debe poder confirmarlo o actualizarlo antes de continuar.

**HU-07 — Línea de tiempo de estado**
- Dado que una solicitud está en curso, cuando el cliente consulta su estado, entonces debe visualizar una línea de tiempo con la etapa actual y las acciones pendientes.

**HU-08 — Mensajes claros**
- Dado un estado interno de la solicitud, cuando se muestra al cliente, entonces debe traducirse a un mensaje simple e instructivo (no a la nomenclatura interna).

**HU-09 — Notificaciones por evento**
- Dado uno de los eventos definidos (inicio, información pendiente, cambio de estado relevante, aprobación con vigencia, contrato disponible, desembolso), cuando ocurre, entonces el sistema debe generar la notificación correspondiente.

**HU-10 — Selección de canal de notificación**
- Dado un cliente con preferencias de notificación configuradas, cuando el sistema genera una notificación, entonces debe enviarla solo por los canales que el cliente autorizó.

**HU-11 — Sin datos sensibles en notificaciones**
- Dado el contenido de una notificación, cuando se genera, entonces no debe incluir datos financieros o personales sensibles en el cuerpo del mensaje.

**HU-12 — Adjuntar documentos**
- Dado que la solicitud requiere un documento (p. ej. boleta o constancia), cuando el cliente lo adjunta, entonces debe quedar asociado a la solicitud correspondiente.

**HU-13 — Extracción de campos con IA**
- Dado un documento adjuntado, cuando se procesa con IA, entonces cada campo extraído debe registrar el documento de origen y un nivel de confianza, y el sistema no debe completar campos que no logra extraer.

**HU-14 — Revisión de baja confianza**
- Dado un campo extraído con confianza por debajo del umbral acordado **[PENDIENTE — el valor del umbral no está definido en las entrevistas]**, cuando se detecta, entonces el caso debe marcarse para revisión manual.

**HU-15 — Consulta de información para evaluación**
- Dado un solicitante identificado, cuando se ejecuta la evaluación, entonces el sistema debe consultar identidad, ingresos, comportamiento interno, endeudamiento, alertas y score.

**HU-16 — Resultado de la evaluación**
- Dado que se aplicaron las políticas de elegibilidad vigentes, cuando concluye la evaluación, entonces el resultado debe ser uno de: aprobado, rechazado, observado o enviado a revisión manual.

**HU-17 — Decisión inmediata para preaprobados**
- Dado un cliente preaprobado, cuando confirma su solicitud, entonces la decisión debe entregarse de forma prácticamente inmediata (tiempo exacto no definido en las entrevistas).

**HU-18 — Contenido de un aprobado**
- Dado un resultado "aprobado", cuando se registra, entonces debe incluir monto máximo, plazo permitido, tasa, condiciones y fecha de vigencia.

**HU-19 — Contenido de un rechazo**
- Dado un resultado "rechazado", cuando se registra, entonces debe incluir las razones internas de la decisión, indicando cuáles son visibles para el cliente.

**HU-20 — Aceptación de contrato**
- Dado un crédito aprobado y aceptado por el cliente, cuando revisa las condiciones y confirma, entonces el contrato debe quedar aceptado y habilitado para el desembolso.

**HU-21 — Envío a revisión manual**
- Dado uno de los criterios listados (inconsistencia de ingresos, alerta de identidad, exposición cercana al límite, documento ilegible, información incompleta, marca de campaña), cuando se detecta en una solicitud, entonces esta debe enviarse a revisión manual.

**HU-22 — Recomendación de excepción**
- Dado un caso en revisión, cuando el analista recomienda una excepción, entonces debe registrar justificación y documentos considerados.

**HU-23 — Aprobación de excepción por supervisor**
- Dado una excepción recomendada, cuando el nivel de riesgo lo requiere, entonces debe ser aprobada o rechazada por un supervisor dentro del sistema, quedando registrado el usuario que autorizó.

**HU-24 — Reconstrucción de una decisión**
- Dado el identificador de una decisión, cuando se audita, entonces el sistema debe reconstruir los datos usados, su fuente, la hora, la versión de reglas vigente, el score obtenido, las excepciones aplicadas y el usuario interviniente.

**HU-25 — Inmutabilidad de decisiones históricas**
- Dado un dato que cambia después de emitida una decisión, cuando ocurre el cambio, entonces la decisión histórica ya registrada no debe modificarse.

**HU-26 — Distinción entre nueva solicitud y reintento**
- Dado un envío repetido del mismo proceso, cuando el sistema lo recibe, entonces debe identificarlo como reintento y no como una solicitud nueva.

**HU-27 — Gestión de reglas de elegibilidad**
- Dado un cambio de política (campaña, apetito de riesgo, segmento, cartera o regulación), cuando se actualiza, entonces debe quedar registrado con su vigencia, sin depender de hojas de cálculo o manuales externos al sistema.

**HU-28 — Persistencia ante fallo de integración**
- Dado que una integración falla durante el llenado de la solicitud, cuando ocurre el error, entonces la información ya registrada por el cliente no debe perderse.

**HU-29 — Reintento acotado**
- Dado un fallo puntual, cuando se resuelve, entonces el sistema debe indicar al cliente que reintente únicamente la acción afectada, evitando solicitudes duplicadas.

**HU-30 — Visibilidad para asesores**
- Dado un asesor autorizado, cuando consulta una solicitud, entonces debe ver el mismo estado que ve el cliente, limitado a la información necesaria.

**HU-31 — Atención en contact center**
- Dado un agente de contact center, cuando atiende a un cliente, entonces puede consultar el estado y registrar una incidencia, pero no modificar una decisión de riesgos.

**HU-32 — Accesibilidad**
- Dado un formulario de la solicitud, cuando se presenta al cliente, entonces debe usar lenguaje claro, ser corto, validar de forma inmediata y ser compatible con lectores de pantalla.

**HU-33 — Eventos del recorrido**
- Dado el avance del cliente por las etapas de la solicitud, cuando ocurre un evento (ingreso, abandono, error, documento rechazado, reintento, tiempo de respuesta, conversión), entonces debe registrarse para su análisis.

**HU-34 — Separación de datos de navegación y financieros**
- Dado un evento de navegación registrado, cuando se almacena, entonces no debe combinarse con información financiera más sensible de lo necesario.

**HU-35 — Indicadores de negocio**
- Dado el conjunto de solicitudes procesadas, cuando se generan reportes, entonces deben calcularse conversión de ofertas a desembolsos, tiempo medio de decisión, abandono por etapa, mora temprana y volumen de intervención manual.

**HU-36 — Disponibilidad en campañas**
- Dado un escenario de campaña con tráfico multiplicado, cuando ocurre el pico de demanda, entonces el sistema debe mantenerse disponible y responder de forma consistente (umbral numérico exacto no definido en las entrevistas).
