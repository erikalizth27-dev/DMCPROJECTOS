# Requerimientos Funcionales — Siniestro Fácil

> Cada requerimiento cita su fuente. Ningún requerimiento fue inferido más allá de lo dicho por los entrevistados; los aspectos no definidos se listan como pendientes en `discrepancias.md`.

## RF-01 Registro de siniestro
El sistema debe permitir crear un siniestro capturando, como mínimo, número de póliza o documento del asegurado, placa del vehículo, fecha y ubicación aproximada, tipo de evento y un medio de contacto, sin exigir evidencia adicional en ese momento. *(Entrevista 2, P2)*

## RF-02 Reporte multicanal / multiactor
El sistema debe permitir que el reporte sea iniciado por el asegurado o por una persona autorizada cuando el titular no pueda hacerlo. *(Entrevista 1, P6)*

## RF-03 Confirmación de identidad, póliza y vehículo
El sistema debe permitir confirmar la identidad del reportante, la póliza y el vehículo al momento del registro. *(Entrevista 2, P1)*

## RF-04 Captura de datos del evento
El sistema debe registrar fecha, hora, ubicación, personas involucradas, descripción del hecho y daños aparentes. *(Entrevista 2, P1)*

## RF-05 Verificación de cobertura y deducible
El sistema debe permitir verificar la cobertura y el deducible aplicables a un siniestro. *(Entrevista 2, P1)*

## RF-06 Coordinación de asistencia
El sistema debe permitir solicitar y dar seguimiento a la asistencia (por ejemplo, grúa) asociada a un siniestro. *(Entrevista 2, P1)*

## RF-07 Gestión de evidencia
El sistema debe permitir adjuntar evidencia (fotografías del vehículo, daños, entorno, documentos de identidad, licencia, tarjeta de propiedad, declaración del conductor, datos de terceros, denuncia cuando aplique), vinculando cada evidencia al siniestro, al momento de captura y, cuando sea posible, a ubicación y dispositivo. *(Entrevista 2, P3)*

## RF-08 Conservación de evidencia original e inmutable
El sistema debe conservar el contenido original de cada evidencia, su hash, metadatos disponibles, fecha de recepción, fuente, transformaciones realizadas y versiones derivadas, sin perder el original al generar versiones optimizadas. *(Entrevista 3, P3; tabla de evidencias — restricción "evidencia inmutable")*

## RF-09 Gestión de estados del siniestro
El sistema debe representar los estados: reportado, validando cobertura, asistencia coordinada, evidencia pendiente, en evaluación, inspección programada, presupuesto recibido, autorizado, observado, rechazado, en reparación, listo para entrega, indemnizado y cerrado, además de subestados internos no visibles para el cliente. *(Entrevista 2, P4)*

## RF-10 Vista de estado y siguiente paso para el asegurado
El sistema debe mostrar al asegurado el estado de su caso y el siguiente paso, sin exponer los subestados internos. *(Entrevista 1, P3, P6; Entrevista 2, P4)*

## RF-11 Asignación de casos
El sistema debe asignar el siniestro considerando ciudad, tipo de daño, severidad, cobertura, disponibilidad de proveedores y señales de riesgo, dirigiendo casos simples a un flujo digital y casos complejos a un ajustador. *(Entrevista 2, P5; Entrevista 1, P3)*

## RF-12 Reasignación con historial
El sistema debe permitir reasignar un caso conservando el historial y la razón de cada reasignación. *(Entrevista 2, P5)*

## RF-13 Identificación de posibles duplicados
El sistema debe permitir identificar cuando un mismo siniestro fue reportado por más de un canal o actor (asegurado, corredor, taller), evitando la creación de expedientes duplicados. *(Entrevista 2, P6)*

## RF-14 Registro formal de autorizaciones
El sistema debe registrar formalmente cualquier autorización otorgada durante el proceso (por ejemplo, las que hoy se dan por teléfono), sustituyendo la autorización no documentada. *(Entrevista 2, P6)*

## RF-15 Gestión de presupuestos de taller
El sistema debe permitir que un taller reciba la orden, presente presupuesto y adjunte diagnóstico, y que el sistema registre la vigencia del presupuesto. *(Entrevista 2, P7)*

## RF-16 Registro de observaciones, repuestos alternativos y ampliaciones
El sistema debe permitir registrar observaciones, propuestas de repuestos alternativos o ampliaciones durante la reparación, indicando quién aprobó cada cambio. *(Entrevista 2, P7)*

## RF-17 Gestión de solicitudes a proveedores con reintento y escalamiento
El sistema debe registrar cada intento de comunicación con un proveedor, distinguiendo entre solicitud aceptada, rechazada o sin respuesta, y debe permitir reintentar, escalar o reasignar cuando el proveedor no responde. *(Entrevista 2, P9)*

