# Modelos de Datos — Stock Único (NovaRetail)

> Los **nombres de entidades, atributos y relaciones** provienen de las entrevistas (objetos de negocio de la tabla de evidencias y detalles dados por Supply Chain y E-commerce). Los **tipos de dato físicos** (VARCHAR, DECIMAL, longitudes, etc.) son **supuestos técnicos del arquitecto**, no reglas de negocio — se marcan explícitamente como tal y se listan en `07_discrepancias.md`, porque ningún entrevistado definió formatos o longitudes.

---

## 1. Modelo Conceptual

### Entidades identificadas (trazabilidad)
| Entidad | Fuente |
|---|---|
| Producto | EV (objetos de negocio: Producto, SKU) |
| Ubicación | EV; SC-7, SC-8 |
| SaldoInventario | SC-1 |
| Movimiento | SC-2, SC-10 |
| Reserva | SC-4, EC-2 |
| Carrito | EV; EC-3 |
| Pedido | EV; EC-3, EC-4 |
| Pago | EV; EC-8 |
| Promesa | EV; CEO-6, EC-3 |
| TareaPreparación | EV; EC-4, EC-7 |
| Transferencia | SC-8 |
| Cliente | EV (actor); CEO-6 |
| Usuario interno (cajero, preparador, supervisor, operador logístico) | EV (actores) |
| Excepción (faltante/daño) | EC-5, EC-7 |

### Relaciones (nivel conceptual)
- Cliente **posee** Carrito
- Carrito **contiene** Producto (mediante ítems)
- Carrito **se convierte en** Pedido
- Pedido **incluye** Producto (mediante ítems del pedido)
- Pedido **se asocia a** Reserva
- Pedido **se asocia a** Pago
- Pedido **tiene** Promesa
- Pedido **se asigna a** Ubicación
- Pedido **genera** TareaPreparación
- TareaPreparación **la realiza** Usuario interno (preparador)
- TareaPreparación **puede generar** Excepción
- Producto **tiene** SaldoInventario por Ubicación
- SaldoInventario **se modifica por** Movimiento
- Movimiento **puede originarse en** Transferencia
- Transferencia **conecta** dos Ubicaciones (origen/destino)
- Reserva **afecta** SaldoInventario

### Diagrama Entidad-Relación (Mermaid) — Conceptual

```mermaid
erDiagram
    CLIENTE ||--o{ CARRITO : posee
    CARRITO ||--o{ PRODUCTO : contiene
    CARRITO ||--o| PEDIDO : "se confirma como"
    PEDIDO ||--o{ PRODUCTO : incluye
    PEDIDO ||--o{ RESERVA : "genera"
    PEDIDO ||--o{ PAGO : "se asocia a"
    PEDIDO ||--|| PROMESA : tiene
    PEDIDO }o--|| UBICACION : "se despacha desde"
    PEDIDO ||--o{ TAREA_PREPARACION : genera
    TAREA_PREPARACION }o--|| USUARIO_INTERNO : "es realizada por"
    TAREA_PREPARACION ||--o{ EXCEPCION : "puede generar"
    PRODUCTO ||--o{ SALDO_INVENTARIO : "tiene por ubicación"
    UBICACION ||--o{ SALDO_INVENTARIO : "almacena"
    SALDO_INVENTARIO ||--o{ MOVIMIENTO : "se modifica por"
    MOVIMIENTO }o--o| TRANSFERENCIA : "puede originarse en"
    TRANSFERENCIA }o--|| UBICACION : origen
    TRANSFERENCIA }o--|| UBICACION : destino
    RESERVA }o--|| PRODUCTO : reserva
    RESERVA }o--|| UBICACION : "en ubicación"
```

---

## 2. Modelo Lógico

> Se detallan atributos mencionados explícitamente en las entrevistas. No se agregan atributos ausentes del input; donde existe un atributo evidentemente necesario pero no declarado (por ejemplo, un identificador técnico), se marca `[supuesto técnico]`.

### Entidades y atributos

**Producto**
- codigo_sku *(EV, SC-1)*
- tipo_manejo: serializado | lote *(SC-1)*
- categoria *[supuesto técnico — mencionado indirectamente en CEO-5 como "tecnología y pequeños electrodomésticos" sin modelo formal de categoría]*
- requiere_numero_serie *(Cierre de Brechas D-08 — true para categorías del MVP)*

