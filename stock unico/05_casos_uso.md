# Casos de Uso — Stock Único (NovaRetail)

> Cada caso de uso referencia las preguntas de entrevista de las que se derivan sus pasos. Los pasos sin trazabilidad explícita no se incluyen; en su lugar se marca **[PASO PENDIENTE DE VALIDAR CON NEGOCIO]**.

---

## UC-01 — Consultar disponibilidad de producto
**Actor principal:** Cliente
**Fuente:** SC-1, SC-3, SC-4, EC-1, EV

**Precondición:** El producto existe en el catálogo.

**Flujo principal:**
1. El cliente consulta un producto en el canal digital.
2. El sistema calcula la disponibilidad como stock utilizable menos reservas y compromisos, considerando stock de seguridad. *(SC-3)*
3. El sistema excluye del cálculo las unidades en tránsito no recibidas. *(SC-8)*
4. El sistema muestra la disponibilidad al cliente.

**Flujo alterno — Alta demanda / campaña:**
3a. Si la réplica de disponibilidad tiene más de 2 minutos de atraso, el sistema muestra disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en vez de una cantidad exacta, en lugar de un dato potencialmente engañoso. *(EC-9; Cierre de Brechas D-05)*

**Postcondición:** El cliente conoce la disponibilidad, sin que ello constituya aún una reserva. *(EC-2)*

---

## UC-02 — Iniciar checkout y crear reserva
**Actor principal:** Cliente
**Actores secundarios:** Sistema de pagos
**Fuente:** EC-2, EC-3, SC-4, SC-5

**Precondición:** El cliente tiene productos en el carrito.

**Flujo principal:**
1. El cliente inicia el pago o confirma el pedido.
2. El sistema crea una reserva con origen, cantidad, ubicación, fecha de creación, expiración y estado. *(SC-4)*
3. El sistema muestra en el checkout: productos, cantidades, ubicación candidata, modalidad de entrega, costo, fecha prometida y vigencia de la oferta. *(EC-3)*
4. Si el carrito tiene varios productos, el sistema decide si salen juntos, desde ubicaciones distintas, o propone una alternativa. *(EC-3)*

**Flujo alterno — Reintento del cliente:**
1a. El cliente reintenta el pago o presiona varias veces. El sistema aplica la operación de forma idempotente y no crea una reserva adicional. *(SC-5, EC-8)*

**Postcondición:** Existe una reserva vigente asociada al intento de compra.

---

## UC-03 — Confirmar pago y pedido
**Actor principal:** Cliente
**Actores secundarios:** Sistema de pagos
**Fuente:** EC-8

**Precondición:** Existe una reserva vigente para el carrito.

**Flujo principal:**
1. El sistema de pagos aprueba el pago.
2. El sistema confirma el pedido y lo correlaciona con el intento, el pago y la reserva. *(EC-8)*

**Flujo alterno — Pago aprobado sin pedido:**
2a. Si el pago se aprueba sin que exista pedido asociado, el sistema lo detecta mediante la correlación intento-pago-pedido-reserva. Si transcurren 15 minutos sin lograr la asociación, ejecuta una reversión automática del pago, notifica al cliente y registra el caso en una cola de revisión operativa. *(EC-8; Cierre de Brechas D-07)*

**Postcondición:** El pedido queda confirmado y trazado.

---

## UC-04 — Asignar ubicación de despacho
**Actor principal:** Sistema (motor de asignación)
**Fuente:** SC-7

**Precondición:** El pedido está confirmado.

**Flujo principal:**
1. El sistema evalúa las ubicaciones candidatas considerando disponibilidad, distancia al cliente, capacidad de preparación, horario, costo, prioridad de tienda, fecha prometida y restricciones del producto. *(SC-7)*
2. El sistema asigna la ubicación óptima al pedido (o a cada ítem, si aplica).

**Postcondición:** El pedido tiene una ubicación de despacho asignada y una fecha prometida calculada.

---

## UC-05 — Preparar pedido en tienda
**Actor principal:** Preparador de tienda
**Fuente:** EC-4, EC-7

**Precondición:** El pedido tiene ubicación asignada.

**Flujo principal:**
1. El sistema genera una tarea de preparación y la incorpora a la cola priorizada del preparador. *(EC-4, EC-7)*
2. El preparador visualiza ubicación interna del producto (cuando existe), tiempo objetivo, y datos mínimos necesarios (sin datos personales innecesarios del cliente). *(EC-7)*
3. El preparador valida SKU y cantidad escaneando el producto.
4. El preparador embala el pedido y lo marca listo para despacho o recojo. *(EC-4)*

**Postcondición:** El pedido queda listo para despacho o recojo.

*Ver UC-06 para el flujo alterno de faltante.*

---

## UC-06 — Gestionar faltante en preparación
**Actor principal:** Preparador de tienda
**Fuente:** EC-5

**Precondición:** El preparador no encuentra la unidad reservada durante UC-05.

**Flujo principal:**
1. El preparador reporta el faltante.
2. El sistema registra la excepción.
3. El sistema busca otra ubicación candidata (repite lógica de UC-04). *(EC-5)*
4. El sistema recalcula la promesa de entrega.
5. El sistema comunica al cliente las opciones: nueva fecha, cambio de tienda, producto sustituto o devolución. *(EC-5)*

**Postcondición:** El pedido continúa su ciclo con una nueva ubicación/promesa, o el cliente elige una alternativa.

