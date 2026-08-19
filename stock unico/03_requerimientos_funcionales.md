# Requerimientos Funcionales — Stock Único (NovaRetail)

> Cada RF cita su origen. Ningún RF fue inventado; donde la entrevista deja una regla abierta, se indica **[REGLA PENDIENTE DE VALIDAR]**.

## RF — Inventario y disponibilidad

**RF-01.** El sistema debe mantener, por SKU y ubicación, los siguientes estados de inventario: stock físico, disponible, reservado, comprometido, bloqueado, dañado, en tránsito y pendiente de recepción. *(SC-1)*

**RF-02.** El sistema debe soportar productos manejados por lote y productos serializados. *(SC-1)* En el MVP (tecnología y pequeños electrodomésticos), los productos requieren número de serie por tratarse de artículos de alto valor con garantía asociada; la vinculación entre el número de serie y la reserva ocurre en el momento de la preparación del pedido (RF-20/UC-05), no al crear la reserva, para mantener flexibilidad de asignación entre unidades equivalentes. *[Cerrado por Cierre de Brechas D-08]*

**RF-03.** El sistema debe registrar movimientos de inventario originados en: ventas en caja, pedidos web, recepciones de proveedores, transferencias, devoluciones, anulaciones, conteos, ajustes, daños, robos y cambios de estado, aceptando tanto eventos en tiempo real como cargas por lotes desde sistemas antiguos. *(SC-2)*

**RF-04.** El sistema debe calcular la disponibilidad para venta como: `disponible = stock_físico − reservado − comprometido − bloqueado − dañado − stock_de_seguridad`. *(SC-3, CEO-2)* El stock de seguridad es un parámetro configurable por SKU y ubicación, con valores por defecto de 5% del stock físico en tienda y 2% en centro de distribución, ajustable manualmente durante campañas; la misma fórmula aplica a todas las categorías del MVP. *[Cerrado por Cierre de Brechas D-01]*

**RF-05.** El sistema debe permitir marcar unidades físicamente presentes en una ubicación como no aptas para venta digital. *(SC-3)*

**RF-06.** El inventario en tránsito no debe considerarse disponible hasta que se registre su recepción en la ubicación destino. *(SC-8)*

**RF-07.** El sistema debe permitir registrar conteos y ajustes de inventario, conservando motivo, usuario responsable y evidencia, sin sobrescribir el historial de valores anteriores. *(SC-6)*

## RF — Reservas

**RF-08.** El sistema debe crear una reserva con: origen, cantidad, ubicación, fecha de creación, expiración y estado. *(SC-4)*

**RF-09.** El estado de una reserva debe transicionar únicamente según: creada → confirmada (cuando el pago se aprueba) → {liberada (por vencimiento, cancelación del cliente o no recojo) | trasladada (si preparación reporta faltante y se reasigna, RF-24)}. El estado vencida es terminal: una reserva vencida no se reactiva; un nuevo intento del cliente genera una reserva nueva. *(SC-4)* *[Cerrado por Cierre de Brechas D-03]*

**RF-10.** La creación de una reserva debe ser una operación idempotente y con control de concurrencia, de forma que un reintento del checkout no genere una reserva adicional sobre la misma unidad. *(SC-5)*

**RF-11.** La reserva debe crearse cuando el cliente inicia el pago o confirma el pedido, no al solo visitar la página del producto, con una expiración de 10 minutos; si el pago queda en estado "procesando" antes de expirar, la expiración se extiende una única vez por 5 minutos adicionales. *(EC-2)* *[Cerrado por Cierre de Brechas D-02]*

**RF-12.** El sistema debe enviar un recordatorio al día 3 y liberar automáticamente la reserva al día 6 si el cliente no retira el pedido en tienda dentro de ese plazo. *(EC-6)* *[Cerrado por Cierre de Brechas D-04]*

## RF — Checkout, pago y pedido

**RF-13.** El checkout debe mostrar al cliente: productos, cantidades, ubicación candidata, modalidad de entrega, costo, fecha prometida y vigencia de la oferta. *(EC-3)*

