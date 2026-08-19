# Discrepancias y Vacíos Pendientes — Stock Único (NovaRetail)

> **Estado: actualizado tras `08_cierre_de_brechas.md`.** Las brechas D-01 a D-10, la incertidumbre de autoridad por sistema, los RNF de arquitectura, y los vacíos de Finanzas y Legal fueron **cerrados** mediante una sesión simulada de cierre de brechas y ya están reflejados en `01` a `06`. Se conservan aquí con el estado `CERRADA` para mantener trazabilidad histórica, y se listan aparte las brechas que **siguen abiertas** porque no fueron tratadas en esa sesión.

## 1. Reglas de negocio — CERRADAS mediante `08_cierre_de_brechas.md`

| # | Vacío | Estado | Decisión de cierre (resumen) | Documentos actualizados |
|---|---|---|---|---|
| D-01 | Fórmula exacta de disponibilidad | **CERRADA** | disponible = stock_físico − reservado − comprometido − bloqueado − dañado − stock_seguridad (5% tienda / 2% CD por defecto) | RF-04, HU-01, HU-29, criterios, modelo lógico |
| D-02 | Duración de expiración de la reserva | **CERRADA** | 10 min + extensión única de 5 min si el pago está "procesando" | RF-11, HU-09, HU-30, criterios, modelo lógico |
| D-03 | Reglas de transición de estado de reserva | **CERRADA** | creada → confirmada → {liberada\|trasladada}; vencida es terminal | RF-09, HU-07, HU-31, criterios |
| D-04 | Plazo de retiro en tienda | **CERRADA** | Recordatorio día 3, liberación automática día 6 | RF-12, HU-10, HU-32, UC-07, criterios |
| D-05 | Criterio de "degradación controlada" | **CERRADA** | Umbral de 2 min de atraso → disponibilidad aproximada; checkout nunca se degrada | RF-32, RNF-05, RNF-07, HU-25, HU-33, UC-01, UC-12 |
| D-06 | Qué es "vender de manera segura" | **CERRADA** | Catálogo se mantiene degradado; reserva/pago se rechazan explícitamente si no hay consistencia | RF-31, RNF-05, HU-26, HU-34, UC-12 |
| D-07 | Compensación por pago sin pedido | **CERRADA** | Reversión automática a los 15 min + cola de revisión operativa | RF-15, HU-35, UC-03 |
| D-08 | Identificación de unidades serializadas | **CERRADA** | Número de serie obligatorio en MVP; se vincula en preparación, no en la reserva | RF-02, HU-36, modelo lógico (UnidadSerializada) |
| D-09 | Partición de pedidos multiproducto | **CERRADA** | Prioridad a despacho único; si no es posible, sub-pedidos por ubicación con decisión del cliente | RF-14, HU-12, HU-37, criterios, modelo lógico (pedido_padre) |
| D-10 | Flujo posterior a "listo para despacho" | **CERRADA** | Eventos del operador logístico: recibido, en tránsito (informativo), entregado/entrega fallida | UC-08, HU-38, modelo lógico (EnvioLogistico) |

## 2. Incertidumbres de la tabla de evidencias — estado actualizado

Estas cinco incertidumbres fueron declaradas directamente en la tabla "Evidencias iniciales" del documento fuente:

1. **Fórmula exacta de disponibilidad** — **CERRADA**, coincide con D-01.
2. **Duración de reservas** — **CERRADA**, coincide con D-02/D-03.
3. **Estrategia de partición de pedidos** — **CERRADA**, coincide con D-09.
4. **Autoridad por sistema** — **CERRADA**. Stock Único = inventario/reserva/disponibilidad; Sistema de Pagos = estado de pago; POS = venta de mostrador (evento reflejado); ERP de proveedores = compras (Stock Único solo refleja recepción). Ver RF-39.
5. **Compensación ante fallas de pago** — **CERRADA**, coincide con D-07.

## 3. Retos de arquitectura del "Reto para el equipo" — estado actualizado

- Consistencia fuerte frente a consistencia eventual — **CERRADA** (RNF-05: eventual en catálogo con umbral de 2 min, fuerte en reserva/pago).
- Inventario agregado frente a unidades serializadas — **CERRADA** (D-08: serializado obligatorio en MVP, vinculado en preparación).
- Transacciones distribuidas entre reserva, pago y pedido — **CERRADA** (D-07: SLA de 15 min y reversión automática).
- Expiración y compensación de reservas — **CERRADA** (D-02, D-03).
- Operación normal frente a modo degradado — **CERRADA** (D-05, D-06).
- Datos operativos en tiempo real frente a analítica histórica — **SIGUE ABIERTA**. La sesión de cierre no definió el mecanismo técnico de separación entre el flujo transaccional y el analítico (por ejemplo, réplica, streaming de eventos o data warehouse independiente); solo se ratificó el principio general (RNF-14).