**UnidadSerializada** *(nueva entidad, Cierre de Brechas D-08)*
- numero_serie
- sku (ref. Producto)
- tarea_preparacion (ref. TareaPreparacion, se vincula solo en el momento de preparación, no al crear la reserva)

**Ubicacion**
- identificador_ubicacion *[supuesto técnico]*
- tipo: tienda | centro_distribucion *(EV: "78 tiendas... dos centros de distribución")*
- capacidad_preparacion *(SC-7)*
- horario_preparacion *(SC-7)*
- prioridad_tienda *(SC-7)*
- puede_vender_en_linea *(SC-7)*
- puede_preparar_en_horario_actual *(SC-7)*

**SaldoInventario**
- sku (ref. Producto)
- ubicacion (ref. Ubicacion)
- stock_fisico *(SC-1)*
- disponible *(SC-1)*
- reservado *(SC-1)*
- comprometido *(SC-1)*
- bloqueado *(SC-1)*
- dañado *(SC-1)*
- en_transito *(SC-1)*
- pendiente_recepcion *(SC-1)*
- stock_seguridad_parametro *(Cierre de Brechas D-01 — porcentaje configurable por SKU/ubicación, 5% tienda / 2% centro de distribución por defecto)*

**Movimiento**
- tipo_origen: venta_caja | pedido_web | recepcion_proveedor | transferencia | devolucion | anulacion | conteo | ajuste | daño | robo | cambio_estado *(SC-2)*
- documento_relacionado *(SC-10)*
- usuario_o_sistema *(SC-10)*
- momento *(SC-10)*
- cantidad_anterior *(SC-10)*
- cantidad_nueva *(SC-10)*
- razon *(SC-6, SC-10)*
- motivo *(SC-6)*
- evidencia *(SC-6)*
- secuencia_evento *[supuesto técnico, necesario para detectar "eventos fuera de orden" (SC-10) pero sin campo explícito declarado]*

**Reserva**
- origen *(SC-4)*
- cantidad *(SC-4)*
- ubicacion (ref. Ubicacion) *(SC-4)*
- fecha_creacion *(SC-4)*
- fecha_expiracion *(SC-4)*
- estado: creada | confirmada | liberada | vencida | trasladada *(SC-4)*
- extension_aplicada *(Cierre de Brechas D-02 — booleano, indica si ya se usó la extensión única de 5 minutos por pago "procesando")*

**Transferencia**
- ubicacion_origen *(SC-8)*
- ubicacion_destino *(SC-8)*
- unidades_solicitadas *(SC-8)*
- unidades_despachadas *(SC-8)*
- unidades_recibidas *(SC-8)*
- diferencia *(SC-8)*

**Carrito**
- cliente (ref. Cliente) *(EV)*
- items (producto + cantidad) *(EC-3)*

**Pedido**
- ubicacion_candidata *(EC-3)*
- modalidad_entrega *(EC-3)*
- costo *(EC-3)*
- fecha_prometida *(EC-3)*
- vigencia_oferta *(EC-3)*
- estado *[supuesto técnico — se infiere de EC-4/EC-5/EC-6 la existencia de estados de pedido, pero no se declara una lista cerrada de estados como sí ocurrió en el caso de Reserva]*
- pedido_padre *(Cierre de Brechas D-09 — referencia opcional al pedido original cuando este es un sub-pedido generado por partición de carrito)*

**EnvioLogistico** *(nueva entidad, Cierre de Brechas D-10)*
- pedido (ref. Pedido)
- estado: recibido_por_logistica | en_transito | entregado | entrega_fallida
- motivo_entrega_fallida (si aplica)

**Promesa**
- fecha_estimada *(CEO-6)*
- tipo: domicilio_hoy | domicilio_manana | retiro_tienda *(CEO-6)*
- ubicacion_retiro (ref. Ubicacion, si aplica) *(CEO-6)*

**Pago**
- estado: aprobado *(EC-8)* *[solo se menciona explícitamente el estado "aprobado"; otros estados no fueron declarados]*
- intento_correlacionado *(EC-8)*

**TareaPreparacion**
- pedido (ref. Pedido)
- ubicacion (ref. Ubicacion)
- ubicacion_interna_producto *(EC-7)*
- tiempo_objetivo *(EC-7)*
- prioridad_en_cola *(EC-7)*
- estado: pendiente | en_preparacion | lista *[supuesto técnico basado en EC-4]*