**RF-14.** Cuando un carrito contiene varios productos, el sistema debe priorizar el despacho desde una sola ubicación; si ninguna ubicación cubre todo el carrito, debe generar sub-pedidos por ubicación con fechas prometidas independientes y dejar que el cliente decida si acepta el envío dividido o retira solo lo disponible en una tienda. *(EC-3)* *[Cerrado por Cierre de Brechas D-09]*

**RF-15.** El sistema debe correlacionar el intento de compra, el pago, el pedido resultante y la reserva asociada, garantizando que un pago aprobado no quede sin pedido y que una reserva confirmada no quede sin trazabilidad. *(EC-8)* Si un pago queda aprobado sin pedido asociado por más de 15 minutos, el sistema debe ejecutar una reversión automática del pago, notificar al cliente y registrar el caso en una cola de revisión operativa. *[Cerrado por Cierre de Brechas D-07]*

**RF-16.** El sistema debe calcular y mostrar al cliente una promesa de entrega (hoy, mañana, o retiro en tienda determinada) antes de que confirme el pago. *(CEO-6, EC-1)*

**RF-17.** Cuando la promesa de entrega cambie después de comunicada, el sistema debe notificar al cliente y ofrecer alternativas: nueva fecha, cambio de tienda, producto sustituto o devolución. *(CEO-6, EC-5)*

## RF — Asignación de ubicación y preparación

**RF-18.** El sistema debe seleccionar la ubicación de despacho considerando: disponibilidad, distancia al cliente, capacidad de preparación, horario, costo, prioridad de tienda, fecha prometida y restricciones del producto. *(SC-7)*

**RF-19.** El sistema no debe asignar pedidos a una tienda que, según su horario configurado, no pueda preparar pedidos en ese momento aunque venda en línea. *(SC-7)*

**RF-20.** Al confirmarse un pedido, el sistema debe generar una tarea de preparación para que el personal de tienda o centro de distribución la acepte, valide SKU y cantidad, embale y marque el pedido como listo para despacho o recojo. *(EC-4)*

**RF-21.** El personal de preparación debe acceder a una cola priorizada de tareas con ubicación interna del producto (cuando exista), tiempo objetivo y una forma simple de escanear el SKU. *(EC-7)*

**RF-22.** El sistema no debe exponer al personal de preparación datos personales del cliente que no sean necesarios para preparar el pedido. *(EC-7)*

**RF-23.** El personal de preparación debe poder reportar faltantes o daños de un producto durante la preparación. *(EC-7)*

**RF-24.** Cuando se reporta un faltante, el sistema debe registrar la excepción, buscar otra ubicación candidata y recalcular la promesa de entrega. *(EC-5)*

## RF — Retiro en tienda y despacho

**RF-25.** El cliente debe poder elegir una tienda con disponibilidad para retiro y recibir una promesa correspondiente. *(EC-6)*

**RF-26.** El sistema debe generar un código de recojo cuando el pedido esté listo para retiro. *(EC-6)*

**RF-27.** El sistema debe validar la identidad de quien retira el pedido y registrar formalmente la entrega. *(EC-6)*

## RF — Transferencias entre ubicaciones

**RF-28.** El sistema debe registrar cada transferencia con: origen, destino, unidades solicitadas, unidades despachadas, unidades recibidas y las diferencias entre ellas. *(SC-8)*

## RF — Auditoría y trazabilidad

**RF-29.** Todo cambio en la cantidad de un saldo de inventario debe registrar: evento de origen, documento relacionado, usuario o sistema responsable, momento, cantidad anterior, cantidad nueva y razón del cambio. *(SC-10)*

**RF-30.** El sistema debe permitir detectar, a partir de la secuencia de eventos, llegadas duplicadas o eventos fuera de orden. *(SC-10)*

## RF — Operación en alto volumen y degradación

