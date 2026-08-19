# 06 — Modelo de Datos
## Proyecto: Crédito Ágil 360

> Las entidades se extraen de la tabla "Evidencias iniciales" y de menciones explícitas en las entrevistas. Los **atributos de negocio** citados provienen literalmente del texto (p. ej. Riesgos P2, P4, P5, P9). Los **atributos técnicos estándar** (identificadores, fechas de auditoría, tipos de dato físicos) no fueron dictados por las entrevistas y se marcan como **[SUPUESTO TÉCNICO — a validar]**; no constituyen reglas de negocio, sino convenciones habituales de modelado necesarias para que el modelo sea implementable.

---

## 1. Modelo Conceptual

### Entidades (solo objetos de negocio mencionados)
Cliente, Solicitud, Oferta, Simulación, Documento, CampoExtraído, Evaluación, Decisión, ReglaDeElegibilidad, Excepción, Contrato, Desembolso, Notificación, Canal, Incidencia, EventoDeRecorrido, Usuario (Analista/Supervisor/Asesor/Agente).

*Fuente: tabla "Evidencias iniciales" (Actores, Objetos de negocio); Riesgos P3, P5, P9; Canales P9, P10.*

### Relaciones (solo las que se infieren directamente del texto)
- Un **Cliente** realiza una o varias **Simulaciones** y **Solicitudes**. (Canales P2)
- Una **Oferta** puede originar una **Solicitud**. (Canales P2)
- Una **Solicitud** se inicia y continúa en uno o varios **Canales**. (Canales P1, P4)
- Una **Solicitud** tiene cero o varios **Documentos** adjuntos. (Canales P2; Riesgos P9)
- Un **Documento** produce cero o varios **CampoExtraído** (por IA). (Riesgos P9)
- Una **Solicitud** tiene una o varias **Evaluaciones**, y cada Evaluación produce una **Decisión**. (Riesgos P1, P4)
- Una **Decisión** se sustenta en una **ReglaDeElegibilidad** vigente (versión). (Riesgos P3, P5)
- Una **Decisión** puede tener asociada una **Excepción**, recomendada por un Analista y aprobada por un Supervisor. (Riesgos P7)
- Una **Solicitud** aprobada y aceptada genera un **Contrato**, que habilita un **Desembolso**. (Canales P2)
- Una **Solicitud** genera una o varias **Notificaciones**. (Canales P6)
- Una **Solicitud** genera uno o varios **EventoDeRecorrido**. (Canales P10)
- Un **Agente** registra cero o varias **Incidencias** sobre una **Solicitud**. (Canales P9)

### Diagrama ER — Conceptual (mermaid)

```mermaid
erDiagram
    CLIENTE ||--o{ SIMULACION : realiza
    CLIENTE ||--o{ SOLICITUD : presenta
    OFERTA ||--o{ SOLICITUD : origina
    CANAL ||--o{ SOLICITUD : "inicia/continua"
    SOLICITUD ||--o{ DOCUMENTO : adjunta
    DOCUMENTO ||--o{ CAMPO_EXTRAIDO : produce
    SOLICITUD ||--o{ EVALUACION : requiere
    EVALUACION ||--|| DECISION : produce
    REGLA_ELEGIBILIDAD ||--o{ DECISION : sustenta
    DECISION ||--o| EXCEPCION : "puede tener"
    USUARIO ||--o{ EXCEPCION : "recomienda/aprueba"
    SOLICITUD ||--o| CONTRATO : genera
    CONTRATO ||--o| DESEMBOLSO : habilita
    SOLICITUD ||--o{ NOTIFICACION : genera
    SOLICITUD ||--o{ EVENTO_RECORRIDO : registra
    USUARIO ||--o{ INCIDENCIA : registra
    SOLICITUD ||--o{ INCIDENCIA : "referida en"
```

---

## 2. Modelo Lógico