**Excepcion**
- tipo: faltante | dañado *(EC-5, EC-7)*
- tarea_preparacion (ref. TareaPreparacion)
- accion_resultante: nueva_ubicacion | recalculo_promesa *(EC-5)*

**CodigoRecojo**
- pedido (ref. Pedido) *(EC-6)*
- codigo *(EC-6)*
- validado_por *(EC-6)*

**UsuarioInterno**
- rol: cajero | preparador | supervisor | operador_logistico *(EV)*

### Diagrama Entidad-Relación (Mermaid) — Lógico

```mermaid
erDiagram
    PRODUCTO {
        string codigo_sku
        string tipo_manejo
    }
    UBICACION {
        string identificador_ubicacion
        string tipo
        int capacidad_preparacion
        string horario_preparacion
        int prioridad_tienda
        bool puede_vender_en_linea
    }
    SALDO_INVENTARIO {
        string sku FK
        string ubicacion FK
        decimal stock_fisico
        decimal disponible
        decimal reservado
        decimal comprometido
        decimal bloqueado
        decimal dañado
        decimal en_transito
        decimal pendiente_recepcion
    }
    MOVIMIENTO {
        string tipo_origen
        string documento_relacionado
        string usuario_o_sistema
        datetime momento
        decimal cantidad_anterior
        decimal cantidad_nueva
        string razon
        string motivo
        string evidencia
    }
    RESERVA {
        string origen
        decimal cantidad
        string ubicacion FK
        datetime fecha_creacion
        datetime fecha_expiracion
        string estado
    }
    TRANSFERENCIA {
        string ubicacion_origen FK
        string ubicacion_destino FK
        decimal unidades_solicitadas
        decimal unidades_despachadas
        decimal unidades_recibidas
        decimal diferencia
    }
    CLIENTE {
        string identificador_cliente
    }
    CARRITO {
        string cliente FK
    }
    PEDIDO {
        string ubicacion_candidata FK
        string modalidad_entrega
        decimal costo
        datetime fecha_prometida
        datetime vigencia_oferta
    }
    PROMESA {
        datetime fecha_estimada
        string tipo
        string ubicacion_retiro FK
    }
    PAGO {
        string estado
        string intento_correlacionado
    }
    TAREA_PREPARACION {
        string pedido FK
        string ubicacion FK
        string ubicacion_interna_producto
        string tiempo_objetivo
        int prioridad_en_cola
        string estado
    }
    EXCEPCION {
        string tipo
        string tarea_preparacion FK
        string accion_resultante
    }
    CODIGO_RECOJO {
        string pedido FK
        string codigo
        string validado_por
    }
    USUARIO_INTERNO {
        string rol
    }

    CLIENTE ||--o{ CARRITO : posee
    CARRITO ||--o| PEDIDO : confirma
    PEDIDO ||--o{ RESERVA : genera
    PEDIDO ||--o{ PAGO : registra
    PEDIDO ||--|| PROMESA : tiene
    PEDIDO }o--|| UBICACION : "asignado a"
    PEDIDO ||--o| TAREA_PREPARACION : genera
    PEDIDO ||--o| CODIGO_RECOJO : "puede generar"
    TAREA_PREPARACION }o--|| USUARIO_INTERNO : realiza
    TAREA_PREPARACION ||--o{ EXCEPCION : "puede reportar"
    PRODUCTO ||--o{ SALDO_INVENTARIO : "tiene en"
    UBICACION ||--o{ SALDO_INVENTARIO : almacena
    SALDO_INVENTARIO ||--o{ MOVIMIENTO : registra
    MOVIMIENTO }o--o| TRANSFERENCIA : "puede originarse en"
    UBICACION ||--o{ TRANSFERENCIA : origen
    UBICACION ||--o{ TRANSFERENCIA : destino
    RESERVA }o--|| PRODUCTO : sobre
    RESERVA }o--|| UBICACION : en
```

---

## 3. Modelo Físico

> **Advertencia de trazabilidad:** los tipos de dato (VARCHAR(n), DECIMAL(p,s), TIMESTAMP, etc.), las claves primarias/foráneas técnicas y la normalización en tablas son **decisiones de diseño del arquitecto de soluciones**, no reglas de negocio provistas por las entrevistas. Se documentan aquí como propuesta técnica, sujeta a validación, y se listan también en `07_discrepancias.md`.