---

## UC-07 — Retirar pedido en tienda
**Actor principal:** Cliente
**Actor secundario:** Personal de tienda
**Fuente:** EC-6

**Precondición:** El pedido está listo para recojo.

**Flujo principal:**
1. El sistema notifica al cliente y genera un código de recojo. *(EC-6)*
2. El cliente se presenta en la tienda con el código.
3. El personal de tienda valida quién retira el pedido.
4. El sistema registra la entrega.

**Flujo alterno — El cliente no recoge dentro del plazo:**
2a. Al día 3 sin retiro, el sistema envía un recordatorio al cliente. Al día 6 sin retiro, libera automáticamente la reserva. *(EC-6; Cierre de Brechas D-04)*

**Postcondición:** El pedido queda entregado y registrado, o la reserva liberada.

---

## UC-08 — Despachar pedido a domicilio
**Actor principal:** Operador logístico
**Fuente:** EC-4, EV

**Precondición:** El pedido está listo para despacho (ver UC-05).

**Flujo principal:**
1. El pedido embalado se entrega al operador logístico para su despacho.
2. El pedido se marca como despachado. *(EC-4)*
3. El operador logístico reporta el evento "recibido por logística". *(Cierre de Brechas D-10)*
4. El operador logístico puede reportar el evento informativo "en tránsito", sin que este modifique el estado visible del pedido para el cliente. *(Cierre de Brechas D-10)*
5. El operador logístico reporta el evento "entregado" o "entrega fallida" (por ejemplo, dirección incorrecta o cliente ausente).
6. El sistema actualiza el estado visible del pedido según el evento recibido en el paso 5. *(Cierre de Brechas D-10)*

**Postcondición:** El pedido queda entregado, o registrado como entrega fallida para su gestión posterior.

**Nota de trazabilidad:** La entrevista original no detallaba el flujo de última milla más allá de "marca listo para despacho"; los pasos 3 a 6 se cerraron mediante `08_cierre_de_brechas.md` (D-10, rol simulado de Logística).

---

## UC-09 — Registrar transferencia entre ubicaciones
**Actor principal:** Sistema de inventario / operador logístico
**Fuente:** SC-8

**Precondición:** Existe la necesidad de mover unidades entre dos ubicaciones.

**Flujo principal:**
1. Se registra la transferencia con origen, destino y unidades solicitadas.
2. Se registran las unidades efectivamente despachadas.
3. Se registran las unidades recibidas en destino.
4. El sistema calcula la diferencia entre lo despachado y lo recibido, si existe. *(SC-8)*
5. Mientras las unidades no se reciban en destino, no se consideran disponibles. *(SC-8)*

**Postcondición:** El movimiento queda auditado (ver UC-11).

---

## UC-10 — Registrar conteo o ajuste de inventario
**Actor principal:** Usuario autorizado de inventario
**Fuente:** SC-6

**Precondición:** Se detecta una diferencia entre el stock físico y el sistema.

**Flujo principal:**
1. El usuario autorizado registra el conteo o ajuste.
2. El sistema exige motivo, usuario y evidencia. *(SC-6)*
3. El sistema conserva el valor anterior junto al nuevo, sin sobrescribir el historial.

**Postcondición:** El ajuste queda auditado (ver UC-11).

---

## UC-11 — Auditar movimiento de inventario
**Actor principal:** Gerente de Supply Chain / analista de inventario
**Fuente:** SC-10

**Precondición:** Existen movimientos registrados en el sistema.

**Flujo principal:**
1. El usuario consulta el historial de movimientos de un SKU/ubicación.
2. El sistema presenta evento de origen, documento relacionado, usuario o sistema, momento, cantidad anterior, cantidad nueva y razón para cada movimiento. *(SC-10)*
3. El sistema permite identificar eventos duplicados o fuera de secuencia. *(SC-10)*

**Postcondición:** El usuario puede reconstruir la causa de una diferencia de inventario.

---

## UC-12 — Operar en modo degradado
**Actor principal:** Sistema
**Fuente:** EC-9, CEO-9, CEO-10

**Precondición:** El sistema detecta alto volumen o retraso de una integración.

**Flujo principal:**
1. El sistema detecta que la réplica de disponibilidad acumula más de 2 minutos de atraso respecto al dato transaccional. *(EC-9; Cierre de Brechas D-05)*
2. El sistema muestra disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en catálogo y navegación, evitando mostrar cantidades exactas potencialmente engañosas. *(EC-9; Cierre de Brechas D-05)*
3. El sistema mantiene la confirmación de reserva y pago como operaciones síncronas y consistentes, sin degradarlas. *(CEO-10; Cierre de Brechas D-06)*

**Flujo alterno — Consistencia no garantizable en checkout:**
3a. Si el sistema no puede garantizar consistencia para una reserva o un pago en curso, la rechaza de forma explícita y clara, en vez de aceptar una compra que no podrá cumplirse. *(Cierre de Brechas D-06)*

**Postcondición:** La operación comercial continúa sin interrupción total: el catálogo permanece disponible en vista aproximada, y las operaciones transaccionales se completan o se rechazan explícitamente, nunca se aceptan de forma optimista.

**Nota de trazabilidad:** La regla exacta que define "venta segura" no estaba especificada por ningún entrevistado original; se cerró mediante `08_cierre_de_brechas.md` (D-05, D-06).
