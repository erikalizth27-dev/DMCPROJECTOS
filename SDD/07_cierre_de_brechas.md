# Cierre de Brechas — Crédito Ágil 360
## Taller de cierre (simulado) sobre `discrepancias.md`

> **Nota de origen:** Banco Andino Digital y sus entrevistas son ficticios (caso de estudio). Este documento **simula** un segundo taller de cierre de brechas con los mismos roles entrevistados (CEO, Riesgos de Crédito, Canales Digitales) más dos roles no entrevistados originalmente pero requeridos para cerrar brechas normativas y técnicas (**Cumplimiento** y **Arquitectura de Datos**). Las respuestas son una simulación razonable para efectos del ejercicio, **no políticas reales de ninguna entidad financiera**. Cada punto cerrado debe tratarse como *decisión de taller simulada*, y así debe quedar rotulado si este material se usa como insumo de un caso de enseñanza.
>
> Formato por brecha: **Brecha (de discrepancias.md) → Rol que responde → Decisión simulada → Impacto en la especificación**.

---

### Brecha 1 — Fuentes externas exactas de consulta
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Para clientes existentes se usan exclusivamente fuentes internas (core bancario, comportamiento transaccional, productos vigentes). Para clientes nuevos y como fuente complementaria, se consulta la Central de Riesgos de la SBS y un buró de crédito privado autorizado, además de validación de identidad contra RENIEC.
**Impacto:** RF-13 se detalla indicando fuente interna vs. externa por tipo de cliente; se agrega RNF sobre timeout y reintento específico por fuente externa (ver Brecha 11).

### Brecha 2 — Política de retención
**Responde:** Cumplimiento (simulado)
**Decisión:** Documentos y campos extraídos de solicitudes aprobadas se retienen 10 años (alineado a la normativa de conservación de expedientes crediticios). Solicitudes rechazadas o abandonadas se retienen 5 años. Eventos de recorrido (analítica) se retienen 24 meses en detalle y luego se agregan de forma anonimizada.
**Impacto:** Se agrega RNF-19 (política de retención) en `04_requerimientos_no_funcionales.md`.

### Brecha 3 — Reglas de deduplicación (nueva solicitud vs. reintento)
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Se considera reintento del mismo proceso cuando coincide cliente + producto solicitado + no han transcurrido más de 24 horas desde el último evento registrado y la solicitud previa no llegó a un estado terminal (aprobado/rechazado/cancelado/desembolsado). Fuera de esa ventana, se crea una solicitud nueva.
**Impacto:** RF-24 se actualiza con la regla concreta; queda como parámetro configurable, no fijo en código.

### Brecha 4 — Límites de actualización de datos ya verificados
**Responde:** Gerente de Canales Digitales (simulado)
**Decisión:** El cliente puede actualizar libremente datos de contacto (teléfono, correo) y cuenta de abono. Los datos de identidad, residencia y situación laboral verificados contra fuente oficial (RENIEC, planilla electrónica) pueden editarse, pero cualquier cambio dispara una revalidación automática contra la fuente correspondiente antes de continuar la evaluación.
**Impacto:** Se agrega criterio de aceptación adicional a HU-06 (revalidación al editar un dato verificado).

### Brecha 5 — SLA por etapa
**Responde:** CEO y Gerente de Riesgos (simulado, conjunto)
**Decisión:**
- Preaprobados: decisión ≤ 10 minutos desde la aceptación de la oferta.
- Evaluación estándar (cliente existente, sin revisión manual): ≤ 48 horas hábiles.
- Casos en revisión manual: ≤ 5 días hábiles.
- Desembolso tras aceptación de contrato: ≤ 24 horas.
**Impacto:** RNF-18 se reemplaza/detalla con estos cuatro SLA; deja de estar "no definido".

### Brecha 6 — Definición operativa de "cliente preaprobado"
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Cliente existente con score interno por encima del umbral vigente para la campaña activa, sin alertas de identidad ni mora vigente, y con una oferta de crédito personal previamente calculada y no vencida.
**Impacto:** Se agrega como regla explícita a RF-15 y CU-04.

