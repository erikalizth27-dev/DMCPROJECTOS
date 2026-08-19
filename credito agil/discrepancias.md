# Discrepancias, Vacíos y Supuestos Pendientes de Validación
## Proyecto: Crédito Ágil 360

> Este documento consolida (a) las incertidumbres ya señaladas explícitamente en las entrevistas, (b) los vacíos de información detectados durante la construcción de historias de usuario, requerimientos, casos de uso y modelo de datos, y (c) los puntos donde el equipo tuvo que hacer una interpretación técnica no dictada por el negocio. Ningún punto de esta lista fue inventado como requerimiento; se documenta aquí precisamente para que **no** se trate como tal hasta su validación por Riesgos, Cumplimiento o el negocio.

---

## 1. Incertidumbres señaladas directamente en las entrevistas
(Tomadas de la tabla "Evidencias iniciales")

1. **Fuentes externas exactas** de consulta (identidad, score, comportamiento) no están nombradas ni descritas en el detalle de integración.
2. **Política de retención** de datos y documentos no fue definida (cuánto tiempo se conservan documentos, campos extraídos, eventos, notificaciones).
3. **Reglas de deduplicación** exactas para distinguir "nueva solicitud" de "reintento del mismo proceso" no están especificadas (solo se declara la necesidad, Riesgos P8).
4. **Límites de actualización de datos**: hasta qué punto el cliente puede modificar información ya verificada por el banco no está definido (Canales P3 solo indica que debe poder confirmar o actualizar).
5. **SLA por etapa**: no hay tiempos de respuesta objetivo definidos por etapa del proceso (simulación, evaluación, decisión, desembolso), salvo la expresión cualitativa "prácticamente inmediata" para preaprobados (CEO P1, P3).

---

## 2. Vacíos adicionales detectados durante la especificación

6. **Definición operativa de "cliente preaprobado"**: no se detallan los criterios que determinan si un cliente entra en esta categoría, más allá de que reciben una decisión casi inmediata.
7. **Umbral numérico de confianza** para marcar campos extraídos por IA como pendientes de revisión manual (Riesgos P9) no está definido; solo se menciona que debe existir un "umbral acordado".
8. **Definición y alcance exacto de "cliente nuevo" vs. "cliente existente"** para efectos de qué información se solicita: la entrevista de Riesgos (P2) menciona la diferencia de tratamiento, pero no los criterios formales de clasificación.
9. **Combinaciones específicas de monto y perfil** que además de los criterios ya listados requieren revisión manual (Riesgos P6 menciona "ciertas combinaciones de monto y perfil" sin detallarlas).
10. **Niveles de riesgo** que determinan cuándo una excepción requiere aprobación de supervisor (Riesgos P7 menciona "según el nivel de riesgo" sin escala ni umbrales).
11. **Objetivo de disponibilidad** del sistema (p. ej. % de uptime, tiempo máximo de indisponibilidad, RTO/RPO) durante operación normal y campañas: solo se menciona la necesidad de disponibilidad y el multiplicador de tráfico (x5).
12. **Estándar de accesibilidad** específico a cumplir (p. ej. WCAG y nivel) no se nombra; solo se listan atributos cualitativos (lenguaje claro, formularios cortos, validación inmediata, lectores de pantalla).
13. **Marco normativo de protección de datos** aplicable (p. ej. ley peruana de protección de datos personales) no se menciona por nombre en las entrevistas; solo se expresa la necesidad de proteger información sensible y financiera.
14. **Alcance de clientes nuevos y trabajadores independientes**: el CEO (P5) indica que se atenderán en una fase posterior, pero no se detallan los requerimientos correspondientes; por lo tanto no se incluyeron en las historias, RF ni casos de uso del MVP.
15. **Detalle de "asesor autorizado"** (Canales P4): no se especifica qué perfiles concretos califican como asesor autorizado más allá de la mención general.
16. **Contenido exacto de "razones internas visibles al cliente"** en un rechazo (Riesgos P4): se declara que no todas las razones se muestran al cliente, pero no cuáles sí.
17. **Atributos propios de Oferta, Simulación, Desembolso e Incidencia**: las entrevistas los mencionan como objetos de negocio pero no describen sus atributos específicos más allá del rol que cumplen en el proceso; en el modelo de datos se dejaron sin atributos de negocio detallados.

---

## 3. Interpretaciones técnicas no dictadas por el negocio (supuestos de modelado)

18. Todos los identificadores primarios/foráneos, tipos de dato físicos (uuid, varchar, decimal, timestamp) y nombres de tabla del **modelo físico** (`06_modelo_datos.md`, sección 3) son convenciones estándar de modelado, no requerimientos declarados por los entrevistados. Deben validarse con el equipo de arquitectura de datos y con el estándar de nomenclatura del banco.
19. La **clasificación de datos maestros vs. transaccionales** (`06_modelo_datos.md`, cierre) es una interpretación del equipo a partir de indicios (vigencia de reglas, estabilidad de catálogos); no fue enunciada explícitamente como tal en las entrevistas.
20. La cardinalidad exacta de algunas relaciones del modelo conceptual/lógico (p. ej. si una Solicitud puede tener más de una Evaluación vigente simultáneamente, o si el Contrato es 1:1 con la Solicitud) se infiere del relato del proceso, no está declarada de forma literal.

---

## 4. Recomendación
Antes de aprobar la especificación como línea base, el equipo de producto debe agendar sesiones de cierre de brechas con **Riesgos de Crédito** (puntos 2, 3, 6, 7, 8, 9, 10, 16), **Cumplimiento** (puntos 11 en su componente regulatorio, 13), **Canales Digitales / UX** (puntos 4, 11, 12, 15) y **Arquitectura de Datos** (puntos 17, 18, 19, 20), de modo que ningún supuesto técnico quede convertido en regla de negocio sin validación formal.
