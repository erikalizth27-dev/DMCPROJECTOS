# Cierre de Brechas — Siniestro Fácil (Respuestas de Negocio Simuladas)

> **Naturaleza de este documento:** las tres entrevistas originales son ficticias (material de un caso de estudio). Este documento **simula** una ronda adicional de decisiones de negocio para cerrar los vacíos identificados en `discrepancias.md`. Cada respuesta está marcada como **[SIMULADO]** y no debe confundirse con una cita textual de las entrevistas originales — es una hipótesis de trabajo razonable, redactada como la daría el rol de negocio correspondiente (CEO, Operaciones o Fraude), para poder avanzar la especificación. Se recomienda validarla con el negocio real antes de construir.
>
> Formato: cada punto retoma el vacío tal como quedó numerado en `discrepancias.md`, seguido de la decisión simulada, el rol que la habría emitido y el impacto sobre los entregables ya generados.

---

## 1. Cierre de las tensiones del "Reto para el equipo"

### 1.1 Rapidez de atención frente a control de fraude
**[SIMULADO — CEO / Prevención de Fraude]:** "Para el flujo digital simple, el objetivo es que el asegurado reciba confirmación de cobertura en minutos, no en días. Para lograrlo sin sacrificar control, la validación antifraude en el flujo simple se ejecuta en paralelo y de forma no bloqueante salvo que se dispare una **regla crítica** (identidad no verificable, evidencia reutilizada detectada, o monto que excede el límite de auto-aprobación). Si no hay regla crítica, el caso avanza y cualquier alerta de severidad baja o media queda para revisión posterior sin detener al cliente."
**Impacto:** Define el comportamiento de RF-22 (política configurable) — se agrega la regla de que solo alertas "críticas" son bloqueantes por defecto; las demás son no bloqueantes y se revisan en paralelo.

### 1.2 Experiencia simple frente a evidencia suficiente
**[SIMULADO — Operaciones]:** "El caso se crea con los datos mínimos. A partir de ahí, el sistema define un checklist de evidencia obligatoria según el tipo de evento (por ejemplo, choque con daños materiales requiere fotos del vehículo, del entorno y de la licencia). El caso puede avanzar a 'validando cobertura' con datos mínimos, pero **no puede pasar de 'en evaluación' a 'inspección programada' o 'presupuesto recibido'** sin que el checklist de evidencia obligatoria esté completo."
**Impacto:** Precisa RF-01/RF-07/RF-09 — se agrega la regla de transición de estado condicionada al checklist de evidencia.

### 1.3 Automatización frente a revisión humana
**[SIMULADO — CEO]:** "Se consideran decisiones sensibles: rechazo de cobertura, confirmación de una alerta de fraude, y autorización de cualquier pago. Estas tres nunca las cierra un modelo de IA por sí solo: la IA puede pre-llenar la recomendación, pero un operador, ajustador o investigador humano —según el caso— debe confirmar antes de que el estado cambie. El sistema debe dejar registrado quién confirmó y cuándo."
**Impacto:** Cierra el vacío de RNF-05 — se define la lista cerrada de "decisiones sensibles" (rechazo de cobertura, confirmación de fraude, autorización de pago).

### 1.4 Expediente único frente a múltiples participantes y reclamos relacionados
**[SIMULADO — Prevención de Fraude]:** "Cada siniestro reportado conserva su propio expediente, aunque comparta accidente con otro. La relación se muestra al operador y al investigador como una pestaña de 'casos relacionados', con el criterio de relación (mismo accidente, mismo teléfono, etc.) visible. Ninguna acción de un caso (aprobación, pago) se ejecuta automáticamente sobre el caso relacionado; cada expediente se resuelve de forma independiente, aunque la existencia de la relación puede escalar la severidad de revisión."
**Impacto:** Cierra el vacío de CU-08 / RF-24 — se define la interfaz conceptual ("pestaña de casos relacionados") y la regla de no propagación automática de decisiones entre casos relacionados.

### 1.5 Almacenamiento de originales frente a versiones optimizadas
**[SIMULADO — Prevención de Fraude / Legal]:** "El original de cada evidencia se conserva sin modificación por un mínimo de 5 años desde el cierre del caso, alineado a los plazos típicos de prescripción de reclamos en el sector. Las versiones optimizadas (comprimidas para visualización en la app) pueden regenerarse en cualquier momento a partir del original y no tienen restricción de plazo."
**Impacto:** Cierra el vacío de RNF-03 — agrega el plazo de retención (5 años) al modelo físico (`evidencia.fecha_recepcion` + política de retención).

