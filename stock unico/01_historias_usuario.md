# Historias de Usuario — Stock Único (NovaRetail)

> Fuente única: `03_retail_stock_unico.md`. Cada historia referencia el origen entre paréntesis con el formato `(Entrevista-Pregunta)`. No se incluyen historias sin trazabilidad explícita a una afirmación del input.

## Convención de trazabilidad
- **CEO-n**: Entrevista 1, Claudia Rivas, pregunta n
- **SC-n**: Entrevista 2, Javier Montalvo (Supply Chain e Inventarios), pregunta n
- **EC-n**: Entrevista 3, Paola Fernández (E-commerce y Tiendas), pregunta n
- **EV**: Tabla "Evidencias iniciales extraídas de las entrevistas"

---

## Bloque A — Disponibilidad e inventario

### HU-01 — Disponibilidad como interpretación única
**Como** responsable de operaciones de NovaRetail,
**quiero** que el sistema calcule la disponibilidad como stock utilizable menos reservas y compromisos, considerando un stock de seguridad,
**para** tener una única interpretación operativa de "disponible para vender" en lugar de que cada sistema calcule algo distinto.
*Fuente: SC-3, CEO-2*

### HU-02 — Segmentación de estados de inventario
**Como** sistema de inventario,
**quiero** representar por SKU y ubicación el stock físico, disponible, reservado, comprometido, bloqueado, dañado, en tránsito y pendiente de recepción,
**para** reflejar fielmente los distintos estados que hoy conviven en la operación.
*Fuente: SC-1*

### HU-03 — Registro de movimientos desde múltiples orígenes
**Como** sistema de inventario,
**quiero** registrar movimientos provenientes de ventas en caja, pedidos web, recepciones de proveedores, transferencias, devoluciones, anulaciones, conteos, ajustes, daños y robos, ya sea en tiempo real o por lotes,
**para** mantener actualizado el saldo de inventario desde cualquier origen.
*Fuente: SC-2*

### HU-04 — Inventario en tránsito no disponible
**Como** sistema de inventario,
**quiero** que el inventario en tránsito no se muestre como disponible hasta su recepción,
**para** evitar prometer unidades que aún no están en la ubicación de despacho.
*Fuente: SC-8*

### HU-05 — Conteos y ajustes con evidencia
**Como** usuario autorizado de inventario,
**quiero** registrar conteos y ajustes conservando motivo, usuario y evidencia cuando el stock físico no coincide con el sistema,
**para** investigar la diferencia sin perder el historial ni la causa del problema.
*Fuente: SC-6*

### HU-06 — Auditoría de cada cambio de cantidad
**Como** gerente de Supply Chain,
**quiero** auditar cada cambio de cantidad con evento de origen, documento relacionado, usuario o sistema, momento, cantidad anterior, cantidad nueva y razón, incluyendo la secuencia de eventos,
**para** detectar llegadas duplicadas o eventos fuera de orden.
*Fuente: SC-10*

---

## Bloque B — Reservas

### HU-07 — Reserva como asignación temporal controlada
**Como** sistema de inventario,
**quiero** registrar cada reserva con origen, cantidad, ubicación, fecha de creación, expiración y estado,
**para** administrar su ciclo de vida: confirmar, liberar, vencer o trasladar a otra ubicación según reglas controladas.
*Fuente: SC-4*

### HU-08 — Reserva idempotente ante reintentos
**Como** sistema de checkout,
**quiero** aplicar control de concurrencia y operaciones idempotentes al crear una reserva,
**para** que un reintento del checkout no genere una reserva adicional sobre la misma unidad.
*Fuente: SC-5, EC-8*

### HU-09 — Momento de creación de la reserva
**Como** cliente,
**quiero** que el producto se reserve solo cuando inicio el pago o confirmo el pedido, con una expiración corta,
**para** que visitar la página no bloquee inventario que otros clientes podrían comprar.
*Fuente: EC-2*