### Tablas propuestas (nombres técnicos snake_case)

- `producto` (sku PK, tipo_manejo, categoria)
- `ubicacion` (id_ubicacion PK, tipo, capacidad_preparacion, horario_preparacion, prioridad_tienda, puede_vender_en_linea)
- `saldo_inventario` (id PK, sku FK, id_ubicacion FK, stock_fisico, disponible, reservado, comprometido, bloqueado, danado, en_transito, pendiente_recepcion)
- `movimiento_inventario` (id PK, id_saldo_inventario FK, tipo_origen, documento_relacionado, usuario_o_sistema, momento, cantidad_anterior, cantidad_nueva, razon, motivo, evidencia_url, id_transferencia FK nullable, numero_secuencia)
- `reserva` (id PK, origen, sku FK, id_ubicacion FK, cantidad, fecha_creacion, fecha_expiracion, estado, id_pedido FK)
- `transferencia` (id PK, id_ubicacion_origen FK, id_ubicacion_destino FK, unidades_solicitadas, unidades_despachadas, unidades_recibidas, diferencia)
- `cliente` (id_cliente PK)
- `carrito` (id_carrito PK, id_cliente FK)
- `carrito_item` (id PK, id_carrito FK, sku FK, cantidad)
- `pedido` (id_pedido PK, id_carrito FK, id_ubicacion_candidata FK, modalidad_entrega, costo, fecha_prometida, vigencia_oferta, estado)
- `pedido_item` (id PK, id_pedido FK, sku FK, cantidad, id_ubicacion_asignada FK)
- `promesa` (id PK, id_pedido FK, fecha_estimada, tipo, id_ubicacion_retiro FK nullable)
- `pago` (id_pago PK, id_pedido FK, estado, id_intento_correlacionado)
- `tarea_preparacion` (id PK, id_pedido FK, id_ubicacion FK, ubicacion_interna_producto, tiempo_objetivo, prioridad_en_cola, estado, id_usuario_preparador FK)
- `excepcion_preparacion` (id PK, id_tarea_preparacion FK, tipo, accion_resultante)
- `codigo_recojo` (id PK, id_pedido FK, codigo, validado_por, fecha_validacion)
- `usuario_interno` (id_usuario PK, rol)

### Diagrama Entidad-Relación (Mermaid) — Físico

