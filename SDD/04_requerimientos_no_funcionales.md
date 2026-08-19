# 04 — Requerimientos No Funcionales
## Proyecto: Crédito Ágil 360

> Cada RNF está sustentado literalmente en las entrevistas. Cuando la entrevista menciona la necesidad pero no un valor numérico o estándar concreto, se indica **[VALOR NO DEFINIDO — ver discrepancias.md]**.

| ID | Requerimiento no funcional | Fuente |
|---|---|---|
| RNF-01 | **Trazabilidad completa**: debe poder reconstruirse el histórico de cada decisión (datos, fuente, hora, versión de reglas, score, excepciones, usuario interviniente). | Riesgos P5, P10 |
| RNF-02 | **Inmutabilidad de decisiones históricas**: un cambio posterior en un dato no debe alterar una decisión ya emitida. | Riesgos P5 |
| RNF-03 | **Segregación de funciones**: los roles con capacidad de recomendar, aprobar o autorizar excepciones deben estar diferenciados (analista vs. supervisor); un agente de contact center no puede modificar decisiones de riesgos. | Riesgos P7, P10; Canales P9 |
| RNF-04 | **Protección de datos personales / información sensible**: no debe exponerse información financiera sensible fuera de lo necesario, ni incluirse en el contenido de notificaciones, ni mezclarse con datos de navegación. | CEO P7; Canales P6, P10 |
| RNF-05 | **Explicabilidad de las decisiones**: no se aceptan decisiones crediticias imposibles de explicar; las decisiones deben seguir políticas controladas y auditables. | CEO P7, P8 |
| RNF-06 | **Gobierno de modelos de IA**: los modelos utilizados (p. ej. extracción documental) deben contar con monitoreo, responsables y límites claros; no deben completar información que no encuentran. | CEO P8; Riesgos P9 |
| RNF-07 | **Disponibilidad durante campañas**: el sistema debe soportar picos de tráfico de hasta cinco veces el volumen normal durante las primeras horas de una campaña. | Canales P8 |
| RNF-08 | **Capacidad transaccional de referencia**: operación habitual de aproximadamente 8,000 simulaciones diarias y 1,500 solicitudes diarias. | Canales P8 |
| RNF-09 | **Idempotencia**: no se debe evaluar ni desembolsar dos veces la misma solicitud; el sistema debe distinguir una solicitud nueva de un reintento del mismo proceso. | Riesgos P8, P10 |
| RNF-10 | **Capacidad de reprocesamiento**: deben poder reprocesarse consultas fallidas a fuentes externas o internas. | Riesgos P10 |
| RNF-11 | **Resiliencia ante fallos de integración**: la información ya registrada por el cliente no debe perderse ante un timeout o fallo, y el reintento debe acotarse a la acción afectada. | Canales P7 |
| RNF-12 | **Accesibilidad**: lenguaje claro, formularios cortos, validaciones inmediatas y compatibilidad con lectores de pantalla. | Canales P9 |
| RNF-13 | **Consistencia de datos entre sistemas**: deben gestionarse diferencias de nombres, direcciones y ocupaciones entre sistemas, y distinguirse solicitudes nuevas de reintentos. | Riesgos P8 |
| RNF-14 | **Continuidad del core bancario**: la solución no debe comprometer la continuidad del core bancario ni depender de que todos los sistemas legados cambien simultáneamente. | CEO P7 |
| RNF-15 | **Cumplimiento de políticas de elegibilidad**: no se aceptan aprobaciones fuera de política. | CEO P7 |
| RNF-16 | **Evolución de reglas sin reconstrucción**: la arquitectura debe permitir modificar reglas de negocio sin reconstruir toda la aplicación, y crecer por producto sin duplicar innecesariamente datos sensibles. | CEO P10 |
| RNF-17 | **Restricción de canal en desembolso/decisión**: la decisión final y sus condiciones deben quedar disponibles de forma consistente sin importar el canal de consulta del cliente o del asesor. | Canales P4 |
| RNF-18 | **Plazo de la primera versión**: la primera versión operativa (alcance MVP) debe estar lista en cuatro meses, priorizando un flujo reducido de extremo a extremo. | CEO P9 |

## Valores y estándares no definidos en las entrevistas
- Tiempo exacto (SLA) considerado "prácticamente inmediato" para preaprobados. **[VALOR NO DEFINIDO]**
- Umbral numérico de confianza para revisión manual de campos extraídos por IA. **[VALOR NO DEFINIDO]**
- Objetivo de disponibilidad (p. ej. % uptime, RTO/RPO). **[VALOR NO DEFINIDO]**
- Estándar de accesibilidad específico (p. ej. WCAG y nivel). **[VALOR NO DEFINIDO]**
- Norma o marco regulatorio de protección de datos aplicable, más allá de la mención genérica a protección de datos personales. **[VALOR NO DEFINIDO]**

Ver detalle en `discrepancias.md`.
