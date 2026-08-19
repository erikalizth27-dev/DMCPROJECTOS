# 05 — Casos de Uso
## Proyecto: Crédito Ágil 360

> Actores identificados en las entrevistas y en la tabla de evidencias: **Cliente, Asesor (agencia/contact center), Analista de Riesgos, Supervisor, Motor de Reglas (sistema), Sistemas externos**. No se incorporan actores adicionales.

---

### CU-01 Iniciar solicitud de crédito (multicanal)
- **Actor principal:** Cliente.
- **Precondición:** El cliente accede a un canal (app, web, agencia, contact center).
- **Flujo principal:**
  1. El cliente selecciona una oferta o simula el crédito.
  2. El sistema crea la solicitud con un identificador único.
  3. El sistema recupera y muestra los datos ya disponibles del cliente.
- **Flujo alterno:** Si el cliente ya tenía una solicitud abierta en otro canal, el sistema la recupera en lugar de crear una nueva.
- **Postcondición:** Solicitud en estado "borrador" u "en curso" asociada al cliente.
- **Fuente:** Canales P1, P2, P4; CEO P6.

### CU-02 Confirmar o actualizar datos del cliente
- **Actor principal:** Cliente.
- **Precondición:** Existe una solicitud iniciada con datos prellenados.
- **Flujo principal:**
  1. El sistema presenta los datos de contacto, dirección, información laboral y cuenta de abono disponibles.
  2. El cliente confirma o actualiza cada dato.
  3. El sistema autoriza las consultas necesarias.
- **Postcondición:** Datos confirmados/actualizados asociados a la solicitud.
- **Fuente:** Canales P2, P3.

### CU-03 Cargar y procesar documento con IA
- **Actor principal:** Cliente. **Actor secundario:** Sistema de extracción (IA).
- **Precondición:** La solicitud requiere un documento (p. ej. boleta o constancia).
- **Flujo principal:**
  1. El cliente adjunta el documento.
  2. El sistema extrae campos y asigna un nivel de confianza a cada uno, conservando el documento de origen.
  3. Si algún campo no se identifica, el sistema no lo completa.
  4. Si algún campo tiene confianza por debajo del umbral acordado, se marca para revisión manual.
- **Postcondición:** Documento asociado a la solicitud con campos extraídos y trazables.
- **Fuente:** Riesgos P9; CEO P8.

### CU-04 Evaluar solicitud (motor de reglas)
- **Actor principal:** Motor de reglas (sistema). **Actor secundario:** Analista de Riesgos.
- **Precondición:** La solicitud cuenta con los datos e información mínima requerida.
- **Flujo principal:**
  1. El sistema identifica al solicitante y determina si es cliente existente o nuevo.
  2. El sistema consulta identidad, ingresos, comportamiento interno, endeudamiento, alertas, score y demás datos requeridos.
  3. El sistema aplica las políticas de elegibilidad vigentes (versión de reglas activa).
  4. El sistema produce un resultado: aprobado, rechazado, observado o revisión manual.
- **Flujo alterno:** Si el cliente está preaprobado, la decisión se entrega de forma prácticamente inmediata.
- **Postcondición:** Decisión registrada con su sustento (datos, fuente, hora, versión de reglas, score).
- **Fuente:** Riesgos P1, P2, P4; CEO P1, P3.

### CU-05 Enviar solicitud a revisión manual
- **Actor principal:** Motor de reglas (sistema). **Actor secundario:** Analista de Riesgos.
- **Precondición:** Se detecta alguno de los criterios de revisión manual (inconsistencia de ingresos, alerta de identidad, exposición cercana al límite, documento ilegible, información incompleta, marca de campaña).
- **Flujo principal:**
  1. El sistema marca la solicitud como pendiente de revisión.
  2. El analista revisa la información y los documentos asociados.
  3. El analista registra su decisión o recomienda una excepción (ver CU-06).
- **Postcondición:** Solicitud con decisión de analista registrada.
- **Fuente:** Riesgos P6.

### CU-06 Recomendar y aprobar excepción
- **Actor principal:** Analista de Riesgos. **Actor secundario:** Supervisor.
- **Precondición:** Existe un caso en revisión manual donde el analista considera pertinente una excepción.
- **Flujo principal:**
  1. El analista registra la recomendación de excepción con su justificación y documentos considerados.
  2. Según el nivel de riesgo, el sistema enruta la excepción a un supervisor.
  3. El supervisor aprueba o rechaza la excepción dentro del sistema.
