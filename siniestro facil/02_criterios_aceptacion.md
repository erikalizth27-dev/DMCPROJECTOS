# Criterios de Aceptación — Siniestro Fácil

> Formato Given/When/Then. Cada criterio referencia la historia de usuario (HU) y su fuente. No se agregan umbrales numéricos, SLA ni reglas que las entrevistas no mencionan explícitamente; donde el dato falta se marca como **[pendiente — ver discrepancias.md]**.

## HU-01 — Reportar un siniestro desde el teléfono
- **Dado** que soy un asegurado con la aplicación,
  **cuando** inicio un reporte de accidente,
  **entonces** puedo completarlo desde el teléfono sin necesidad de llamar a un canal telefónico. *(Entrevista 1, P3)*

## HU-02 — Ser guiado paso a paso durante el reporte
- **Dado** que estoy reportando un siniestro,
  **cuando** avanzo en el formulario,
  **entonces** la aplicación me indica en lenguaje humano qué hacer, cómo protegerme, qué evidencia recopilar y cuándo llegará la asistencia. *(Entrevista 1, P6)*

## HU-03 — Reportar con información mínima
- **Dado** que no cuento con toda la evidencia en el momento,
  **cuando** intento crear el caso con número de póliza o documento, placa del vehículo, fecha y ubicación aproximada, tipo de evento y un medio de contacto,
  **entonces** el sistema permite crear el caso sin exigir evidencia adicional de inmediato. *(Entrevista 2, P2)*
- **Dado** que el sistema exige un dato distinto a los mínimos listados,
  **entonces** esto contradice el requisito y debe revisarse. *(Entrevista 2, P2)*

## HU-04 — Reporte por un tercero autorizado
- **Dado** que el titular de la póliza no puede reportar el caso,
  **cuando** una persona autorizada realiza el reporte,
  **entonces** el sistema permite registrar el caso identificando que el reportante es distinto al asegurado. *(Entrevista 1, P6)*
- **[Pendiente]** Las entrevistas no describen cómo se valida o define "persona autorizada". *(ver discrepancias.md)*

## HU-05 — Adjuntar evidencias desde la aplicación
- **Dado** que estoy en el proceso de reporte o seguimiento,
  **cuando** adjunto fotografías o documentos,
  **entonces** cada evidencia queda vinculada al siniestro, al momento de captura y, cuando sea posible, a ubicación y dispositivo. *(Entrevista 2, P3)*

## HU-06 — Conocer el estado y siguiente paso del caso
- **Dado** que tengo un siniestro en curso,
  **cuando** consulto mi caso,
  **entonces** veo el estado actual y el siguiente paso, sin necesidad de llamar. *(Entrevista 1, P3, P4)*
- **Dado** que el proceso tiene subestados internos,
  **entonces** el asegurado ve únicamente los estados relevantes para él, no los subestados internos. *(Entrevista 2, P4)*

## HU-07 — Recibir asistencia coordinada
- **Dado** que el caso lo requiere,
  **cuando** se coordina la asistencia,
  **entonces** el sistema registra la solicitud y su resultado. *(Entrevista 2, P1, P9)*

## HU-08 — Registrar y validar el caso reportado
- **Dado** que un operador atiende un reporte,
  **cuando** registra el caso,
  **entonces** confirma identidad del reportante, póliza y vehículo, y registra fecha, hora, ubicación, personas involucradas, descripción y daños aparentes. *(Entrevista 2, P1)*

## HU-09 — Verificar cobertura y deducible
- **Dado** un caso registrado,
  **cuando** el operador verifica la póliza,
  **entonces** el sistema muestra la cobertura y el deducible aplicables. *(Entrevista 2, P1)*
- **[Pendiente]** No se especifica el resultado exacto ni el mensaje cuando la cobertura es rechazada; el CEO solo indica que debe evitarse el "rechazo incorrecto de coberturas". *(Entrevista 1, P7 — ver discrepancias.md)*

## HU-10 — Evitar casos duplicados por múltiples canales
- **Dado** que un mismo accidente es reportado por el asegurado, el corredor y el taller,
  **cuando** se registra el segundo o tercer reporte,
  **entonces** el sistema debe permitir identificar que corresponde al mismo siniestro. *(Entrevista 2, P6)*
- **[Pendiente]** La política exacta de deduplicación no está definida en las entrevistas. *(ver discrepancias.md, incertidumbre explícita del CEO/Operaciones)*

## HU-11 — Asignar el caso según reglas de negocio
- **Dado** un caso validado,
  **cuando** se ejecuta la asignación,
  **entonces** se consideran ciudad, tipo de daño, severidad, cobertura, disponibilidad de proveedores y señales de riesgo, enviando casos simples a flujo digital y casos complejos a un ajustador. *(Entrevista 2, P5; Entrevista 1, P3)*

## HU-12 — Reasignar un caso conservando el historial
- **Dado** un caso asignado,
  **cuando** se reasigna,
  **entonces** el sistema conserva el historial de asignaciones previas y la razón del cambio. *(Entrevista 2, P5)*

## HU-13 — Registrar autorizaciones que hoy se dan por teléfono
- **Dado** que se otorga una autorización,
  **cuando** el operador la registra,
  **entonces** queda constancia formal en el sistema, sustituyendo la autorización telefónica no documentada. *(Entrevista 2, P6)*

## HU-14 — Consultar la vigencia de un presupuesto
- **Dado** un presupuesto presentado por un taller,
  **cuando** el operador lo consulta,
  **entonces** el sistema muestra su vigencia. *(Entrevista 2, P7)*
- **[Pendiente]** El período de vigencia no está definido en las entrevistas. *(ver discrepancias.md)*

