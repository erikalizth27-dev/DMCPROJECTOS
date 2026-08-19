# Requerimientos No Funcionales — Stock Único (NovaRetail)

> Solo se listan RNF explícitamente mencionados o directamente derivables de una restricción declarada por un entrevistado. Ningún umbral numérico se inventa cuando el input no lo entrega; se marca **[VALOR PENDIENTE DE VALIDAR]**.

## RNF-01 — Concurrencia
El sistema debe controlar la concurrencia sobre operaciones de reserva de inventario, evitando que dos procesos reserven la misma unidad simultáneamente.
*Fuente: SC-5; EV (Restricciones: "Concurrencia")*

## RNF-02 — Idempotencia
Las operaciones críticas de checkout y reserva deben ser idempotentes: un reintento de la misma acción (por ejemplo, por reintento del cliente o timeout) no debe generar una reserva, pedido o pago duplicado.
*Fuente: SC-5, EC-8; EV (Restricciones: "Idempotencia")*

## RNF-03 — Alto volumen / escalabilidad
El sistema debe soportar picos de hasta 12,000 pedidos por hora y miles de consultas de disponibilidad por segundo durante campañas.
*Fuente: EC-9; EV (Restricciones: "Alto volumen")*

## RNF-04 — Latencia diferenciada
Las operaciones de venta y reserva deben responder en segundos. Los indicadores analíticos pueden tolerar mayor latencia.
*Fuente: SC-9; EV (Restricciones: "Latencia baja")*

## RNF-05 — Consistencia según criticidad de la operación
El catálogo/consulta de disponibilidad opera con consistencia eventual: se tolera un atraso de hasta 2 minutos, mostrando disponibilidad aproximada por encima de ese umbral. La confirmación de reserva y el pago requieren consistencia fuerte: son siempre operaciones síncronas y se rechazan explícitamente si no pueden garantizarse.
*Fuente: EC-9; Cierre de Brechas D-05, D-06 [Cerrado]*

## RNF-06 — Auditoría y trazabilidad
Todo cambio de cantidad de inventario y toda transferencia deben quedar auditados con evento de origen, documento relacionado, usuario o sistema, momento, valores anterior y nuevo, y razón; además debe poder detectarse la secuencia de eventos para identificar duplicados o desórdenes de llegada.
*Fuente: SC-10; EV (Restricciones: "Auditoría")*

## RNF-07 — Operación en modo degradado
Ante alta carga o retraso de integraciones, el sistema debe degradar su comportamiento de forma controlada: cuando la réplica de disponibilidad acumula más de 2 minutos de atraso, se muestra disponibilidad aproximada ("pocas unidades", "disponible", "agotado") en vez de una cantidad exacta, sin interrumpir la operación comercial; la confirmación de reserva y pago nunca se degrada.
*Fuente: EC-9, CEO-9, CEO-10; EV (Restricciones: "operación degradada"); Cierre de Brechas D-05, D-06 [Cerrado]*

## RNF-08 — Protección de datos del cliente
El personal de preparación en tienda no debe visualizar datos personales del cliente que no sean necesarios para preparar el pedido. Al validar un retiro en tienda, el personal solo debe ver el nombre del cliente y los últimos dígitos de su medio de contacto, sin acceso al contacto completo ni a datos de medios de pago.
*Fuente: EC-7; EV (Restricciones: "protección de datos del cliente"); Cierre de Brechas — Legal/Cumplimiento [Cerrado]*

## RNF-09 — No interrupción de la venta en tienda
El nuevo sistema no debe interrumpir las ventas que ya se realizan en tiendas físicas.
*Fuente: CEO-7*

## RNF-10 — No retención indefinida de inventario reservado
El sistema no debe reservar inventario de forma indefinida; toda reserva debe tener una expiración.
*Fuente: CEO-7, SC-4, EC-2*

## RNF-11 — Integridad de la promesa de entrega
El sistema no debe prometer al cliente unidades que no existen.
*Fuente: CEO-7*

## RNF-12 — Evolución/integración gradual
El sistema debe poder integrarse con los sistemas existentes de forma gradual, sin requerir el reemplazo simultáneo de todos los sistemas actuales.
*Fuente: CEO-7*

## RNF-13 — Control sobre el uso de inteligencia artificial
Las funciones de IA (predicción de demanda, sugerencia de redistribución, detección de anomalías) deben ser recomendaciones; las transacciones de reserva y descuento de stock deben permanecer como operaciones controladas del sistema transaccional, no delegadas a un modelo predictivo.
*Fuente: CEO-8*

## RNF-14 — Separación entre datos operativos y analítica histórica
El sistema debe distinguir entre los datos operativos en tiempo real (necesarios para vender) y la información analítica histórica (usada para mejorar la operación), sin que ambos flujos compitan por los mismos recursos críticos.
*Fuente: EC-10, SC-9; EV (Incertidumbres: "datos operativos en tiempo real frente a analítica histórica")*

## RNF-15 — Disponibilidad objetivo del sistema
El servicio de checkout y reserva debe tener una disponibilidad objetivo del 99.9% mensual, admitiendo degradación (no caída total) durante picos de campaña.
*Fuente: Cierre de Brechas — Tecnología/Arquitectura*

## RNF-16 — Recuperación ante desastres
Los servicios transaccionales de reserva y pedido deben tener un RTO (tiempo objetivo de recuperación) de 1 hora y un RPO (punto objetivo de recuperación) de 5 minutos.
*Fuente: Cierre de Brechas — Tecnología/Arquitectura*

## RNF-17 — Cifrado de datos personales
Los datos personales del cliente deben cifrarse en tránsito y en reposo.
*Fuente: Cierre de Brechas — Tecnología/Arquitectura, Legal/Cumplimiento*

## RNF-18 — Cumplimiento normativo de protección de datos
El sistema debe cumplir la normativa peruana de protección de datos personales vigente para el tratamiento de datos de clientes.
*Fuente: Cierre de Brechas — Legal/Cumplimiento*

## Nota de autovalidación
La versión anterior de este documento no incluía RNF de disponibilidad del sistema (uptime %), recuperación ante desastres, cifrado de datos ni cumplimiento normativo específico, porque ningún entrevistado original los mencionó. Estos vacíos fueron cerrados mediante `08_cierre_de_brechas.md` (RNF-15 a RNF-18). Persisten sin cerrar, por no haber sido tratados en la sesión de cierre: tiempos de respuesta exactos en milisegundos más allá de "segundos" (RNF-04) y cualquier normativa distinta a la peruana de protección de datos (por ejemplo, normativa de comercio electrónico) — ver `07_discrepancias.md`, sección actualizada.