```mermaid
erDiagram
    producto {
        varchar sku PK
        varchar tipo_manejo
        varchar categoria
    }
    ubicacion {
        varchar id_ubicacion PK
        varchar tipo
        int capacidad_preparacion
        varchar horario_preparacion
        int prioridad_tienda
        boolean puede_vender_en_linea
    }
    saldo_inventario {
        bigint id PK
        varchar sku FK
        varchar id_ubicacion FK
        decimal stock_fisico
        decimal disponible
        decimal reservado
        decimal comprometido
        decimal bloqueado
        decimal danado
        decimal en_transito
        decimal pendiente_recepcion
    }
    movimiento_inventario {
        bigint id PK
        bigint id_saldo_inventario FK
        varchar tipo_origen
        varchar documento_relacionado
        varchar usuario_o_sistema
        timestamp momento
        decimal cantidad_anterior
        decimal cantidad_nueva
        varchar razon
        varchar motivo
        varchar evidencia_url
        bigint id_transferencia FK
        bigint numero_secuencia
    }
    reserva {
        bigint id PK
        varchar origen
        varchar sku FK
        varchar id_ubicacion FK
        decimal cantidad
        timestamp fecha_creacion
        timestamp fecha_expiracion
        varchar estado
        bigint id_pedido FK
    }
    transferencia {
        bigint id PK
        varchar id_ubicacion_origen FK
        varchar id_ubicacion_destino FK
        decimal unidades_solicitadas
        decimal unidades_despachadas
        decimal unidades_recibidas
        decimal diferencia
    }
    cliente {
        bigint id_cliente PK
    }
    carrito {
        bigint id_carrito PK
        bigint id_cliente FK
    }
    carrito_item {
        bigint id PK
        bigint id_carrito FK
        varchar sku FK
        decimal cantidad
    }
    pedido {
        bigint id_pedido PK
        bigint id_carrito FK
        varchar id_ubicacion_candidata FK
        varchar modalidad_entrega
        decimal costo
        timestamp fecha_prometida
        timestamp vigencia_oferta
        varchar estado
    }
    pedido_item {
        bigint id PK
        bigint id_pedido FK
        varchar sku FK
        decimal cantidad
        varchar id_ubicacion_asignada FK
    }
    promesa {
        bigint id PK
        bigint id_pedido FK
        timestamp fecha_estimada
        varchar tipo
        varchar id_ubicacion_retiro FK
    }
    pago {
        bigint id_pago PK
        bigint id_pedido FK
        varchar estado
        varchar id_intento_correlacionado
    }
    tarea_preparacion {
        bigint id PK
        bigint id_pedido FK
        varchar id_ubicacion FK
        varchar ubicacion_interna_producto
        varchar tiempo_objetivo
        int prioridad_en_cola
        varchar estado
        bigint id_usuario_preparador FK
    }
    excepcion_preparacion {
        bigint id PK
        bigint id_tarea_preparacion FK
        varchar tipo
        varchar accion_resultante
    }
    codigo_recojo {
        bigint id PK
        bigint id_pedido FK
        varchar codigo
        varchar validado_por
        timestamp fecha_validacion
    }
    usuario_interno {
        bigint id_usuario PK
        varchar rol
    }

    cliente ||--o{ carrito : ""
    carrito ||--o{ carrito_item : ""
    carrito ||--o| pedido : ""
    pedido ||--o{ pedido_item : ""
    pedido ||--o{ reserva : ""
    pedido ||--o{ pago : ""
    pedido ||--|| promesa : ""
    pedido }o--|| ubicacion : ""
    pedido ||--o| tarea_preparacion : ""
    pedido ||--o| codigo_recojo : ""
    tarea_preparacion }o--|| usuario_interno : ""
    tarea_preparacion ||--o{ excepcion_preparacion : ""
    producto ||--o{ saldo_inventario : ""
    ubicacion ||--o{ saldo_inventario : ""
    saldo_inventario ||--o{ movimiento_inventario : ""
    movimiento_inventario }o--o| transferencia : ""
    ubicacion ||--o{ transferencia : "origen"
    ubicacion ||--o{ transferencia : "destino"
    reserva }o--|| producto : ""
    reserva }o--|| ubicacion : ""
    carrito_item }o--|| producto : ""
    pedido_item }o--|| producto : ""
    pedido_item }o--|| ubicacion : ""
```

## 4. Delta de modelo derivado del Cierre de Brechas

> Los diagramas Mermaid de las secciones 1 a 3 corresponden a la versión previa al cierre de brechas. Los siguientes cambios fueron incorporados a nivel de atributos/entidades en el modelo lógico (ver arriba) y deben reflejarse en la próxima actualización de los diagramas y del modelo físico:

- **SaldoInventario** gana `stock_seguridad_parametro` (D-01).
- **Reserva** gana `extension_aplicada` (D-02).
- **Producto** gana `requiere_numero_serie`; se agrega la entidad **UnidadSerializada** relacionada 1..1 con TareaPreparacion (D-08).
- **Pedido** gana `pedido_padre` (referencia a sí mismo) para modelar sub-pedidos por partición de carrito (D-09).
- Se agrega la entidad **EnvioLogistico**, relacionada 1..1 con Pedido, para registrar los eventos del operador logístico tras el despacho (D-10).

```mermaid
erDiagram
    PEDIDO ||--o| PEDIDO : "pedido_padre (sub-pedido de)"
    PEDIDO ||--o| ENVIO_LOGISTICO : genera
    PRODUCTO ||--o{ UNIDAD_SERIALIZADA : identifica
    UNIDAD_SERIALIZADA }o--|| TAREA_PREPARACION : "se vincula en"
    ENVIO_LOGISTICO {
        string estado
        string motivo_entrega_fallida
    }
    UNIDAD_SERIALIZADA {
        string numero_serie
        string sku FK
        string tarea_preparacion FK
    }
```

## Nota de autovalidación
Todos los nombres de entidad, atributo y relación en los tres niveles provienen de las entrevistas o de la tabla de evidencias, salvo los elementos marcados `[supuesto técnico]` y los del apartado 4, que provienen de `08_cierre_de_brechas.md` y están citados como tal. Los tipos de dato del modelo físico completo siguen siendo decisiones de diseño del arquitecto, listadas en `07_discrepancias.md`.