## HU-15 — Reintentar, escalar o reasignar ante proveedor sin respuesta
- **Dado** que un proveedor no responde,
  **cuando** el sistema o el operador actúan,
  **entonces** es posible reintentar, escalar o reasignar, y cada intento queda registrado distinguiendo si fue aceptado, rechazado o sin respuesta. *(Entrevista 2, P9)*

## HU-16 — Auditar la línea de tiempo completa de un caso
- **Dado** un caso existente,
  **cuando** se consulta su auditoría,
  **entonces** se muestra quién registró la información, qué cambió, qué evidencias se añadieron, qué cobertura se aplicó, qué proveedor actuó, qué presupuesto fue aprobado, qué comunicación recibió el cliente y qué pago se autorizó. *(Entrevista 2, P10)*

## HU-17 — Recibir casos complejos derivados
- **Dado** un caso clasificado como complejo o riesgoso,
  **cuando** se asigna,
  **entonces** se deriva a un ajustador para revisión especializada. *(Entrevista 1, P3; Entrevista 2, P5)*

## HU-18 — Programar inspección
- **Dado** un caso que requiere inspección,
  **cuando** se programa,
  **entonces** el caso pasa al estado "inspección programada". *(Entrevista 2, P4, P8)*

## HU-19 — Recibir la orden y presentar presupuesto
- **Dado** un taller que recibe una orden,
  **cuando** presenta el presupuesto,
  **entonces** adjunta el diagnóstico y queda registrada la solicitud de aprobación. *(Entrevista 2, P7)*

## HU-20 — Registrar observaciones, repuestos alternativos y ampliaciones
- **Dado** una reparación en curso,
  **cuando** el taller registra una observación, un repuesto alternativo o una ampliación,
  **entonces** el cambio queda documentado con quién lo aprobó. *(Entrevista 2, P7)*

## HU-21 — Recibir y responder solicitudes de asistencia
- **Dado** una solicitud de asistencia enviada a un proveedor,
  **cuando** el proveedor responde (o no responde),
  **entonces** el sistema registra si fue aceptada, rechazada o sin respuesta. *(Entrevista 2, P9)*

## HU-22 — Revisar alertas de fraude
- **Dado** una alerta generada,
  **cuando** el investigador la revisa,
  **entonces** ve tipo, severidad, explicación, datos de origen, fecha, modelo o regla utilizado y estado de revisión, y puede confirmarla, descartarla o pedir más información dejando la justificación registrada. *(Entrevista 3, P4)*
- **Dado** que existe una inconsistencia,
  **entonces** el sistema no la trata como fraude confirmado ni produce rechazo automático. *(Entrevista 3, P1; Entrevista 1, P8)*

## HU-23 — Consultar señales de riesgo del caso
- **Dado** un caso con señales de riesgo,
  **cuando** el investigador lo consulta,
  **entonces** ve las señales presentes (repetición de participantes/vehículos/talleres, pólizas recientes al evento, ubicaciones incoherentes, fotos reutilizadas, montos atípicos, versiones contradictorias, patrones de contacto compartidos, antecedentes de reclamos) diferenciando señales determinísticas de señales de modelo. *(Entrevista 3, P2)*

## HU-24 — Acceder a información ampliada según rol
- **Dado** un investigador de fraude autenticado,
  **cuando** consulta información ampliada,
  **entonces** el acceso se concede según rol y necesidad, y la consulta o descarga queda registrada. *(Entrevista 3, P7)*
- **Dado** un operador regular,
  **entonces** no ve la información ampliada reservada a investigación. *(Entrevista 3, P7)*

## HU-25 — Relacionar casos sin fusionar expedientes
- **Dado** dos o más siniestros que comparten accidente, teléfono, cuenta bancaria, taller o persona,
  **cuando** el investigador los consulta,
  **entonces** el sistema muestra la relación entre ellos sin fusionar los expedientes. *(Entrevista 3, P8)*

## HU-26 — Consultar el histórico reproducible de una alerta
- **Dado** una alerta generada en el pasado,
  **cuando** se consulta meses después,
  **entonces** el sistema permite reconstruir por qué se generó, aun si la regla o el modelo cambiaron, mostrando versión, datos de entrada y evidencia de revisión humana. *(Entrevista 3, P10)*

## HU-27 — Configurar y versionar la política de bloqueo por alertas
- **Dado** una alerta con severidad crítica,
  **cuando** se evalúa la política vigente,
  **entonces** el sistema aplica la versión de política correspondiente para decidir si bloquea el pago, deriva el caso o solo aumenta prioridad de revisión. *(Entrevista 3, P5)*
- **[Pendiente]** Los umbrales exactos de cada política no están definidos en las entrevistas. *(ver discrepancias.md)*

## HU-28 — Ver una vista única del caso
- **Dado** un supervisor,
  **cuando** consulta un siniestro,
  **entonces** obtiene una vista única con la información del caso, sin necesidad de consultar sistemas o canales distintos. *(Entrevista 1, P3)*

## HU-29 — Medir los indicadores de éxito del proceso
- **Dado** la operación en curso,
  **cuando** se consultan los indicadores,
  **entonces** se dispone de tiempo hasta primera asistencia, tiempo hasta decisión, porcentaje de casos resueltos sin llamadas adicionales, satisfacción del cliente, costo operativo por siniestro y pérdidas evitadas por fraude. *(Entrevista 1, P4)*

## HU-30 — Revisar y corregir una decisión asistida por IA
- **Dado** una recomendación generada por IA (clasificación, priorización o alerta),
  **cuando** un usuario autorizado la revisa,
  **entonces** puede confirmarla o descartarla, y la decisión final queda explicada y registrada como revisión humana. *(Entrevista 1, P7, P8; Entrevista 3, P4)*