## 4. Requerimientos no funcionales — estado actualizado

| RNF faltante | Estado |
|---|---|
| Disponibilidad del sistema (uptime) | **CERRADA** — RNF-15: 99.9% mensual |
| Recuperación ante desastres (RTO/RPO) | **CERRADA** — RNF-16: RTO 1h / RPO 5min |
| Cifrado de datos en tránsito/reposo | **CERRADA** — RNF-17 |
| Cumplimiento normativo de protección de datos | **CERRADA** — RNF-18: normativa peruana |
| Tiempos de respuesta exactos en milisegundos (más allá de "segundos") | **SIGUE ABIERTA** — no tratada en el cierre |
| Normativa de comercio electrónico (distinta a protección de datos) | **SIGUE ABIERTA** — no tratada en el cierre |

## 5. Supuestos técnicos del modelo de datos (no son reglas de negocio)

Todo lo marcado `[supuesto técnico]` en `06_modelos_datos.md`:
- Identificadores técnicos de Ubicación, Pedido, Movimiento, etc.
- Campo de categoría de producto (el input solo menciona categorías a nivel de alcance: "tecnología y pequeños electrodomésticos", CEO-5, no como atributo modelado).
- Campo de secuencia de evento en Movimiento (necesario para cumplir SC-10, pero sin nombre de campo declarado).
- Lista cerrada de estados de Pedido (a diferencia de Reserva, cuyos estados sí fueron enumerados explícitamente en SC-4).
- Todos los tipos de dato físicos (VARCHAR, DECIMAL, TIMESTAMP, BIGINT) del modelo físico completo — son decisiones de diseño, no datos de negocio.

## 6. Alcance no cubierto por las entrevistas (fuera del MVP declarado) — sin cambios

Estos puntos no fueron tratados en la sesión de cierre y **siguen abiertos**:

- Categorías distintas a tecnología y pequeños electrodomésticos (CEO-5: expansión futura, sin fecha).
- Ciudades distintas a Lima (CEO-5: expansión futura, sin fecha).
- Modelo futuro de "promesa sobre stock en camino con suficiente confianza" para inventario en tránsito, mencionado por Supply Chain como posibilidad futura, no como requerimiento actual (SC-8).
- Detalle operativo de predicción de demanda y redistribución por IA: se declaró el rol permitido (recomendación, no decisión automática — CEO-8), pero no hay criterios de aceptación, umbrales de confianza ni proceso de revisión humana definidos.

## 7. Entrevistas no realizadas — estado actualizado

El documento fuente original solo incluía entrevistas a CEO, Supply Chain e Inventarios, y E-commerce y Tiendas. La sesión de cierre incorporó respuestas simuladas de cuatro roles adicionales:

| Rol no entrevistado originalmente | Estado |
|---|---|
| Finanzas/Costos | **CERRADA** — fórmula de costo de preparación por pedido (RF-34) |
| Sistemas de Pago | **CERRADA parcialmente** — se definió el SLA de reversión (D-07); no se cubrieron otros aspectos del proveedor de pagos (comisiones, medios soportados, conciliación) |
| Legal/Cumplimiento | **CERRADA parcialmente** — se definió el dato mínimo visible en retiro (RNF-08) y la normativa aplicable (RNF-18); no se cubrió política de retención de datos ni derechos ARCO |
| Logística/Última milla | **CERRADA parcialmente** — se definió el flujo de eventos post-despacho (D-10); no se cubrieron SLA de tiempo de entrega ni zonas de cobertura |

---

## Resumen de brechas remanentes (después del cierre)
Tras `08_cierre_de_brechas.md`, las brechas que **siguen sin decisión** son:

1. Mecanismo técnico de separación entre datos operativos en tiempo real y analítica histórica (sección 3).
2. Tiempos de respuesta exactos en milisegundos y normativa de comercio electrónico (sección 4).
3. Alcance de categorías/ciudades futuras y criterios operativos de IA para predicción de demanda (sección 6).
4. Aspectos no cubiertos en profundidad de Pagos, Legal y Logística (sección 7).

Ninguna de estas cuatro áreas bloquea el arranque del desarrollo del MVP definido (categorías tecnología/electrodomésticos, Lima); se recomienda tratarlas en una segunda sesión de cierre antes de escalar a otras categorías, ciudades o de habilitar las capacidades de IA con impacto en decisión.
