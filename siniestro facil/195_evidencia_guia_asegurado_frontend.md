# Evidencia — Guía contextual para el asegurado

## Objetivo

Cumplir la orientación paso a paso de HU-02 mostrando al asegurado qué hacer según el estado visible y el siguiente paso de su siniestro.

## Alcance

- Traducción de estados y siguientes pasos técnicos a lenguaje humano.
- Tarjeta destacada **Qué hacer ahora** dentro de la consulta del caso.
- Orientación específica para los estados públicos definidos por RF-09.
- Referencia al historial como fuente de cambios visibles.
- Instrucciones prudentes para mantener disponible el medio de contacto y conservar evidencia original cuando corresponda.
- Respuesta alternativa segura para cualquier estado futuro no reconocido.
- Sin exposición de subestados internos.
- Sin promesas de tiempos de asistencia, reparación o pago.
- Sin cambios en backend, RBAC, autenticación o infraestructura.

## Trazabilidad

| Fuente | Cobertura |
|---|---|
| HU-02 | Instrucciones paso a paso en lenguaje humano |
| HU-06 | Estado claro y siguiente paso |
| RF-09 | Estados públicos del siniestro |
| RF-10 | Vista de estado y siguiente paso sin subestados internos |
| RF-18 | Historial como fuente de cambios visibles |

## Archivos modificados

- `frontend/src/App.tsx`
- `frontend/src/styles.css`

## Validación esperada

```bash
cd "$HOME/DMCPROJECTOS"
git switch agent/ciclo-8-guia-asegurado
git pull --ff-only

cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
npm ci
npm run typecheck
npm run build
```

La fusión requiere autorización explícita del Product Owner.