> Se listan solo los atributos explícitamente mencionados en las entrevistas para cada entidad. Los atributos adicionales necesarios para que el modelo sea funcional se marcan como supuesto técnico.

- **Cliente**: identidad, edad, residencia, situación laboral *(Riesgos P2)* — id_cliente **[SUPUESTO TÉCNICO]**.
- **Solicitud**: producto solicitado, monto, plazo, canal de origen, estado *(Riesgos P2; Canales P5)* — id_solicitud, fecha_creación **[SUPUESTO TÉCNICO]**.
- **Oferta**: (mencionada como origen de la solicitud, sin atributos propios detallados) *(Canales P2)* — id_oferta **[SUPUESTO TÉCNICO]**.
- **Simulación**: (mencionada como paso previo a la solicitud, sin atributos detallados) *(Canales P2)* — id_simulación **[SUPUESTO TÉCNICO]**.
- **Documento**: tipo (boleta, constancia), archivo de origen *(Riesgos P9)* — id_documento **[SUPUESTO TÉCNICO]**.
- **CampoExtraído**: nombre del campo, valor, nivel_de_confianza, documento_origen *(Riesgos P9)* — id_campo **[SUPUESTO TÉCNICO]**.
- **Evaluación**: ingresos, comportamiento interno, endeudamiento, alertas, score, obligaciones vigentes, comportamiento de pago, exposición total *(Riesgos P1, P2)* — id_evaluación, fecha_hora **[SUPUESTO TÉCNICO]**.
- **Decisión**: resultado (aprobado/rechazado/observado/revisión manual), monto máximo, plazo permitido, tasa, condiciones, fecha de vigencia, razones internas, versión_de_reglas, score, hora, datos_usados, fuente_de_datos, usuario_interviniente *(Riesgos P4, P5)* — id_decisión **[SUPUESTO TÉCNICO]**.
- **ReglaDeElegibilidad**: criterio (campaña/apetito de riesgo/segmento/cartera/regulación), vigencia *(Riesgos P3)* — id_regla, versión **[SUPUESTO TÉCNICO]**.
- **Excepción**: justificación, documentos considerados, usuario que autorizó, nivel de riesgo *(Riesgos P7)* — id_excepción, estado **[SUPUESTO TÉCNICO]**.
- **Contrato**: monto, plazo, tasa, condiciones *(Canales P2)* — id_contrato, fecha_aceptación **[SUPUESTO TÉCNICO]**.
- **Desembolso**: (mencionado como resultado final del proceso, sin atributos propios detallados) *(Canales P2, P6)* — id_desembolso, fecha **[SUPUESTO TÉCNICO]**.
- **Notificación**: tipo de evento, canal permitido (app/correo/SMS) *(Canales P6)* — id_notificación, fecha_envío **[SUPUESTO TÉCNICO]**.
- **Canal**: nombre (app, web, agencia, contact center) *(Canales P1)* — id_canal **[SUPUESTO TÉCNICO]**.
- **Incidencia**: (registrada por el agente de contact center, sin atributos detallados) *(Canales P9)* — id_incidencia, descripción **[SUPUESTO TÉCNICO]**.
- **EventoDeRecorrido**: tipo (ingreso, abandono, error, documento rechazado, reintento), tiempo de respuesta *(Canales P10)* — id_evento, fecha_hora **[SUPUESTO TÉCNICO]**.
- **Usuario**: rol (analista, supervisor, asesor, agente) *(Riesgos P7; Canales P4, P9)* — id_usuario **[SUPUESTO TÉCNICO]**.

### Diagrama ER — Lógico (mermaid)