**RF-31.** El sistema debe seguir permitiendo la venta de manera segura cuando una integración externa o interna presenta retraso, evitando detener la operación comercial. *(CEO-10)* "Venta segura" se define como: el catálogo y la navegación se mantienen disponibles en vista aproximada (RF-32), mientras que la reserva y el pago —al ser transaccionales— se rechazan de forma explícita y clara si el sistema no puede garantizar consistencia, en vez de aceptar una compra que después no podrá cumplirse. *[Cerrado por Cierre de Brechas D-06]*

**RF-32.** Ante alto volumen o degradación, el sistema no debe mostrar al cliente información de disponibilidad que el propio sistema identifique como potencialmente engañosa o desactualizada. *(EC-9, CEO-9)* El umbral de activación de la vista degradada es una réplica de disponibilidad con más de 2 minutos de atraso respecto al dato transaccional; en ese caso se muestra disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en vez de una cantidad exacta. La confirmación de reserva en el checkout nunca se degrada: siempre es síncrona y consistente. *[Cerrado por Cierre de Brechas D-05]*

## RF — Analítica y reporting

**RF-33.** El sistema debe capturar datos de conversión, abandono, productos sin disponibilidad, promesas incumplidas, tiempo de preparación, reasignaciones, cancelaciones y sustituciones, permitiendo distinguir si el problema se originó en inventario, pago, logística o tienda. *(EC-10)*

**RF-34.** El sistema debe permitir calcular los indicadores de negocio: tasa de cancelación por falta de stock, exactitud de inventario, pedidos entregados dentro de la promesa, porcentaje de ventas omnicanal, rotación, quiebres, costo de preparación por pedido y reservas vencidas sin convertirse en venta. *(CEO-4)* El costo de preparación por pedido se calcula como (tiempo de preparación × costo por hora del personal asignado) + costo fijo de empaque por pedido, desagregado por ubicación. *[Cerrado por Cierre de Brechas — Finanzas]*

## RF — Alcance del MVP (declarado explícitamente por el negocio)

**RF-35.** La primera versión debe cubrir las categorías de tecnología y pequeños electrodomésticos, en la ciudad de Lima. *(CEO-5)* Otras categorías y ciudades quedan fuera del alcance inicial y se consideran evolución futura.

**RF-36.** El sistema debe integrarse gradualmente con los sistemas existentes, sin reemplazarlos todos en una sola etapa. *(CEO-7)*

## RF — Rol de la inteligencia artificial (uso acotado y explícitamente declarado)

**RF-37.** La inteligencia artificial puede utilizarse para anticipar demanda, sugerir redistribución de inventario y detectar comportamientos anómalos, pero estas funciones son de recomendación, no de decisión automática. *(CEO-8)*

**RF-38.** La reserva y el descuento de stock deben ejecutarse siempre como transacciones controladas del sistema; una predicción de IA no debe crear ni inventar existencias. *(CEO-8)*

## RF — Cerrados a partir del Cierre de Brechas (`08_cierre_de_brechas.md`)

**RF-39.** Cada dato debe tener un único sistema de autoridad: Stock Único es la fuente de verdad de saldo de inventario, reservas y disponibilidad; el sistema de pagos es dueño del estado del pago; el punto de venta (POS) es dueño de la venta de mostrador y solo notifica el movimiento a Stock Único; el ERP de proveedores es dueño de las órdenes de compra, y Stock Único únicamente refleja la recepción. *(Cierre de Brechas — Incertidumbre "autoridad por sistema")*

**RF-40.** Tras el despacho a domicilio, el sistema debe recibir del operador logístico los eventos de "recibido por logística", "en tránsito" (informativo) y "entregado" o "entrega fallida"; solo estos dos últimos deben actualizar el estado del pedido visible para el cliente. *(Cierre de Brechas D-10)*

**RF-41.** En el proceso de validación de retiro en tienda, el personal solo debe visualizar el nombre del cliente y los últimos dígitos de su medio de contacto, sin acceso al contacto completo ni a datos de medios de pago. *(Cierre de Brechas — Legal/Cumplimiento)*
