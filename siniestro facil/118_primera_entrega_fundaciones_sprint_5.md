# Primera entrega de fundaciones — Sprint 5

## Alcance implementado

- Catálogo de ocho tipos de señal del modelo físico.
- Orígenes `deterministica` y `modelo`.
- Severidades `baja`, `media`, `alta` y `critica`.
- Efectos aprobados por S5-DEC-01.
- Estados de revisión de alerta.
- Criterios de relación entre casos.
- Normalización exacta estable.
- Orden canónico de pares de siniestros y prohibición de autorrelación.
- Adaptador determinístico versionado con entradas y explicación reproducibles.
- Modelos SQLAlchemy para `politica_alerta`, `alerta`, `senal_riesgo` y `relacion_casos`.

## Seguridad funcional

- Una alerta solo produce prioridad, derivación o bloqueo temporal del pago.
- No existe confirmación automática de fraude.
- No existe rechazo automático.
- Solo el valor booleano explícito `true` activa una regla simulada.
- No se infieren datos ausentes.

## Pruebas

- Once pruebas nuevas.
- Total esperado: **281 pruebas**.
- No se requiere migración: las cuatro tablas ya existen en el esquema físico.
- Estado: pendiente de validación en Cloud Shell.
