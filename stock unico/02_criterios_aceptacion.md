# Criterios de Aceptación — Stock Único (NovaRetail)

> Formato Gherkin (Dado / Cuando / Entonces). Cada criterio deriva exclusivamente de afirmaciones de las entrevistas. Donde el input no fija un valor numérico o una regla exacta, se marca **[VACÍO — ver discrepancias.md]** en vez de inventar el umbral.

## HU-01 — Disponibilidad como interpretación única
```
Dado un SKU con stock físico, reservas y compromisos registrados en una ubicación
Cuando el sistema calcula la disponibilidad para venta
Entonces el resultado debe ser: disponible = stock_físico − reservado − comprometido − bloqueado
  − dañado − stock_de_seguridad
Y el stock de seguridad debe tomar el valor parametrizado para ese SKU/ubicación,
  con 5% del stock físico como valor por defecto en tienda y 2% en centro de distribución
Y ese valor debe ser consistente entre los canales que lo consultan
[Cerrado por Cierre de Brechas D-01]
```

## HU-04 — Inventario en tránsito no disponible
```
Dado un movimiento de recepción de proveedor o transferencia aún no recibido en la ubicación destino
Cuando se consulta la disponibilidad de ese SKU en esa ubicación
Entonces las unidades en tránsito NO deben contarse como disponibles
Y solo pasan a disponible una vez registrada la recepción
```

## HU-05 — Conteos y ajustes con evidencia
```
Dado que un usuario autorizado detecta una diferencia entre stock físico y sistema
Cuando registra un conteo o ajuste
Entonces el sistema debe exigir motivo, usuario responsable y evidencia asociada
Y debe conservar el valor anterior y el nuevo sin sobrescribir el historial
```

## HU-06 — Auditoría de cada cambio de cantidad
```
Dado cualquier cambio en la cantidad de un saldo de inventario
Cuando el cambio se registra
Entonces debe quedar almacenado: evento de origen, documento relacionado, usuario o sistema,
  momento, cantidad anterior, cantidad nueva y razón
Y el sistema debe permitir identificar si el evento llegó duplicado o fuera de secuencia
```

## HU-07 — Reserva como asignación temporal controlada
```
Dado un cliente que inicia el pago de un producto disponible
Cuando el sistema crea la reserva
Entonces la reserva debe registrar origen, cantidad, ubicación, fecha de creación, expiración y estado
Y su estado debe transicionar únicamente según: creada → confirmada → {liberada | trasladada}
Y el estado vencida debe ser terminal: una reserva vencida no puede reactivarse
[Cerrado por Cierre de Brechas D-03]
```

## HU-08 — Reserva idempotente ante reintentos
```
Dado que un cliente reintenta el checkout múltiples veces para el mismo pedido
Cuando el sistema procesa cada reintento
Entonces NO debe crearse más de una reserva activa para la misma intención de compra
Y la operación debe comportarse de forma idempotente ante reintentos equivalentes
```

## HU-09 — Momento de creación de la reserva
```
Dado un cliente que solo está visitando la ficha de producto
Cuando consulta disponibilidad sin iniciar pago
Entonces el sistema NO debe crear una reserva
Dado que el cliente inicia el pago o confirma el pedido
Cuando se ejecuta esa acción
Entonces el sistema debe crear la reserva con una expiración de 10 minutos
Dado que el pago queda en estado "procesando" antes de que la reserva expire
Cuando el sistema detecta ese estado
Entonces debe extender la expiración una única vez por 5 minutos adicionales,
  sin volver a extenderla si se repite el estado "procesando"
[Cerrado por Cierre de Brechas D-02]
```

## HU-10 — Liberación de reserva no recogida
```
Dado un pedido con retiro en tienda cuya reserva está confirmada
Cuando transcurren 3 días desde que el pedido queda listo para recojo sin que el cliente lo retire
Entonces el sistema debe enviarle un recordatorio
Dado que transcurren 6 días desde que el pedido queda listo para recojo sin retiro
Cuando se cumple ese plazo
Entonces el sistema debe liberar automáticamente la reserva
Y las unidades deben volver a estar disponibles
[Cerrado por Cierre de Brechas D-04]
```

## HU-13 — Correlación entre intento, pago, pedido y reserva
```
Dado un pago que es aprobado por el sistema de pagos
Cuando se procesa esa aprobación
Entonces debe existir un pedido asociado a ese pago
Dado una reserva confirmada
Cuando se audita el pedido
Entonces debe existir trazabilidad completa entre intento, pago, pedido y reserva
```

## HU-14 — Promesa de entrega confiable
```
Dado un cliente que está por confirmar un pedido
Cuando el sistema calcula la promesa de entrega
Entonces debe informar si el pedido llegará hoy, mañana, o si puede recogerse en una tienda determinada
Y esta información debe mostrarse ANTES de que el cliente pague
```

## HU-15 — Comunicación ante cambio de promesa
```
Dado un pedido cuya promesa de entrega ya fue comunicada al cliente
Cuando la promesa cambia por cualquier motivo (por ejemplo, un faltante)
Entonces el sistema debe comunicar el cambio al cliente
Y debe ofrecer alternativas (nueva fecha, cambio de tienda, producto sustituto o devolución)
  en lugar de cancelar directamente
```