### HU-10 — Liberación de reserva no recogida
**Como** sistema de retiro en tienda,
**quiero** liberar la reserva si el cliente no recoge el pedido dentro del plazo,
**para** devolver esas unidades a disponibilidad.
*Fuente: EC-6*

---

## Bloque C — Checkout, pago y pedido

### HU-11 — Información del checkout
**Como** cliente,
**quiero** ver en el checkout los productos, cantidades, ubicación candidata, modalidad de entrega, costo, fecha prometida y vigencia de la oferta,
**para** decidir mi compra con información clara antes de pagar.
*Fuente: EC-3*

### HU-12 — Resolución de carritos multiproducto
**Como** sistema de checkout,
**quiero** decidir si los productos de un carrito con varios ítems salen juntos, desde ubicaciones distintas, o si se propone una alternativa,
**para** completar el pedido de forma coherente con la disponibilidad real.
*Fuente: EC-3*

### HU-13 — Correlación entre intento, pago, pedido y reserva
**Como** sistema de checkout,
**quiero** correlacionar el intento de compra, el pago, el pedido y la reserva,
**para** que un pago aprobado no termine sin pedido asociado ni una reserva confirmada quede sin trazabilidad.
*Fuente: EC-8*

### HU-14 — Promesa de entrega confiable
**Como** cliente,
**quiero** conocer una promesa confiable antes de pagar (si recibiré hoy, mañana, o si puedo recoger en una tienda determinada),
**para** decidir mi compra con expectativas claras.
*Fuente: CEO-6*

### HU-15 — Comunicación ante cambio de promesa
**Como** cliente,
**quiero** ser notificado y recibir alternativas cuando cambia la promesa de entrega,
**para** no enfrentar una cancelación sin explicación ni opciones.
*Fuente: CEO-6, EC-5*

---

## Bloque D — Asignación de ubicación y preparación en tienda

### HU-16 — Selección de ubicación de despacho
**Como** sistema de asignación de pedidos,
**quiero** elegir la ubicación considerando disponibilidad, distancia al cliente, capacidad de preparación, horario, costo, prioridad de tienda, fecha prometida y restricciones del producto,
**para** asignar cada pedido a la ubicación más adecuada.
*Fuente: SC-7*

### HU-17 — Tarea de preparación en tienda
**Como** preparador de tienda,
**quiero** recibir una tarea de preparación cuando se confirma el pedido, validar SKU y cantidad, embalar y marcar listo para despacho o recojo,
**para** completar el ciclo de preparación del pedido.
*Fuente: EC-4*

### HU-18 — Cola priorizada con datos mínimos necesarios
**Como** preparador de tienda,
**quiero** ver una cola priorizada de tareas con ubicación interna del producto, tiempo objetivo y una forma simple de escanear el SKU, sin ver datos personales del cliente que no necesite,
**para** preparar pedidos eficientemente respetando la privacidad del cliente.
*Fuente: EC-7*

### HU-19 — Gestión de faltante en preparación
**Como** preparador de tienda,
**quiero** registrar una excepción cuando no encuentro una unidad reservada,
**para** que el sistema busque otra ubicación y recalcule la promesa en lugar de cancelar directamente.
*Fuente: EC-5*

### HU-20 — Opciones al cliente ante un faltante
**Como** cliente,
**quiero** recibir opciones (nueva fecha, cambio de tienda, producto sustituto o devolución) cuando ocurre un faltante,
**para** decidir cómo continuar en lugar de recibir solo una cancelación.
*Fuente: EC-5*

---

## Bloque E — Retiro en tienda y despacho

### HU-21 — Retiro en tienda con código
**Como** cliente,
**quiero** elegir una tienda con disponibilidad, recibir una promesa y un código de recojo cuando el pedido esté listo,
**para** retirar mi pedido de forma controlada.
*Fuente: EC-6*

### HU-22 — Validación de retiro
**Como** sistema de retiro en tienda,
**quiero** validar quién retira el pedido y registrar la entrega,
**para** dejar constancia formal de la entrega y evitar entregas indebidas.
*Fuente: EC-6*