```mermaid
erDiagram
    CLIENTE {
        string identidad
        int edad
        string residencia
        string situacion_laboral
    }
    SOLICITUD {
        string producto_solicitado
        decimal monto
        int plazo
        string canal_origen
        string estado
    }
    DOCUMENTO {
        string tipo
        string archivo_origen
    }
    CAMPO_EXTRAIDO {
        string nombre_campo
        string valor
        decimal nivel_confianza
    }
    EVALUACION {
        decimal ingresos
        string comportamiento_interno
        decimal endeudamiento
        string alertas
        decimal score
        decimal obligaciones_vigentes
        string comportamiento_pago
        decimal exposicion_total
    }
    DECISION {
        string resultado
        decimal monto_maximo
        int plazo_permitido
        decimal tasa
        string condiciones
        date fecha_vigencia
        string razones_internas
        string version_reglas
        string usuario_interviniente
    }
    REGLA_ELEGIBILIDAD {
        string criterio
        date vigencia_desde
        date vigencia_hasta
    }
    EXCEPCION {
        string justificacion
        string documentos_considerados
        string usuario_autorizo
        string nivel_riesgo
    }
    CONTRATO {
        decimal monto
        int plazo
        decimal tasa
        string condiciones
    }
    NOTIFICACION {
        string tipo_evento
        string canal_permitido
    }
    CANAL {
        string nombre
    }
    INCIDENCIA {
        string descripcion
    }
    EVENTO_RECORRIDO {
        string tipo_evento
        decimal tiempo_respuesta
    }
    USUARIO {
        string rol
    }

    CLIENTE ||--o{ SOLICITUD : presenta
    CANAL ||--o{ SOLICITUD : origina
    SOLICITUD ||--o{ DOCUMENTO : adjunta
    DOCUMENTO ||--o{ CAMPO_EXTRAIDO : produce
    SOLICITUD ||--o{ EVALUACION : requiere
    EVALUACION ||--|| DECISION : produce
    REGLA_ELEGIBILIDAD ||--o{ DECISION : sustenta
    DECISION ||--o| EXCEPCION : puede_tener
    USUARIO ||--o{ EXCEPCION : recomienda_aprueba
    SOLICITUD ||--o| CONTRATO : genera
    SOLICITUD ||--o{ NOTIFICACION : genera
    SOLICITUD ||--o{ EVENTO_RECORRIDO : registra
    USUARIO ||--o{ INCIDENCIA : registra
    SOLICITUD ||--o{ INCIDENCIA : referida_en
```

---

## 3. Modelo Físico

> Nombres de tabla, tipos de dato y llaves son **[SUPUESTO TÉCNICO — a validar con el equipo de arquitectura de datos]**, ya que las entrevistas no especifican el motor de base de datos, tipos de dato ni longitudes. Solo la existencia de los campos de negocio está confirmada por las entrevistas (ver sección 2).

### Tablas propuestas (resumen)

| Tabla | PK | FK relevantes |
|---|---|---|
| cliente | id_cliente | — |
| canal | id_canal | — |
| solicitud | id_solicitud | id_cliente, id_canal, id_oferta |
| oferta | id_oferta | — |
| simulacion | id_simulacion | id_cliente |
| documento | id_documento | id_solicitud |
| campo_extraido | id_campo | id_documento |
| evaluacion | id_evaluacion | id_solicitud |
| decision | id_decision | id_evaluacion, id_regla |
| regla_elegibilidad | id_regla | — |
| excepcion | id_excepcion | id_decision, id_usuario_recomienda, id_usuario_aprueba |
| contrato | id_contrato | id_solicitud |
| desembolso | id_desembolso | id_contrato |
| notificacion | id_notificacion | id_solicitud |
| incidencia | id_incidencia | id_solicitud, id_usuario |
| evento_recorrido | id_evento | id_solicitud, id_canal |
| usuario | id_usuario | — |

### Diagrama ER — Físico (mermaid)