### 1.6 Procesos síncronos de atención frente a coordinaciones asíncronas con terceros
**[SIMULADO — Operaciones]:** "Para solicitudes de asistencia (grúa), si el proveedor no confirma en 10 minutos, el sistema reintenta con el mismo proveedor una vez; si no hay respuesta en un segundo intento de 10 minutos, escala automáticamente al siguiente proveedor disponible en la zona. Para presupuestos y aprobaciones de taller, el ciclo es asíncrono por naturaleza y no tiene un límite de minutos, pero el caso muestra al asegurado que está 'en espera de proveedor' para que la ausencia de respuesta no se perciba como inacción del sistema."
**Impacto:** Cierra el vacío de RF-17 / RNF-10 — agrega el umbral operativo (10 minutos, un reintento, luego escalamiento automático) exclusivamente para asistencia; los presupuestos quedan explícitamente sin SLA duro.

---

## 2. Cierre de incertidumbres reconocidas por los entrevistados

### 2.1 Política de deduplicación
**[SIMULADO — Operaciones]:** "Un nuevo reporte se considera potencial duplicado de un siniestro existente si coincide la placa del vehículo y la fecha del evento (mismo día). En ese caso, el sistema no crea un caso nuevo automáticamente: presenta al operador el caso existente para que decida si vincula el nuevo reporte como un canal adicional del mismo siniestro o lo registra como un caso distinto."
**Impacto:** Cierra el vacío de RF-13/HU-10 — define el criterio de coincidencia (placa + fecha) y que la decisión final la toma un operador, no el sistema de forma automática.

### 2.2 Umbrales antifraude (bloqueo, derivación, priorización)
**[SIMULADO — Prevención de Fraude]:** "La política versionada usa tres niveles: **crítica** (bloquea el pago hasta revisión — por ejemplo, evidencia con reutilización de imagen confirmada), **alta** (deriva el caso a un investigador antes de continuar, sin bloquear pagos ya en curso de otros casos) y **media/baja** (solo incrementa la prioridad de revisión, el caso sigue su flujo normal). El monto expuesto no cambia el nivel por sí solo, pero sí determina si la revisión la hace un investigador junior o senior."
**Impacto:** Cierra el vacío de RF-22/ALERTA.severidad — da contenido concreto a los tres niveles de severidad ya modelados como enumerado abierto.

### 2.3 Retención de evidencia
Cerrado en el punto 1.5 (5 años desde el cierre del caso).

### 2.4 SLA por región y tipo de siniestro
**[SIMULADO — Operaciones]:** "Para el piloto, se define un único SLA por etapa, sin diferenciar por región todavía (la diferenciación por región queda para la fase de expansión nacional): primera respuesta al reporte, 15 minutos; asignación del caso, 1 hora; programación de inspección cuando aplica, 48 horas; recepción de presupuesto del taller, 5 días hábiles desde la inspección; decisión de autorización, 3 días hábiles desde la recepción del presupuesto."
**Impacto:** Cierra el vacío de RNF (SLA) — aplica solo al piloto de una ciudad; queda pendiente para la fase de expansión la diferenciación por región.

### 2.5 Alcance de integración con talleres
**[SIMULADO — Operaciones]:** "Para el piloto, la integración con el taller cubre: recepción de orden, envío de presupuesto y diagnóstico, notificación de observaciones/repuestos alternativos/ampliaciones, y notificación de estado de reparación (iniciada, lista para entrega). No incluye, en esta fase, integración de facturación electrónica ni inventario de repuestos del taller."
**Impacto:** Acota RF-15/RF-16/RF-19(taller) al alcance del piloto; deja explícito qué no se integra en esta primera versión.

---

## 3. Cierre de vacíos de dato / atributo