## HU-16 — Selección de ubicación de despacho
```
Dado un pedido confirmado que requiere asignación de ubicación
Cuando el sistema evalúa las ubicaciones candidatas
Entonces debe considerar disponibilidad, distancia al cliente, capacidad de preparación,
  horario, costo, prioridad de tienda, fecha prometida y restricciones del producto
Y no debe asignar una ubicación que no pueda preparar el pedido en el horario correspondiente
```

## HU-18 — Cola priorizada con datos mínimos necesarios
```
Dado un preparador de tienda que abre su cola de tareas
Cuando visualiza un pedido asignado
Entonces debe ver ubicación interna del producto, tiempo objetivo y opción de escanear el SKU
Y NO debe ver datos personales del cliente que no necesite para preparar el pedido
```

## HU-19 — Gestión de faltante en preparación
```
Dado un preparador que no encuentra una unidad reservada durante la preparación
Cuando reporta el faltante
Entonces el sistema debe registrar la excepción
Y debe buscar otra ubicación candidata y recalcular la promesa de entrega
```

## HU-21 — Retiro en tienda con código
```
Dado un pedido de retiro en tienda que queda listo para recojo
Cuando el sistema notifica al cliente
Entonces debe entregarle un código de recojo
Y el cliente debe poder usar ese código para validar su identidad al momento del retiro
```

## HU-23 — Registro de transferencias
```
Dado una transferencia de unidades entre dos ubicaciones
Cuando se registra cada etapa (solicitud, despacho, recepción)
Entonces el sistema debe registrar unidades solicitadas, despachadas y recibidas
Y debe calcular y almacenar cualquier diferencia entre lo despachado y lo recibido
```

## HU-25 — Degradación controlada en campañas
```
Dado un escenario de campaña con miles de consultas por segundo
Cuando la réplica de disponibilidad acumula más de 2 minutos de atraso respecto al dato transaccional
Entonces el sistema debe mostrar disponibilidad aproximada
  ("pocas unidades", "disponible" o "agotado") en vez de una cantidad exacta
Y en ningún caso debe mostrar un número de unidades que el sistema sabe desactualizado
Y la confirmación de reserva en el checkout debe seguir siendo síncrona y consistente,
  sin degradarse aunque la vista de catálogo esté en modo aproximado
[Cerrado por Cierre de Brechas D-05]
```

## HU-26 — Continuidad ante integración retrasada
```
Dado que una integración externa o interna presenta retraso
Cuando un cliente navega el catálogo
Entonces el sistema debe mantener el catálogo disponible en modo de vista aproximada (ver HU-25)
Dado que un cliente intenta confirmar una reserva o un pago mientras el sistema no puede
  garantizar consistencia
Cuando se ejecuta esa acción
Entonces el sistema debe rechazarla de forma explícita y clara,
  en vez de aceptar una compra que no podrá cumplirse
[Cerrado por Cierre de Brechas D-06]
```

## HU-35 — Reversión automática de pago sin pedido
```
Dado un pago aprobado sin pedido asociado
Cuando transcurren 15 minutos sin que se establezca la asociación
Entonces el sistema debe ejecutar una reversión automática del pago
Y debe notificar al cliente
Y debe registrar el caso en una cola de revisión operativa, aunque ya se haya revertido
[Cerrado por Cierre de Brechas D-07]
```

## HU-37 — División de pedido en envíos independientes
```
Dado un carrito confirmado que ninguna ubicación puede despachar completo
Cuando el sistema evalúa las ubicaciones candidatas
Entonces debe generar sub-pedidos por ubicación, cada uno con su propia fecha prometida
Y debe presentar al cliente la opción de aceptar el envío dividido
  o retirar solo lo disponible en una tienda
[Cerrado por Cierre de Brechas D-09]
```

## HU-38 — Actualización de estado por eventos logísticos
```
Dado un pedido despachado y recibido por el operador logístico
Cuando el operador logístico reporta el evento de entrega o de entrega fallida
Entonces el sistema debe actualizar el estado del pedido visible para el cliente
Y solo los eventos de "entregado" y "entrega fallida" deben modificar ese estado visible
  (el evento "en tránsito" es informativo)
[Cerrado por Cierre de Brechas D-10]
```

## HU-40 — Datos mínimos visibles al validar retiro
```
Dado un pedido listo para retiro en tienda
Cuando el personal de tienda consulta los datos del cliente para validar la entrega
Entonces debe ver únicamente el nombre del cliente y los últimos dígitos
  de su medio de contacto
Y NO debe ver el contacto completo ni datos de medios de pago
[Cerrado por Cierre de Brechas — Legal/Cumplimiento]
```

## Nota de autovalidación
Los criterios de HU-02, HU-03, HU-11, HU-12, HU-17, HU-20, HU-22, HU-24, HU-27, HU-28, HU-29, HU-30 (ver arriba como parte de HU-09), HU-31 (ver arriba como parte de HU-07), HU-32 (ver arriba como parte de HU-10), HU-33/HU-34 (ver arriba como parte de HU-25/HU-26), HU-36, HU-39 y HU-41 no se detallan en Gherkin adicional por ser principalmente estructurales, de cálculo o de reporting; sus reglas quedan cubiertas en `03_requerimientos_funcionales.md`. Ningún `[VACÍO]` permanece abierto entre los que existían en la versión anterior de este documento: todos fueron cerrados con `08_cierre_de_brechas.md` y quedan referenciados como `[Cerrado por Cierre de Brechas D-xx]`.