## RF-18 Auditoría / línea de tiempo del caso
El sistema debe mantener una línea de tiempo completa del caso: quién registró información, qué cambió, qué evidencias se añadieron, qué cobertura se aplicó, qué proveedor actuó, qué presupuesto fue aprobado, qué comunicación recibió el cliente y qué pago fue autorizado. *(Entrevista 2, P10)*

## RF-19 Generación de alertas de fraude
El sistema debe generar alertas de fraude con tipo, severidad, explicación, datos que la originaron, fecha y modelo o regla utilizado. *(Entrevista 3, P4)*

## RF-20 Señales de riesgo antifraude
El sistema debe identificar señales de riesgo tales como repetición de participantes, vehículos o talleres; pólizas contratadas cerca del evento; ubicaciones incoherentes; fotografías reutilizadas; montos atípicos; versiones contradictorias; patrones de contacto compartidos; y antecedentes de reclamos, distinguiendo señales determinísticas de señales generadas por modelos. *(Entrevista 3, P2)*

## RF-21 Gestión del ciclo de vida de una alerta
El sistema debe permitir que un investigador confirme, descarte o solicite más información sobre una alerta, registrando la justificación de la decisión. *(Entrevista 3, P4)*

## RF-22 Política configurable de bloqueo por alertas
El sistema debe permitir configurar y versionar la política que determina si una alerta bloquea temporalmente un pago, deriva el caso a revisión, o solo aumenta la prioridad de revisión, según la combinación de señales y el monto expuesto. *(Entrevista 3, P5)*

## RF-23 Control de acceso por rol a información sensible
El sistema debe restringir el acceso a información ampliada de fraude por rol y necesidad, y debe registrar las descargas de evidencia y las consultas sensibles. *(Entrevista 3, P7)*

## RF-24 Relación entre casos sin fusión de expedientes
El sistema debe permitir relacionar siniestros que comparten accidente, teléfono, cuenta bancaria, taller o persona, sin fusionar los expedientes correspondientes. *(Entrevista 3, P8)*

## RF-25 Conservación de valor declarado y valor normalizado
El sistema debe conservar por separado el valor declarado originalmente (por ejemplo, nombre o placa como fue ingresado) y su valor normalizado, sin reemplazar silenciosamente uno por otro. *(Entrevista 3, P9)*

## RF-26 Reproducibilidad de alertas y decisiones
El sistema debe permitir reconstruir, en cualquier momento posterior, por qué un caso recibió una alerta específica, incluyendo la versión de la regla o modelo utilizado, los datos de entrada y la evidencia de la revisión humana, aun si la regla o el modelo ya cambiaron. *(Entrevista 3, P10)*

## RF-27 Uso de IA como apoyo, no como decisión final
El sistema debe permitir que la IA clasifique fotografías, detecte documentos faltantes, resuma declaraciones, priorice casos y sugiera inconsistencias, sin que estas salidas se traten como una decisión definitiva; toda decisión sensible debe ser revisable por una persona y quedar explicada. *(Entrevista 1, P7, P8; Entrevista 3, P6)*

## RF-28 Comparación visual y detección de reutilización de imágenes
El sistema debe apoyarse en IA para comparar visualmente daños y detectar posible reutilización de fotografías, así como extraer datos y agrupar relaciones sospechosas entre casos. *(Entrevista 3, P6)*

## RF-29 Panel de indicadores de gestión
El sistema debe exponer indicadores de tiempo hasta primera asistencia, tiempo hasta decisión, porcentaje de casos resueltos sin llamadas adicionales, satisfacción del cliente, costo operativo por siniestro y pérdidas evitadas por fraude. *(Entrevista 1, P4)*

## RF-30 Vista única del caso
El sistema debe ofrecer una vista única y consolidada de cada siniestro para uso interno. *(Entrevista 1, P3)*

## RF-31 Alcance de siniestros elegibles
El sistema debe operar sobre siniestros vehiculares de daños materiales sin lesiones graves, de clientes directos y con pólizas vigentes; los casos con heridos, fallecidos, procesos legales o daños masivos deben derivarse a rutas especializadas fuera del alcance de esta primera versión. *(Entrevista 1, P5)*

## RF-32 Tolerancia a integraciones externas no disponibles
El sistema debe seguir operando cuando alguna integración externa (pólizas, red de talleres, proveedores de grúa, ajustadores, mapas, mensajería, medios de pago) esté temporalmente indisponible o responda con lentitud. *(Entrevista 1, P9)*

## RF-33 Piloto acotado
El sistema debe poder desplegarse inicialmente en una sola ciudad y con un grupo controlado de talleres, cubriendo el flujo completo desde el reporte hasta la autorización de reparación. *(Entrevista 1, P10)*