---

## Bloque F — Transferencias entre ubicaciones

### HU-23 — Registro de transferencias
**Como** sistema de inventario,
**quiero** registrar cada transferencia con origen, destino, unidades solicitadas, despachadas, recibidas y diferencias,
**para** dar seguimiento completo al movimiento entre ubicaciones.
*Fuente: SC-8*

---

## Bloque G — Operación en alto volumen y modo degradado

### HU-24 — Latencia diferenciada por tipo de operación
**Como** sistema de Stock Único,
**quiero** responder en segundos para ventas y reservas, permitiendo mayor latencia para indicadores analíticos,
**para** priorizar la coherencia donde el negocio la necesita sin sacrificar velocidad de venta.
*Fuente: SC-9*

### HU-25 — Degradación controlada en campañas
**Como** cliente en el sitio de comercio electrónico,
**quiero** que el sistema degrade su comportamiento de forma controlada en campañas de alto volumen, sin mostrarme datos engañosos,
**para** seguir comprando con confianza aun bajo carga extrema.
*Fuente: EC-9, CEO-9*

### HU-26 — Continuidad ante integración retrasada
**Como** negocio de NovaRetail,
**quiero** que el sistema continúe vendiendo de manera segura si alguna integración se retrasa,
**para** no detener la operación comercial por una dependencia externa.
*Fuente: CEO-10*

---

## Bloque H — Analítica operativa

### HU-27 — Datos para mejorar la operación
**Como** directora de E-commerce y Tiendas,
**quiero** disponer de datos de conversión, abandono, productos sin disponibilidad, promesas incumplidas, tiempo de preparación, reasignaciones, cancelaciones y sustituciones, distinguiendo si el problema se originó en inventario, pago, logística o tienda,
**para** identificar y corregir causas raíz de la mala experiencia.
*Fuente: EC-10*

### HU-28 — Indicadores de negocio
**Como** CEO,
**quiero** medir tasa de cancelación por falta de stock, exactitud de inventario, pedidos entregados dentro de la promesa, porcentaje de ventas omnicanal, rotación, quiebres, costo de preparación por pedido y reservas vencidas sin convertirse en venta,
**para** evaluar el éxito del proyecto Stock Único.
*Fuente: CEO-4*

---

## Bloque I — Historias derivadas del Cierre de Brechas (`08_cierre_de_brechas.md`, simulado)

> Estas historias no provienen de las tres entrevistas originales, sino de la sesión simulada de cierre de brechas. Se marcan con **(CB-Dxx)** en vez de la notación CEO-n/SC-n/EC-n, para distinguir su origen.

### HU-29 — Stock de seguridad parametrizable
**Como** sistema de inventario,
**quiero** aplicar un stock de seguridad configurable por SKU y ubicación (5% por defecto en tienda, 2% en centro de distribución) al calcular disponibilidad,
**para** evitar comprometer unidades que operativamente no deberían venderse.
*Fuente: Cierre de Brechas D-01*

### HU-30 — Expiración de reserva con extensión por pago en proceso
**Como** cliente,
**quiero** que mi reserva expire a los 10 minutos si no completo el pago, con una única extensión de 5 minutos si el pago queda "procesando",
**para** tener tiempo razonable sin bloquear inventario indefinidamente.
*Fuente: Cierre de Brechas D-02*

### HU-31 — Ciclo de vida cerrado de la reserva
**Como** sistema de inventario,
**quiero** que una reserva solo transicione entre creada → confirmada → {liberada | trasladada}, con vencida como estado terminal no reactivable,
**para** evitar inconsistencias en el manejo de reservas.
*Fuente: Cierre de Brechas D-03*

### HU-32 — Recordatorio y liberación automática de retiro en tienda
**Como** cliente con pedido de retiro en tienda,
**quiero** recibir un recordatorio al día 3 y que mi reserva se libere automáticamente al día 6 si no he recogido el pedido,
**para** conocer el plazo real y no perder oportunidad de recuperar mi compra a tiempo.
*Fuente: Cierre de Brechas D-04*