```mermaid
erDiagram
    cliente {
        uuid id_cliente PK
        varchar identidad
        int edad
        varchar residencia
        varchar situacion_laboral
    }
    canal {
        uuid id_canal PK
        varchar nombre
    }
    oferta {
        uuid id_oferta PK
    }
    simulacion {
        uuid id_simulacion PK
        uuid id_cliente FK
    }
    solicitud {
        uuid id_solicitud PK
        uuid id_cliente FK
        uuid id_canal FK
        uuid id_oferta FK
        varchar producto_solicitado
        decimal monto
        int plazo
        varchar estado
        timestamp fecha_creacion
    }
    documento {
        uuid id_documento PK
        uuid id_solicitud FK
        varchar tipo
        varchar archivo_origen
    }
    campo_extraido {
        uuid id_campo PK
        uuid id_documento FK
        varchar nombre_campo
        varchar valor
        decimal nivel_confianza
    }
    evaluacion {
        uuid id_evaluacion PK
        uuid id_solicitud FK
        decimal ingresos
        decimal endeudamiento
        decimal score
        decimal exposicion_total
        timestamp fecha_hora
    }
    regla_elegibilidad {
        uuid id_regla PK
        varchar criterio
        date vigencia_desde
        date vigencia_hasta
    }
    decision {
        uuid id_decision PK
        uuid id_evaluacion FK
        uuid id_regla FK
        varchar resultado
        decimal monto_maximo
        int plazo_permitido
        decimal tasa
        varchar condiciones
        date fecha_vigencia
        varchar razones_internas
        varchar usuario_interviniente
        timestamp fecha_hora
    }
    excepcion {
        uuid id_excepcion PK
        uuid id_decision FK
        varchar justificacion
        varchar documentos_considerados
        uuid id_usuario_recomienda FK
        uuid id_usuario_aprueba FK
        varchar estado
    }
    contrato {
        uuid id_contrato PK
        uuid id_solicitud FK
        decimal monto
        int plazo
        decimal tasa
        timestamp fecha_aceptacion
    }
    desembolso {
        uuid id_desembolso PK
        uuid id_contrato FK
        timestamp fecha
    }
    notificacion {
        uuid id_notificacion PK
        uuid id_solicitud FK
        varchar tipo_evento
        varchar canal_permitido
        timestamp fecha_envio
    }
    incidencia {
        uuid id_incidencia PK
        uuid id_solicitud FK
        uuid id_usuario FK
        varchar descripcion
    }
    evento_recorrido {
        uuid id_evento PK
        uuid id_solicitud FK
        uuid id_canal FK
        varchar tipo_evento
        decimal tiempo_respuesta
        timestamp fecha_hora
    }
    usuario {
        uuid id_usuario PK
        varchar rol
    }

    cliente ||--o{ simulacion : ""
    cliente ||--o{ solicitud : ""
    canal ||--o{ solicitud : ""
    oferta ||--o{ solicitud : ""
    solicitud ||--o{ documento : ""
    documento ||--o{ campo_extraido : ""
    solicitud ||--o{ evaluacion : ""
    evaluacion ||--|| decision : ""
    regla_elegibilidad ||--o{ decision : ""
    decision ||--o| excepcion : ""
    usuario ||--o{ excepcion : ""
    solicitud ||--o| contrato : ""
    contrato ||--o| desembolso : ""
    solicitud ||--o{ notificacion : ""
    solicitud ||--o{ incidencia : ""
    usuario ||--o{ incidencia : ""
    solicitud ||--o{ evento_recorrido : ""
    canal ||--o{ evento_recorrido : ""
```

## Datos maestros vs. transaccionales (según lo declarado)
- **Datos maestros (relativamente estables):** Cliente, Canal, Usuario, ReglaDeElegibilidad (con versión), Oferta.
- **Datos transaccionales:** Solicitud, Simulación, Documento, CampoExtraído, Evaluación, Decisión, Excepción, Contrato, Desembolso, Notificación, Incidencia, EventoDeRecorrido.

*Base: distinción implícita en Riesgos P3 (reglas con vigencia y cambios frecuentes) y Riesgos P5 (histórico inmutable de decisiones). La clasificación formal maestro/transaccional no fue enunciada explícitamente por los entrevistados; se marca como interpretación del equipo — ver `discrepancias.md`.*