### Brecha 7 — Umbral de confianza de extracción por IA
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Umbral de confianza mínimo aceptado sin revisión humana: **90%** por campo. Entre 70% y 90% el campo se resalta para verificación rápida del analista. Por debajo de 70% el campo se trata como no extraído y requiere captura manual.
**Impacto:** RF-12 y HU-14 quedan con el valor numérico; se elimina el "[PENDIENTE]".

### Brecha 8 — Cliente nuevo vs. cliente existente
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Se considera "cliente existente" a quien tiene una relación activa con el banco de al menos 90 días con al menos un producto vigente (cuenta, tarjeta u otro). Todo lo demás se trata como cliente nuevo.
**Impacto:** RF-13 y CU-04 incorporan la regla de clasificación.

### Brecha 9 — Combinaciones de monto y perfil que requieren revisión manual
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Se envían a revisión manual las solicitudes que superen el 80% del monto máximo permitido para el segmento del cliente, o cuyo monto solicitado sea superior a 3 veces el promedio de sus últimos 6 meses de ingresos observados.
**Impacto:** Se agrega como criterio adicional en RF-19 y HU-21.

### Brecha 10 — Niveles de riesgo para aprobación de excepciones
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Riesgo bajo (desviación de política ≤10% en monto o tasa): puede aprobarlo el propio analista. Riesgo medio (10%–25%): requiere aprobación de un supervisor. Riesgo alto (>25% o cualquier excepción sobre alertas de identidad): requiere aprobación de un supervisor y queda marcada para revisión posterior de Cumplimiento.
**Impacto:** CU-06 y RF-21 incorporan la escala; se agrega un nuevo actor "Cumplimiento" solo para revisión posterior de excepciones de riesgo alto (revisión, no autorización).

### Brecha 11 — Objetivo de disponibilidad
**Responde:** Arquitectura de Soluciones / DevOps (simulado)
**Decisión:** Disponibilidad objetivo del 99.5% mensual para el flujo de solicitud y consulta de estado. RTO de 4 horas y RPO de 15 minutos para el componente transaccional. Durante campañas (pico x5) se activa escalamiento adicional previamente planificado.
**Impacto:** RNF-07 se actualiza con estos valores.

### Brecha 12 — Estándar de accesibilidad
**Responde:** Gerente de Canales Digitales (simulado)
**Decisión:** Se adopta como referencia WCAG 2.1 nivel AA para los canales web y móvil.
**Impacto:** RNF-12 incorpora el estándar.

### Brecha 13 — Marco normativo de protección de datos
**Responde:** Cumplimiento (simulado)
**Decisión:** Aplica la Ley N.º 29733 (Ley de Protección de Datos Personales del Perú) y su reglamento, además de las disposiciones de la SBS sobre gestión de riesgo crediticio y conservación de expedientes.
**Impacto:** RNF-04 y RNF-15 citan el marco normativo aplicable.

### Brecha 14 — Alcance de clientes nuevos y trabajadores independientes
**Responde:** CEO (simulado)
**Decisión:** Se confirma como Fase 2, con inicio de diseño detallado a partir del tercer mes posterior al lanzamiento del MVP (créditos personales, clientes existentes). No se detalla en esta especificación; se documenta solo como ítem de roadmap.
**Impacto:** Se mantiene fuera de alcance en `03_requerimientos_funcionales.md`, ahora con fecha estimada de inicio de Fase 2.

### Brecha 15 — Definición de "asesor autorizado"
**Responde:** Gerente de Canales Digitales (simulado)
**Decisión:** Personal de agencia y contact center con perfil "asesor" asignado en el sistema de gestión de accesos del banco, autenticación con segundo factor, y visibilidad limitada a las solicitudes de los clientes que atiende en el momento de la interacción (sin búsqueda libre de cartera).
**Impacto:** RF-28 y CU-07 incorporan la restricción de acceso.