| Vacío | Decisión simulada | Rol |
|---|---|---|
| Nombre del asegurado | Se captura como campo obligatorio adicional a documento y contacto, ya que es necesario para comunicación y documentos legales de reparación. | **[SIMULADO — Operaciones]** |
| Nombre del proveedor (taller/grúa) | Se captura como campo obligatorio al dar de alta al proveedor en el catálogo interno. | **[SIMULADO — Operaciones]** |
| Tipo de documento del asegurado | Catálogo cerrado inicial: cédula/DNI, pasaporte, carné de extranjería — alineado a los documentos de identidad que ya usa la aseguradora para emitir pólizas. | **[SIMULADO — Operaciones]** |
| Definición de "persona autorizada" para reportar | Se acepta el reporte de un tercero declarando su relación con el asegurado (familiar, dependiente, testigo) y un dato de contacto; no se exige documento notarial para el reporte inicial, pero sí para autorizar pagos o cambios de cobertura más adelante. | **[SIMULADO — CEO]** |
| Subestados internos del siniestro | Se definen como notas operativas libres dentro de cada estado principal (por ejemplo, dentro de "en evaluación": "esperando fotos adicionales", "esperando declaración de tercero"), sin cambiar el catálogo cerrado de estados visibles al cliente. | **[SIMULADO — Operaciones]** |
| Catálogo cerrado de canales de reporte | Teléfono, correo, aplicación móvil, corredor — estos cuatro canales, sin agregar otros en el piloto. | **[SIMULADO — Operaciones]** |
| Criterio de "monto atípico" | Un monto se marca atípico si excede en más de 50% el promedio histórico de siniestros con el mismo tipo de daño y tipo de vehículo. | **[SIMULADO — Prevención de Fraude]** |

**Impacto:** Estos cierres permiten quitar la marca `[pendiente]` de los atributos correspondientes en el modelo lógico y físico (`asegurado.nombre`, `asegurado.tipo_documento`, `proveedor.nombre`) y precisar los catálogos `canal_origen` y `señal_riesgo` (monto_atipico).

---

## 4. Cierre de decisiones técnicas

**[SIMULADO — Arquitectura de Soluciones, a partir de la instrucción del CEO de tolerar integraciones lentas y de partir con un piloto acotado]:**

| Decisión técnica | Definición simulada |
|---|---|
| Motor de base de datos | Base de datos relacional (PostgreSQL) para el núcleo transaccional (pólizas, siniestros, presupuestos, pagos, alertas), dado que el modelo tiene fuertes relaciones e integridad referencial. |
| Almacenamiento de evidencia binaria | Los archivos originales (fotos, documentos) se almacenan en un servicio de almacenamiento de objetos; la base de datos relacional guarda únicamente la referencia (URI), el hash y los metadatos — ya reflejado como `contenido_original_uri` en el modelo físico. |
| Particionamiento / archivado | Sin particionamiento para el piloto (una ciudad, volumen acotado); se evaluará archivado histórico de siniestros cerrados hace más de 5 años cuando se alcance escala nacional, alineado al plazo de retención de evidencia (ver 1.5). |
| Integraciones (mapas, mensajería, pagos) | Se seleccionan mediante proveedores comerciales estándar de mercado a definir en la fase de arquitectura detallada; no se fija un proveedor específico en esta etapa porque el CEO solo mencionó la categoría de dependencia, no un proveedor. |

**Impacto:** Cierra la sección 4 de `discrepancias.md`; el modelo físico puede pasar de "pendiente" a "definido para el piloto", dejando explícito que la selección de proveedores concretos de mensajería/pagos/mapas queda para una etapa posterior de arquitectura.

---

## 5. Resumen de brechas que permanecen abiertas después de esta simulación

Aun con las respuestas simuladas, dos puntos requieren validación real con el negocio antes de construir (no se simulan porque exceden lo que un cierre de brechas razonable puede asumir sin datos reales del negocio):

1. **Selección de proveedores tecnológicos concretos** (pasarela de pagos, proveedor de mapas, proveedor de mensajería) — depende de contratos y condiciones comerciales reales de Seguros Horizonte, no de una decisión de producto.
2. **Cifras reales de SLA y umbrales de fraude** — los valores del punto 2.2, 2.4 y 3 (monto atípico) son hipótesis de trabajo razonables para poder diseñar el sistema; deben calibrarse con datos históricos reales de los ~18,000 siniestros mensuales antes de fijarse como reglas de producción.

## 6. Nota de trazabilidad
Todo lo anterior está marcado **[SIMULADO]** y con el rol que emitiría la decisión, precisamente para no mezclarlo con las citas textuales de `01_historias_usuario.md` a `08_modelo_fisico.md`, que sí provienen de las entrevistas originales. Se recomienda, al actualizar los demás entregables con estas decisiones, mantener la cita `[SIMULADO — cierre_de_brechas.md, sección X]` en lugar de atribuirlas a una entrevista que no las contiene.
