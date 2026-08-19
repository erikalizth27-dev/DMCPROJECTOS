# Requerimientos No Funcionales — Siniestro Fácil

> Se listan únicamente atributos de calidad mencionados o directamente implicados por los entrevistados. No se fijan valores numéricos (tiempos, disponibilidad, capacidad) que las entrevistas no proporcionan; esos umbrales quedan como pendientes en `discrepancias.md`.

## RNF-01 Privacidad y protección de datos personales
El sistema debe proteger los datos personales del asegurado y de terceros involucrados, evitando su exposición indebida. *(Entrevista 1, P7 — riesgo a evitar: "exposición de datos personales")*

## RNF-02 Trazabilidad integral
Toda acción relevante sobre un caso (registro, cambios, evidencias añadidas, cobertura aplicada, proveedor que actuó, presupuesto aprobado, comunicación al cliente, pago autorizado) debe quedar registrada de forma trazable. *(Entrevista 2, P10; tabla de evidencias — restricción "trazabilidad")*

## RNF-03 Inmutabilidad de la evidencia
La evidencia original no debe poder alterarse ni perderse; cualquier transformación (por ejemplo, compresión de imágenes) debe generar una versión derivada sin sustituir el original. *(Entrevista 3, P3; tabla de evidencias — restricción "evidencia inmutable")*

## RNF-04 Control de pagos duplicados
El sistema debe evitar pagos duplicados sobre un mismo siniestro. *(Entrevista 1, P7; tabla de evidencias — restricción "control de pagos duplicados")*

## RNF-05 Revisión humana de decisiones sensibles
Ninguna decisión sensible (por ejemplo, rechazo de cobertura, confirmación de fraude, autorización de pago) debe quedar exclusivamente en manos de un proceso automatizado; debe existir posibilidad de revisión humana y quedar la decisión explicada. *(Entrevista 1, P7, P8; tabla de evidencias — restricción "revisión humana")*

## RNF-06 Explicabilidad de la IA
Toda sugerencia o clasificación generada por IA (fotografías, documentos faltantes, resúmenes, priorización, inconsistencias) debe poder explicarse; una alerta no equivale a una conclusión de fraude. *(Entrevista 1, P8; Entrevista 3, P4)*

## RNF-07 Reproducibilidad de reglas y modelos antifraude
El sistema debe conservar versiones de reglas y modelos, así como los datos de entrada usados en cada evaluación, de modo que una alerta pueda explicarse meses después aunque la regla o el modelo hayan cambiado. *(Entrevista 3, P10)*

## RNF-08 Control de acceso basado en rol y necesidad
El acceso a información debe restringirse según el rol del usuario y su necesidad de conocer; el acceso a información ampliada de fraude está reservado a perfiles autorizados (por ejemplo, investigadores). *(Entrevista 3, P7)*

## RNF-09 Registro de accesos sensibles
Las descargas de evidencia y las consultas sensibles deben quedar registradas. *(Entrevista 3, P7)*

## RNF-10 Tolerancia a integraciones externas lentas o no disponibles
La arquitectura debe tolerar integraciones con proveedores externos (sistema de pólizas, red de talleres, proveedores de grúa, ajustadores, mapas, mensajería, medios de pago) que sean lentas o estén temporalmente indisponibles, sin bloquear al cliente. *(Entrevista 1, P9; Entrevista 2, P9)*

## RNF-11 Coordinación asíncrona con terceros
Las interacciones con proveedores externos deben poder tratarse de forma asíncrona (reintento, escalamiento, reasignación) en lugar de exigir respuesta síncrona e inmediata. *(Entrevista 2, P9; tabla de evidencias — restricción "tolerancia a proveedores externos")*

## RNF-12 Usabilidad y lenguaje orientado al cliente
La experiencia del asegurado debe presentarse en lenguaje humano y guiado paso a paso, evitando terminología interna de la aseguradora. *(Entrevista 1, P6)*

## RNF-13 Separación de valor declarado y valor normalizado
La normalización de datos (nombres, placas, ubicaciones) no debe sobrescribir el valor original declarado por el usuario o el tercero. *(Entrevista 3, P9)*

## RNF-14 Configurabilidad y versionado de políticas de negocio
Las políticas que determinan el tratamiento de alertas (bloqueo de pago, derivación, aumento de prioridad) deben ser configurables y quedar versionadas. *(Entrevista 3, P5)*

## RNF-15 Escalabilidad del piloto hacia operación nacional
El sistema debe concebirse para operar inicialmente en un piloto acotado (una ciudad, grupo controlado de talleres) con capacidad de expandirse posteriormente a todo el país. *(Entrevista 1, P10)*

## Pendientes explícitos (sin fuente para fijar valor)
Los siguientes atributos fueron mencionados como relevantes pero sin un valor o mecanismo concreto en las entrevistas, por lo que no se fija ningún número aquí (ver `discrepancias.md`):
- SLA por región y por tipo de siniestro para cada etapa (primera respuesta, llegada de grúa, revisión de cobertura, asignación, inspección, recepción de presupuesto, autorización, cierre). *(Entrevista 2, P8: "Cada etapa tiene un compromiso distinto según el tipo de siniestro y la ubicación", sin cifras.)*
- Tiempo o política de conservación de imágenes originales. *(Entrevista 3, P3, P10 — mencionan la necesidad pero no el plazo.)*
- Umbrales exactos de sensibilidad/falsos positivos de los modelos de IA antifraude. *(Entrevista 3, P6: "Necesitamos medir falsos positivos", sin umbral.)*
- Volúmetria de disponibilidad/capacidad del sistema, aunque se conoce el volumen operativo actual (≈420,000 pólizas activas, ≈18,000 reportes de siniestro al mes) como referencia de contexto. *(Contexto ficticio del documento.)*
