# Decisiones recomendadas para el piloto backend

## Estado

`PROPUESTAS PARA APROBACIÓN DEL PRODUCT OWNER`.

Estas decisiones permiten continuar el planning. Las reglas cuantitativas se implementan de forma configurable y se recalibran con datos reales.

## DEC-01 — Cierre de brechas simulado

Se adopta `cierre_de_brechas.md` como línea base provisional del piloto. No se presenta como política definitiva de producción.

## DEC-02 — Rechazo y reapertura de cobertura

- El rechazo requiere confirmación humana.
- El asegurado puede solicitar revisión aportando información adicional.
- Sólo un supervisor puede reabrir el caso.
- La reapertura devuelve el caso a `en_evaluacion`, registra motivo, actor y fecha, y conserva el rechazo original en la línea de tiempo.
- Si se confirma el rechazo, el caso puede pasar a `cerrado`.

## DEC-03 — Vigencia de presupuesto

- Valor predeterminado: 30 días calendario desde la recepción.
- Una vigencia explícita y válida enviada por el taller prevalece.
- Un presupuesto vencido pasa a `observado` y requiere confirmación o actualización.

## DEC-04 — Autorización de pagos

- Operador o ajustador prepara la solicitud.
- Supervisor autoriza.
- La misma persona no prepara y autoriza.
- El backend sólo permite `emitido` cuando existe autorización persistida.
- Los límites por monto se definen después de analizar información real.

## DEC-05 — Taller y corredor

- No crean directamente siniestros durante el piloto.
- Aportan información a casos con orden o referencia válida.
- Un operador registra los casos nuevos comunicados por estos canales y ejecuta la búsqueda de duplicados.

## DEC-06 — Entrega y cierre

- El taller registra `listo_para_entrega`.
- El asegurado confirma mediante aplicación, enlace seguro o código de un solo uso.
- El sistema registra actor, fecha y medio antes de pasar a `cerrado`.
- Como excepción, un operador adjunta evidencia y un supervisor autoriza el cierre manual.

## DEC-07 — Plan de sprints

- Sprints de 2 semanas.
- Horizonte recomendado: 7 sprints / 14 semanas.
- Equipo: Product Owner o analista, líder técnico, dos desarrolladores backend, QA de automatización y especialista GCP/DevOps.
- La capacidad y fecha final se recalibran al terminar Sprint 0.

## Aprobación requerida

Para convertir estas propuestas en decisiones definitivas debe registrarse nombre o rol aprobador y fecha. Después se reemplazará este estado por `APROBADO` y se actualizarán los documentos funcionales afectados.
