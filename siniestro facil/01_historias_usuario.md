# Historias de Usuario — Siniestro Fácil

> Trazabilidad: cada historia cita la entrevista y pregunta de origen. Ninguna historia agrega alcance, actor o funcionalidad no mencionada en el material de descubrimiento.

## Actor: Asegurado / Reportante autorizado

### HU-01 — Reportar un siniestro desde el teléfono
**Como** asegurado,
**quiero** reportar un accidente desde mi teléfono,
**para** iniciar la atención sin llamar por teléfono ni acudir a una oficina.
*Fuente: Entrevista 1 (CEO), P3, P6.*

### HU-02 — Ser guiado paso a paso durante el reporte
**Como** asegurado,
**quiero** recibir instrucciones en lenguaje humano (qué hacer, cómo protegerme, qué evidencia recopilar, cuándo llega la asistencia),
**para** actuar correctamente sin conocer los términos internos de la aseguradora.
*Fuente: Entrevista 1 (CEO), P6.*

### HU-03 — Reportar el siniestro con la información mínima disponible
**Como** asegurado,
**quiero** poder crear el caso con solo número de póliza o documento, placa del vehículo, fecha y ubicación aproximada, tipo de evento y un medio de contacto,
**para** iniciar el proceso incluso si no puedo aportar toda la evidencia de inmediato, especialmente si estoy en una situación de riesgo.
*Fuente: Entrevista 2 (Operaciones), P2.*

### HU-04 — Reporte por un tercero autorizado
**Como** persona autorizada por el asegurado,
**quiero** poder reportar el siniestro cuando el titular no puede hacerlo,
**para** que el caso no quede bloqueado por la imposibilidad del titular.
*Fuente: Entrevista 1 (CEO), P6.*

### HU-05 — Adjuntar evidencias desde la aplicación
**Como** asegurado,
**quiero** adjuntar fotografías del vehículo, daños, entorno, documentos de identidad, licencia, tarjeta de propiedad y demás evidencia solicitada,
**para** que el caso avance sin repetir información por distintos canales.
*Fuente: Entrevista 1 (CEO), P3; Entrevista 2 (Operaciones), P3.*

### HU-06 — Conocer el estado y el siguiente paso del caso
**Como** asegurado,
**quiero** ver una vista clara del avance de mi caso y cuál es el siguiente paso,
**para** no depender de llamadas adicionales para saber qué está pasando.
*Fuente: Entrevista 1 (CEO), P3, P4 (indicador "casos resueltos sin llamadas adicionales").*

### HU-07 — Recibir asistencia coordinada
**Como** asegurado,
**quiero** que se coordine asistencia (por ejemplo grúa) cuando corresponda,
**para** resolver la emergencia inmediata del accidente.
*Fuente: Entrevista 2 (Operaciones), P1.*

## Actor: Operador de Siniestros

### HU-08 — Registrar y validar el caso reportado
**Como** operador,
**quiero** confirmar identidad del reportante, la póliza y el vehículo, y registrar fecha, hora, ubicación, personas involucradas, descripción y daños aparentes,
**para** dejar constituido el expediente inicial del siniestro.
*Fuente: Entrevista 2 (Operaciones), P1.*

### HU-09 — Verificar cobertura y deducible
**Como** operador,
**quiero** verificar la cobertura y el deducible aplicable al caso,
**para** informar correctamente al asegurado y habilitar los siguientes pasos.
*Fuente: Entrevista 2 (Operaciones), P1.*

### HU-10 — Evitar casos duplicados por múltiples canales
**Como** operador,
**quiero** identificar si un mismo siniestro ya fue reportado por el asegurado, el corredor o el taller,
**para** no crear expedientes duplicados.
*Fuente: Entrevista 2 (Operaciones), P6.*

### HU-11 — Asignar el caso según reglas de negocio
**Como** operador o sistema de asignación,
**quiero** asignar el siniestro considerando ciudad, tipo de daño, severidad, cobertura, disponibilidad de proveedores y señales de riesgo,
**para** enviar los casos simples a un flujo digital y los complejos a un ajustador.
*Fuente: Entrevista 2 (Operaciones), P5; Entrevista 1 (CEO), P3.*

### HU-12 — Reasignar un caso conservando el historial
**Como** operador,
**quiero** reasignar un siniestro registrando el historial y la razón del cambio,
**para** mantener trazabilidad de quién fue responsable del caso en cada momento.
*Fuente: Entrevista 2 (Operaciones), P5.*

### HU-13 — Registrar autorizaciones que hoy se dan por teléfono
**Como** operador,
**quiero** registrar formalmente en el sistema las autorizaciones que hoy se otorgan por teléfono,
**para** eliminar autorizaciones no documentadas.
*Fuente: Entrevista 2 (Operaciones), P6.*

### HU-14 — Consultar la vigencia de un presupuesto
**Como** operador,
**quiero** conocer la vigencia de cada presupuesto presentado por un taller,
**para** saber si aún puede aprobarse o requiere actualización.
*Fuente: Entrevista 2 (Operaciones), P7.*

### HU-15 — Reintentar, escalar o reasignar ante un proveedor sin respuesta
**Como** operador,
**quiero** que el sistema permita reintentar, escalar o reasignar cuando un proveedor no responde,
**para** que el asegurado no quede bloqueado por la falla de un proveedor específico.
*Fuente: Entrevista 2 (Operaciones), P9.*

### HU-16 — Auditar la línea de tiempo completa de un caso
**Como** operador o supervisor,
**quiero** consultar quién registró la información, qué cambió, qué evidencias se añadieron, qué cobertura se aplicó, qué proveedor actuó, qué presupuesto fue aprobado, qué comunicación recibió el cliente y qué pago se autorizó,
**para** auditar el caso de extremo a extremo.
*Fuente: Entrevista 2 (Operaciones), P10.*