- **Regla:** No se aceptan aprobaciones de excepciones por correo fuera del sistema.
- **Postcondición:** Excepción registrada con su decisión y el usuario que la autorizó.
- **Fuente:** Riesgos P7.

### CU-07 Consultar estado de la solicitud
- **Actor principal:** Cliente. **Actor secundario:** Asesor autorizado.
- **Precondición:** La solicitud existe y el actor está autenticado/autorizado.
- **Flujo principal:**
  1. El actor consulta el estado desde cualquier canal.
  2. El sistema traduce el estado interno a un mensaje simple (para el cliente) o al detalle correspondiente (para el asesor), limitado a la información necesaria.
- **Postcondición:** Estado y acciones pendientes visualizados.
- **Fuente:** Canales P2, P4, P5.

### CU-08 Notificar al cliente
- **Actor principal:** Sistema. **Actor secundario:** Cliente.
- **Precondición:** Ocurre un evento notificable (inicio, información pendiente, cambio de estado, aprobación con vigencia, contrato disponible, desembolso).
- **Flujo principal:**
  1. El sistema identifica el evento.
  2. El sistema construye la notificación sin datos sensibles.
  3. El sistema la envía únicamente por los canales autorizados por el cliente.
- **Postcondición:** Notificación entregada.
- **Fuente:** Canales P6.

### CU-09 Aceptar contrato y desembolsar
- **Actor principal:** Cliente. **Actor secundario:** Sistema.
- **Precondición:** La solicitud está aprobada y vigente.
- **Flujo principal:**
  1. El cliente revisa monto, plazo, tasa y condiciones.
  2. El cliente acepta el contrato.
  3. El sistema ejecuta el desembolso, garantizando que no se desembolse dos veces la misma solicitud.
- **Postcondición:** Solicitud en estado "desembolsado".
- **Fuente:** Canales P2; Riesgos P10.

### CU-10 Reintentar acción tras fallo de integración
- **Actor principal:** Cliente. **Actor secundario:** Sistema.
- **Precondición:** Una integración falla durante el proceso (p. ej. consulta externa con timeout).
- **Flujo principal:**
  1. El sistema conserva la información ya registrada por el cliente.
  2. El sistema informa que continuará procesando o solicita reintentar solo la acción afectada.
  3. El cliente reintenta la acción puntual, sin generar una solicitud duplicada.
- **Postcondición:** Proceso continuado sin pérdida de información ni duplicidad.
- **Fuente:** Canales P7.

### CU-11 Auditar una decisión
- **Actor principal:** Analista/Gerente de Riesgos.
- **Precondición:** Existe una decisión registrada.
- **Flujo principal:**
  1. El actor solicita el detalle de una decisión.
  2. El sistema reconstruye los datos usados, la fuente, la hora, la versión de reglas vigente, el score, las excepciones aplicadas y el usuario interviniente.
- **Regla:** Cambios posteriores en los datos no alteran la decisión histórica.
- **Fuente:** Riesgos P5.

### CU-12 Gestionar reglas de elegibilidad
- **Actor principal:** Gerente de Riesgos.
- **Precondición:** Se requiere crear, modificar o dar de baja una regla (por campaña, apetito de riesgo, segmento, cartera o regulación).
- **Flujo principal:**
  1. El actor registra la regla con su vigencia.
  2. El sistema la activa según la fecha correspondiente, sin afectar decisiones históricas ya emitidas con versiones anteriores.
- **Fuente:** Riesgos P3.

### CU-13 Registrar incidencia en contact center
- **Actor principal:** Agente de contact center.
- **Precondición:** Un cliente contacta al banco por una solicitud en curso.
- **Flujo principal:**
  1. El agente consulta el estado de la solicitud.
  2. El agente registra una incidencia si corresponde.
- **Restricción:** El agente no puede modificar una decisión de riesgos.
- **Fuente:** Canales P9.

### CU-14 Analizar eventos del recorrido
- **Actor principal:** Área de Canales Digitales.
- **Precondición:** Existen eventos registrados por etapa del recorrido.
- **Flujo principal:**
  1. El área consulta eventos de ingreso, abandono, error, documento rechazado, reintento, tiempo de respuesta y conversión.
  2. El sistema presenta esta información separada de datos financieros sensibles.
- **Fuente:** Canales P10.

### CU-15 Medir indicadores de negocio
- **Actor principal:** CEO / dirección del banco.
- **Precondición:** Existen solicitudes procesadas en el periodo de análisis.
- **Flujo principal:**
  1. El actor consulta conversión de ofertas a desembolsos, tiempo medio de decisión, abandono por etapa, mora temprana y volumen de intervención manual.
- **Fuente:** CEO P4.
