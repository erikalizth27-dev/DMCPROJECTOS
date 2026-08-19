# Cierre de Brechas — Stock Único (NovaRetail)

> **Naturaleza de este documento:** las entrevistas originales (`03_retail_stock_unico.md`) son ficticias, construidas para el ejercicio. Este documento **simula una sesión de cierre de brechas** con los mismos roles de negocio (CEO, Supply Chain, E-commerce/Tiendas) y roles adicionales no entrevistados originalmente (Pagos, Legal/Cumplimiento, Logística, Finanzas), con el fin de resolver los vacíos listados en `07_discrepancias.md`.
>
> **Estas respuestas son simuladas, no reales.** Se documentan con el mismo nivel de trazabilidad que las entrevistas originales (rol + respuesta) para que puedan tratarse como una fuente formal más y propagarse a los demás entregables. Cualquier cifra aquí definida debe ser confirmada por el negocio real antes de construir el sistema.

---

## 1. Cierre de reglas de negocio no definidas (D-01 a D-10)

### D-01 — Fórmula exacta de disponibilidad
**Responde:** Javier Montalvo, Supply Chain e Inventarios (simulado)

> "Definimos disponible_para_venta = stock_físico − reservado − comprometido − bloqueado − dañado − stock_de_seguridad. El stock de seguridad se parametriza por SKU y ubicación, con un valor por defecto del 5% del stock físico para tienda y 2% para centro de distribución. Para modalidad de retiro en tienda, además excluimos el stock marcado como 'no apto para venta digital'. Esta fórmula es la misma para todas las categorías del MVP (tecnología y pequeños electrodomésticos); no habrá fórmulas distintas por campaña en esta primera versión, solo el parámetro de stock de seguridad puede subir temporalmente durante una campaña."

**Decisión de cierre:** RF-04 se actualiza: la fórmula queda fija como se describe arriba; el stock de seguridad es un parámetro configurable por SKU/ubicación con valores por defecto 5% (tienda) y 2% (centro de distribución), ajustable manualmente durante campañas.

---

### D-02 — Duración de expiración de la reserva en checkout
**Responde:** Paola Fernández, E-commerce y Tiendas (simulado)

> "La reserva creada al iniciar el pago debe expirar a los 10 minutos si el pago no se confirma. Si el medio de pago está 'procesando' (respuesta asíncrona), extendemos la reserva una sola vez por 5 minutos adicionales, no de forma indefinida."

**Decisión de cierre:** RF-11 se actualiza: expiración base de 10 minutos, con una extensión única de 5 minutos ante pago en estado "procesando".

---

### D-03 — Reglas de transición de estado de una reserva
**Responde:** Javier Montalvo, Supply Chain e Inventarios (simulado)

> "El flujo es: creada → confirmada (cuando el pago se aprueba) → puede pasar a liberada (si vence sin pago, si el cliente cancela, o si no se recoge dentro del plazo) o a trasladada (si Preparación reporta faltante y se reasigna a otra ubicación, ver D-09). Una reserva vencida no puede reactivarse; si el cliente vuelve a intentar, se crea una reserva nueva."

**Decisión de cierre:** RF-09 se actualiza con el diagrama de estados: `creada → {confirmada | liberada}`, `confirmada → {liberada | trasladada}`. Estado `vencida` es terminal.

---

### D-04 — Plazo de retiro en tienda antes de liberar la reserva
**Responde:** Paola Fernández, E-commerce y Tiendas (simulado)

> "El plazo estándar es de 5 días calendario desde que el pedido queda listo para recojo. Enviamos un recordatorio al día 3 y liberamos automáticamente al día 6 si no hubo retiro."

**Decisión de cierre:** RF-12 se actualiza: plazo de recojo = 5 días calendario, con recordatorio al día 3 y liberación automática al día 6.

---

### D-05 — Criterio operativo de "degradación controlada"
**Responde:** Paola Fernández, E-commerce y Tiendas (simulado), con validación de Claudia Rivas, CEO (simulado)

> **Paola:** "Cuando el sistema detecta que no puede confirmar disponibilidad en tiempo real (por ejemplo, la réplica tiene más de 2 minutos de atraso), mostramos un rango de disponibilidad ('pocas unidades' en vez de un número exacto) en lugar de ocultar el producto o mostrar un número que podría ser incorrecto. El checkout sigue exigiendo confirmación de reserva síncrona incluso en este modo; ahí no degradamos."
> **Claudia:** "Estoy de acuerdo. Prefiero mostrar menos precisión que mentirle al cliente. Lo que no negocio es que el checkout final siga siendo una operación controlada y confirmada."

**Decisión de cierre:** RNF-07 y RF-32 se actualizan: umbral de "vista degradada" = réplica de disponibilidad con más de 2 minutos de atraso → se muestra disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en vez de cantidad exacta; la confirmación de reserva en checkout nunca se degrada, siempre es síncrona y consistente.

---

### D-06 — Qué constituye "vender de manera segura" con integración retrasada
**Responde:** Claudia Rivas, CEO (simulado)