## Actor: Ajustador

### HU-17 — Recibir casos complejos derivados
**Como** ajustador,
**quiero** recibir los siniestros que requieren revisión especializada,
**para** evaluarlos con el criterio que su severidad o riesgo exige.
*Fuente: Entrevista 1 (CEO), P3; Entrevista 2 (Operaciones), P5.*

### HU-18 — Programar inspección
**Como** ajustador u operador,
**quiero** programar una inspección del vehículo,
**para** continuar el flujo de evaluación del siniestro.
*Fuente: Entrevista 2 (Operaciones), P4 (estado "inspección programada"), P8.*

## Actor: Taller

### HU-19 — Recibir la orden y presentar presupuesto
**Como** taller,
**quiero** recibir la orden del siniestro, presentar el presupuesto y adjuntar el diagnóstico,
**para** solicitar la aprobación de la reparación.
*Fuente: Entrevista 2 (Operaciones), P7.*

### HU-20 — Registrar observaciones, repuestos alternativos y ampliaciones
**Como** taller,
**quiero** registrar observaciones, propuestas de repuestos alternativos o ampliaciones durante la reparación,
**para** que cada cambio quede documentado y sea aprobado por quien corresponde.
*Fuente: Entrevista 2 (Operaciones), P7.*

## Actor: Proveedor de asistencia / grúa

### HU-21 — Recibir y responder solicitudes de asistencia
**Como** proveedor de grúa u otro proveedor de asistencia,
**quiero** recibir la solicitud y que quede registrada mi respuesta (aceptada, rechazada o sin respuesta),
**para** que el operador pueda actuar según corresponda.
*Fuente: Entrevista 2 (Operaciones), P9.*

## Actor: Investigador de Fraude

### HU-22 — Revisar alertas de fraude generadas por reglas o modelos
**Como** investigador de fraude,
**quiero** revisar cada alerta con su tipo, severidad, explicación, datos de origen, fecha y modelo o regla utilizado,
**para** confirmarla, descartarla o solicitar más información dejando la justificación registrada.
*Fuente: Entrevista 3 (Fraude), P4.*

### HU-23 — Consultar señales de riesgo del caso
**Como** investigador de fraude,
**quiero** ver señales como repetición de participantes, vehículos o talleres, pólizas contratadas cerca del evento, ubicaciones incoherentes, fotografías reutilizadas, montos atípicos, versiones contradictorias, patrones de contacto compartidos y antecedentes de reclamos,
**para** evaluar el riesgo del siniestro.
*Fuente: Entrevista 3 (Fraude), P2.*

### HU-24 — Acceder a información ampliada según rol
**Como** investigador de fraude,
**quiero** tener acceso a información ampliada que un operador regular no ve,
**para** cumplir mi función de investigación, quedando mis descargas y consultas sensibles registradas.
*Fuente: Entrevista 3 (Fraude), P7.*

### HU-25 — Relacionar casos sin fusionar expedientes
**Como** investigador de fraude,
**quiero** ver la relación entre siniestros que comparten accidente, teléfono, cuenta bancaria, taller o persona,
**para** detectar patrones sospechosos sin fusionar incorrectamente los expedientes.
*Fuente: Entrevista 3 (Fraude), P8.*

### HU-26 — Consultar el histórico reproducible de una alerta
**Como** investigador de fraude,
**quiero** poder reconstruir meses después por qué un caso recibió una alerta, aunque la regla o el modelo hayan cambiado,
**para** sustentar decisiones e investigaciones posteriores.
*Fuente: Entrevista 3 (Fraude), P10.*

### HU-27 — Configurar y versionar la política de bloqueo por alertas
**Como** investigador de fraude / responsable de la política antifraude,
**quiero** que la política que determina si una alerta bloquea un pago, deriva el caso o solo aumenta la prioridad de revisión sea configurable y quede versionada,
**para** ajustar el tratamiento de riesgo sin perder trazabilidad de qué política aplicó a cada caso.
*Fuente: Entrevista 3 (Fraude), P5.*

## Actor: Supervisor / Gerencia de Operaciones y Dirección (CEO)

### HU-28 — Ver una vista única del caso
**Como** supervisor,
**quiero** una vista única del caso con toda su información,
**para** dar seguimiento sin consultar múltiples canales o repositorios.
*Fuente: Entrevista 1 (CEO), P3.*

### HU-29 — Medir los indicadores de éxito del proceso
**Como** dirección de la compañía,
**quiero** medir tiempo hasta primera asistencia, tiempo hasta decisión, porcentaje de casos resueltos sin llamadas adicionales, satisfacción del cliente, costo operativo por siniestro y pérdidas evitadas por fraude,
**para** evaluar el desempeño del proceso en conjunto.
*Fuente: Entrevista 1 (CEO), P4.*

### HU-30 — Revisar y, si corresponde, corregir una decisión asistida por IA
**Como** supervisor u operador autorizado,
**quiero** poder revisar y anular una recomendación generada por IA (clasificación, priorización, alerta de inconsistencia),
**para** asegurar que ninguna decisión sensible se tome de forma automática sin posibilidad de revisión humana.
*Fuente: Entrevista 1 (CEO), P7, P8.*

## Notas de alcance de esta sección
- Todas las historias corresponden a siniestros vehiculares de daños materiales sin lesiones graves, clientes directos y pólizas vigentes; los casos con heridos, fallecidos, procesos legales o daños masivos quedan fuera del alcance descrito. *Fuente: Entrevista 1 (CEO), P5.*
- No se generaron historias de usuario para seguros de salud u hogar: las entrevistas concentran el caso únicamente en seguros vehiculares. *Fuente: Contexto ficticio del documento.*
