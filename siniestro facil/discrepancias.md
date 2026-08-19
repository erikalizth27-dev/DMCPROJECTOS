# Discrepancias, Vacíos y Tensiones Pendientes — Siniestro Fácil

> Este documento consolida todo lo que **no** tiene una definición explícita en las tres entrevistas y que, por lo tanto, no fue convertido en requerimiento, regla de negocio o atributo cerrado en los demás entregables. También recoge las tensiones que el propio caso pide dejar explícitas.

## 1. Tensiones planteadas explícitamente en el "Reto para el equipo"
Ninguna de estas tensiones fue resuelta por los entrevistados con una regla concreta; se dejan abiertas para decisión del equipo de negocio/producto:

1. **Rapidez de atención frente a control de fraude.** El CEO pide "velocidad con criterio, no velocidad sin controles" (Entrevista 1, P2), y Fraude exige que una alerta no bloquee automáticamente salvo reglas críticas configurables (Entrevista 3, P5), pero ninguna entrevista fija el punto de equilibrio (qué tan rápido debe ser el flujo digital simple frente a cuánta fricción antifraude se tolera).
2. **Experiencia simple frente a evidencia suficiente.** Operaciones permite crear el caso con datos mínimos (Entrevista 2, P2), pero no define cuándo ni cómo se exige el resto de la evidencia antes de avanzar de estado.
3. **Automatización frente a revisión humana.** El CEO exige revisión humana para decisiones sensibles (Entrevista 1, P7-P8) y Fraude exige justificación registrada (Entrevista 3, P4), pero no se definió qué decisiones se consideran "sensibles" de forma exhaustiva, ni el mecanismo operativo de escalamiento a revisión.
4. **Expediente único frente a múltiples participantes y reclamos relacionados.** Fraude pide relacionar sin fusionar (Entrevista 3, P8); no se definió cómo se presenta esa relación al operador ni qué acciones habilita.
5. **Almacenamiento de originales frente a versiones optimizadas.** Fraude exige conservar el original (Entrevista 3, P3); no se definió el tiempo de conservación ni el mecanismo de almacenamiento.
6. **Procesos síncronos de atención frente a coordinaciones asíncronas con terceros.** Operaciones describe reintento/escalamiento/reasignación (Entrevista 2, P9); no se definieron tiempos de espera antes de escalar.

## 2. Incertidumbres reconocidas directamente por los entrevistados
Provienen de la tabla "Evidencias iniciales extraídas de las entrevistas" y de menciones puntuales:

- Política exacta de deduplicación de casos reportados por varios canales (Entrevista 2, P6).
- Umbrales antifraude que determinan si una alerta bloquea, deriva o solo prioriza (Entrevista 3, P5, P6).
- Tiempo o política de conservación de imágenes/evidencia original (Entrevista 3, P3, P10).
- SLA por región y por tipo de siniestro para cada etapa del proceso (Entrevista 2, P8).
- Alcance detallado de la integración con talleres más allá de recepción de orden, presupuesto y diagnóstico (Entrevista 2, P7, P9).

## 3. Vacíos de dato / atributo sin fuente explícita
Estos campos son necesarios para sostener el modelo de datos pero no aparecen mencionados en el texto de las entrevistas; se marcaron como `[pendiente]` en los modelos:

- Nombre del asegurado, nombre del proveedor (taller/grúa) y tipo de documento del asegurado no se mencionan explícitamente, solo "documento" y "placa" como identificadores (Entrevista 2, P2).
- Definición y mecanismo de validación de "persona autorizada" para reportar en lugar del titular (Entrevista 1, P6).
- Definición completa de los "subestados internos" del siniestro, mencionados pero no enumerados (Entrevista 2, P4).
- Catálogo cerrado de canales de reporte más allá de los ejemplos dados (teléfono, correo, aplicación móvil, corredor) (contexto ficticio del documento, Entrevista 2, P6).
- Definición de "monto atípico" como señal de riesgo — se menciona la señal pero no el criterio o umbral (Entrevista 3, P2).

## 4. Decisiones técnicas fuera del alcance de las entrevistas
No se fijan en los entregables porque ningún entrevistado se pronunció sobre tecnología o infraestructura:

- Motor de base de datos definitivo.
- Mecanismo de almacenamiento de archivos binarios de evidencia (base de datos vs. almacenamiento de objetos).
- Estrategia de particionamiento, archivado o retención de datos históricos.
- Plataforma de mensajería, mapas o medios de pago específicos a integrar (el CEO solo los menciona como categorías de dependencia, Entrevista 1, P9).

## 5. Alcance explícitamente excluido (no es un vacío, es una decisión ya tomada)
Para evitar que se interprete como pendiente, se deja constancia de que lo siguiente **sí** fue definido por el CEO como fuera de alcance de esta primera versión, y así se reflejó en RF-31:
- Siniestros con heridos, fallecidos o procesos legales.
- Daños masivos.
- Seguros de salud y de hogar (el caso se concentra en seguros vehiculares).
- Clientes no directos (fuera del canal directo) en el piloto inicial.

## 6. Trazabilidad — verificación de autovalidación
Se revisaron los seis entregables (historias de usuario, criterios de aceptación, requerimientos funcionales, requerimientos no funcionales, casos de uso y modelos de datos) confirmando que cada ítem cita entrevista y pregunta de origen, salvo los elementos estructurales de modelado (identificadores, llaves foráneas, timestamps de auditoría) explícitamente marcados como `[estructural]`, que son necesarios para cualquier modelo relacional y no constituyen un requerimiento de negocio inventado. No se identificaron requerimientos sin trazabilidad que requieran reescritura.