### Brecha 16 — Razones de rechazo visibles al cliente
**Responde:** Gerente de Riesgos de Crédito (simulado)
**Decisión:** Al cliente se le muestran únicamente categorías genéricas: "capacidad de pago insuficiente", "historial crediticio", "información incompleta o no verificable" o "política vigente no cumplida". El detalle específico (scores, fuentes, cálculos) queda solo en el expediente interno auditable.
**Impacto:** RF-17 y HU-19 incorporan la lista de categorías visibles.

### Brecha 17 — Atributos de Oferta, Simulación, Desembolso e Incidencia
**Responde:** Gerente de Canales Digitales + Gerente de Riesgos (simulado, conjunto)
**Decisión:**
- **Oferta:** producto, monto sugerido, tasa referencial, vigencia, segmento/campaña de origen.
- **Simulación:** monto simulado, plazo simulado, cuota estimada, tasa referencial.
- **Desembolso:** monto desembolsado, cuenta destino, fecha y hora, canal de ejecución.
- **Incidencia:** categoría (consulta de estado, reclamo, error técnico), canal de registro, estado de la incidencia.
**Impacto:** `06_modelo_datos.md` se actualiza incorporando estos atributos de negocio, que dejan de estar "sin detallar".

### Brecha 18-20 — Supuestos técnicos de modelado (tipos de dato, PK/FK, clasificación maestro/transaccional, cardinalidades)
**Responde:** Arquitectura de Datos (simulado)
**Decisión:** Se ratifican como válidos los supuestos técnicos propuestos (uuid como llave primaria, tipos de dato estándar, clasificación maestro/transaccional y cardinalidades descritas), sin cambios de fondo, dejando abierta su revisión formal en la etapa de diseño detallado de base de datos.
**Impacto:** Los supuestos técnicos pasan de "a validar" a "validados en taller simulado, sujetos a diseño detallado".

---

## Resumen de brechas cerradas

| # | Brecha | Estado |
|---|---|---|
| 1 | Fuentes externas | Cerrada (simulada) |
| 2 | Política de retención | Cerrada (simulada) |
| 3 | Reglas de deduplicación | Cerrada (simulada) |
| 4 | Límites de actualización de datos | Cerrada (simulada) |
| 5 | SLA por etapa | Cerrada (simulada) |
| 6 | Definición de "preaprobado" | Cerrada (simulada) |
| 7 | Umbral de confianza IA | Cerrada (simulada) |
| 8 | Cliente nuevo vs. existente | Cerrada (simulada) |
| 9 | Combinaciones monto/perfil | Cerrada (simulada) |
| 10 | Niveles de riesgo para excepciones | Cerrada (simulada) |
| 11 | Objetivo de disponibilidad | Cerrada (simulada) |
| 12 | Estándar de accesibilidad | Cerrada (simulada) |
| 13 | Marco normativo de datos | Cerrada (simulada) |
| 14 | Alcance clientes nuevos/independientes | Confirmada como Fase 2 (no cerrada al MVP) |
| 15 | Definición de "asesor autorizado" | Cerrada (simulada) |
| 16 | Razones de rechazo visibles | Cerrada (simulada) |
| 17 | Atributos de Oferta/Simulación/Desembolso/Incidencia | Cerrada (simulada) |
| 18-20 | Supuestos técnicos de modelado | Ratificados, pendientes de diseño detallado |

## Siguiente paso sugerido
Con este cierre, `02_criterios_aceptacion.md`, `03_requerimientos_funcionales.md`, `04_requerimientos_no_funcionales.md`, `05_casos_de_uso.md` y `06_modelo_datos.md` pueden actualizarse reemplazando cada marca `[PENDIENTE]` / `[SUPUESTO TÉCNICO — a validar]` por la decisión correspondiente de este documento. Puedo aplicar esas actualizaciones a los cinco archivos si lo confirmas.