### HU-33 — Disponibilidad aproximada en vista degradada
**Como** cliente,
**quiero** ver una disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en vez de un número exacto cuando la información de inventario tiene más de 2 minutos de atraso,
**para** no recibir un dato que podría ser incorrecto, sin que esto afecte la confirmación de mi compra en el checkout.
*Fuente: Cierre de Brechas D-05*

### HU-34 — Rechazo explícito ante inconsistencia de checkout
**Como** cliente,
**quiero** que mi reserva o pago se rechace de forma explícita y clara cuando el sistema no puede garantizar consistencia,
**para** no recibir una confirmación de compra que después no pueda cumplirse.
*Fuente: Cierre de Brechas D-06*

### HU-35 — Reversión automática de pago sin pedido
**Como** sistema de checkout,
**quiero** revertir automáticamente un pago aprobado que no logra asociarse a un pedido dentro de 15 minutos, y dejar el caso en una cola de revisión operativa,
**para** no dejar cobros sin contrapartida ni casos sin seguimiento.
*Fuente: Cierre de Brechas D-07*

### HU-36 — Vinculación de número de serie en preparación
**Como** preparador de tienda,
**quiero** vincular el número de serie de la unidad física al pedido en el momento de la preparación, no antes,
**para** mantener flexibilidad de asignación entre unidades equivalentes hasta el último momento posible.
*Fuente: Cierre de Brechas D-08*

### HU-37 — División de pedido en envíos independientes
**Como** cliente con un carrito que ninguna ubicación puede despachar completo,
**quiero** que se me ofrezca dividir mi pedido en envíos independientes con fechas propias, y decidir si acepto,
**para** no perder la compra completa por falta de disponibilidad en un solo lugar.
*Fuente: Cierre de Brechas D-09*

### HU-38 — Actualización de estado por eventos logísticos
**Como** sistema de Stock Único,
**quiero** recibir del operador logístico los eventos de recepción, entrega y entrega fallida tras el despacho,
**para** mantener actualizado el estado del pedido visible para el cliente.
*Fuente: Cierre de Brechas D-10*

### HU-39 — Costo de preparación por pedido
**Como** gerente de Finanzas,
**quiero** que el sistema calcule el costo de preparación de cada pedido como tiempo de preparación por costo/hora del personal más un costo fijo de empaque, desagregado por ubicación,
**para** negociar la compensación entre canal digital y tienda física.
*Fuente: Cierre de Brechas — Finanzas*

### HU-40 — Datos mínimos visibles al validar retiro
**Como** personal de tienda que valida un retiro,
**quiero** ver únicamente el nombre del cliente y los últimos dígitos de su medio de contacto,
**para** confirmar la identidad sin acceder a información personal innecesaria.
*Fuente: Cierre de Brechas — Legal/Cumplimiento*

### HU-41 — Autoridad única por tipo de dato
**Como** arquitecto de la solución,
**quiero** que cada dato tenga un único sistema dueño (Stock Único = inventario/reserva/disponibilidad; Pagos = estado de pago; POS = venta de mostrador; ERP de proveedores = compras),
**para** eliminar ambigüedad sobre qué sistema corrige a cuál ante una discrepancia.
*Fuente: Cierre de Brechas — Incertidumbre "autoridad por sistema"*

---

## Nota de autovalidación
Las historias del Bloque A al H citan explícitamente la entrevista y pregunta de origen. Las historias del Bloque I citan `08_cierre_de_brechas.md` como fuente simulada. Ya no quedan historias pendientes por falta de una regla concreta entre las brechas cerradas en ese documento; lo que permanece abierto (predicción de demanda por IA con criterios operativos, alcance fuera de Lima/categorías iniciales, entre otros) se mantiene documentado en `07_discrepancias.md`, actualizado en su sección de brechas remanentes.