> "Significa dos cosas: primero, que el catálogo y la navegación nunca se caen aunque una integración de inventario esté lenta — para eso usamos la vista degradada de la que habla Paola. Segundo, que la reserva y el pago, que sí son transaccionales, se rechazan de forma explícita y clara si no podemos garantizar consistencia, en vez de aceptar una compra que después no podemos cumplir. Prefiero decirle 'inténtalo en un momento' a un cliente antes que confirmarle algo que no le puedo entregar."

**Decisión de cierre:** RF-31 se actualiza: catálogo/navegación se mantienen disponibles en modo degradado (ver D-05); reserva y pago se bloquean explícitamente (mensaje claro al cliente) si el sistema no puede garantizar consistencia en la operación transaccional, en vez de aceptarla de forma optimista.

---

### D-07 — Compensación cuando el pago se aprueba sin pedido asociado
**Responde:** rol simulado adicional — Gerente de Medios de Pago (no entrevistado originalmente)

> "Si un pago queda aprobado sin pedido asociado por más de 15 minutos, se dispara automáticamente una reversión (reembolso) y se notifica al cliente. Estos casos también deben quedar en una cola de revisión para el equipo de operaciones, aunque se hayan revertido automáticamente."

**Decisión de cierre:** RF-15 se amplía: SLA de correlación pago-pedido = 15 minutos; vencido ese plazo sin pedido asociado, se ejecuta reversión automática y se registra el caso para revisión operativa.

---

### D-08 — Nivel de identificación de unidades serializadas
**Responde:** Javier Montalvo, Supply Chain e Inventarios (simulado)

> "Para el MVP (tecnología y pequeños electrodomésticos) sí necesitamos número de serie porque son productos de alto valor con garantía asociada. La unidad serializada se identifica al momento de la recepción en tienda o centro de distribución, y se vincula a la reserva únicamente en el momento de la preparación del pedido (no antes), para no perder flexibilidad de asignación entre unidades equivalentes."

**Decisión de cierre:** RF-02 se actualiza: en el MVP, los productos de tecnología y pequeños electrodomésticos SÍ requieren número de serie; la vinculación serie-reserva ocurre en el momento de preparación (UC-05), no en la creación de la reserva.

---

### D-09 — Reglas de partición de pedidos multiproducto
**Responde:** Paola Fernández, E-commerce y Tiendas (simulado)

> "La regla por defecto es: intentamos despachar todo desde una sola ubicación. Si ninguna ubicación tiene todo el carrito, dividimos el pedido en sub-pedidos por ubicación y se lo mostramos al cliente como envíos separados con fechas de entrega independientes, dejando que decida si acepta el envío dividido o retira solo lo disponible en una tienda."

**Decisión de cierre:** RF-14 se actualiza: prioridad a despacho único; si no es posible, se generan sub-pedidos por ubicación con fechas independientes y el cliente decide si acepta el envío dividido.

---

### D-10 — Flujo posterior a "listo para despacho" en modalidad domicilio
**Responde:** rol simulado adicional — Gerente de Logística y Última Milla (no entrevistado originalmente)

> "Una vez que el pedido está embalado y marcado como listo, el operador logístico lo recoge, lo escanea como recibido, y a partir de ahí nosotros gestionamos el estado de tránsito y entrega final con nuestro propio sistema de ruteo. Lo único que Stock Único necesita recibir de vuelta es la confirmación de entrega o la excepción de entrega fallida (dirección incorrecta, cliente ausente), para actualizar el estado del pedido y, si corresponde, liberar cualquier compromiso pendiente."

**Decisión de cierre:** Se agrega UC-08 (versión ampliada): tras el despacho, Stock Único recibe eventos de "recibido por logística", "en tránsito" (opcional/informativo) y "entregado" o "entrega fallida" desde el sistema de ruteo del operador logístico; solo estos dos últimos estados actualizan el estado visible del pedido al cliente.

---

## 2. Cierre de incertidumbres declaradas por los entrevistados originales

### Autoridad por sistema (quién es la fuente de verdad de cada dato)
**Responde:** Claudia Rivas, CEO (simulado), con Javier Montalvo (simulado)

> **Claudia:** "Quiero una regla simple: cada dato tiene un único dueño."
> **Javier:** "Entonces: Stock Único es la fuente de verdad para saldo de inventario, reservas y disponibilidad. El sistema de pagos es dueño del estado del pago. El sistema de punto de venta sigue siendo dueño de las ventas de mostrador, pero nos notifica el movimiento a nosotros en tiempo real. El ERP de proveedores sigue siendo dueño de las órdenes de compra; nosotros solo reflejamos la recepción."

**Decisión de cierre:** Se documenta como regla de arquitectura: Stock Único = autoridad de inventario/reserva/disponibilidad; Sistema de Pagos = autoridad de estado de pago; POS = autoridad de venta de mostrador (evento reflejado, no reescrito); ERP de proveedores = autoridad de compras (Stock Único solo refleja recepción).

### Consistencia fuerte vs. eventual
**Ya cerrado mediante D-05/D-06:** catálogo/disponibilidad = eventual (tolerancia de hasta 2 minutos); reserva/pago = fuerte (síncrona).

---

## 3. Cierre de requerimientos no funcionales antes ausentes

**Responde:** rol simulado adicional — Gerente de Tecnología / Arquitectura (no entrevistado originalmente), validado por Claudia Rivas (simulado)

> "Definimos: disponibilidad objetivo del sistema de checkout y reserva del 99.9% mensual, con degradación aceptada (no caída total) durante picos de campaña. RTO de 1 hora y RPO de 5 minutos para los servicios transaccionales de reserva y pedido. Todo dato personal del cliente se cifra en tránsito y en reposo, y el acceso del personal de preparación se limita por rol, tal como ya se había definido. Cumplimos la normativa peruana de protección de datos personales vigente para el tratamiento de datos de clientes."

**Decisión de cierre — nuevos RNF:**
- **RNF-15:** Disponibilidad objetivo de checkout/reserva del 99.9% mensual.
- **RNF-16:** RTO de 1 hora y RPO de 5 minutos para servicios transaccionales de reserva y pedido.
- **RNF-17:** Cifrado de datos personales del cliente en tránsito y en reposo.
- **RNF-18:** Cumplimiento de la normativa peruana de protección de datos personales.

---

## 4. Cierre de alcance (roles no entrevistados originalmente)

### Finanzas — costo de preparación por pedido
**Responde:** rol simulado adicional — Gerente de Finanzas (no entrevistado originalmente)

> "El costo de preparación por pedido debe calcularse como tiempo de preparación × costo por hora del personal asignado, más un costo fijo de empaque por pedido. Necesitamos este dato desagregado por tienda para negociar la compensación entre canal digital y tienda física."

**Decisión de cierre:** RF-34 se amplía: el costo de preparación por pedido se calcula como (tiempo de preparación × costo/hora del personal) + costo fijo de empaque, desagregado por ubicación.

### Legal/Cumplimiento — protección de datos
**Responde:** rol simulado adicional — Oficial de Cumplimiento (no entrevistado originalmente)

> "Confirmamos que aplica la Ley de Protección de Datos Personales del Perú. El personal de tienda solo debe ver nombre y últimos dígitos de contacto para validar el retiro, nunca el detalle completo de contacto o medios de pago."

**Decisión de cierre:** RNF-08 se amplía: en retiro en tienda, el personal solo visualiza nombre del cliente y los últimos dígitos del medio de contacto usado para validar identidad.

---

## 5. Resumen de decisiones de cierre (para propagar a los demás entregables)

| ID | Decisión de cierre | Documentos a actualizar |
|---|---|---|
| D-01 | Fórmula de disponibilidad fija + stock de seguridad parametrizable (5%/2%) | RF-04, HU-01, modelo lógico (SaldoInventario) |
| D-02 | Expiración de reserva: 10 min + extensión única de 5 min | RF-11, HU-09 |
| D-03 | Máquina de estados de reserva cerrada | RF-09, HU-07, modelo lógico (Reserva) |
| D-04 | Plazo de recojo: 5 días, recordatorio día 3, liberación día 6 | RF-12, HU-10, UC-07 |
| D-05 | Umbral de vista degradada: 2 min de atraso en réplica | RNF-07, RF-32, UC-12 |
| D-06 | Reserva/pago se rechazan explícitamente en modo degradado, catálogo se mantiene | RF-31, UC-12 |
| D-07 | SLA de reversión de pago sin pedido: 15 min | RF-15, UC-03 |
| D-08 | Número de serie obligatorio en MVP, vinculado en preparación | RF-02, modelo lógico/físico |
| D-09 | Partición en sub-pedidos por ubicación con decisión del cliente | RF-14, HU-12 |
| D-10 | Flujo de eventos con operador logístico tras despacho | UC-08 |
| Autoridad por sistema | Reglas de dueño de dato definidas | Modelo conceptual, RNF de integración |
| RNF nuevos | 99.9% disponibilidad, RTO 1h/RPO 5min, cifrado, normativa peruana | RNF (nuevos RNF-15 a RNF-18) |
| Finanzas | Fórmula de costo de preparación | RF-34 |
| Legal | Datos mínimos visibles en retiro en tienda | RNF-08 |

---

## Nota de autovalidación
Todas las respuestas de esta sesión son **simuladas** y quedan claramente atribuidas a un rol (existente en las entrevistas originales o marcado como "rol simulado adicional"). Se recomienda, en un proyecto real, reemplazar cada respuesta simulada por la validación efectiva del área correspondiente antes de congelar el alcance del MVP. Ningún vacío de `07_discrepancias.md` fue cerrado inventando una decisión sin atribución de rol — cada cierre indica quién (simuladamente) lo decidió.

¿Deseas que actualice ahora los archivos `01` a `06` incorporando estas decisiones de cierre (por ejemplo, marcando los RF/HU/UC afectados como "cerrado" con la nueva regla), o prefieres mantener este documento como una capa adicional de trazabilidad sin modificar los entregables originales?
