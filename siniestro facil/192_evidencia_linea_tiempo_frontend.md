# Evidencia — Línea de tiempo en frontend React

## Objetivo

Permitir que el asegurado consulte el historial auditable de su siniestro desde la vista existente **Consultar mi caso**.

## Alcance

- Cliente tipado para `GET /siniestros/{id}/linea-tiempo?cantidad=20`.
- Consulta paralela del resumen y la línea de tiempo.
- Presentación cronológica de tipo y fecha de cada evento visible.
- Estado vacío cuando el caso no contiene movimientos visibles.
- Limpieza del historial anterior cuando la consulta falla.
- Reutilización del token de Identity Platform a través del BFF.
- Sin exposición de detalles internos ni ampliación de permisos.

## Trazabilidad

| Origen | Cobertura |
|---|---|
| Sprint 6 — línea de tiempo consolidada | Consulta de eventos del siniestro |
| RBAC del backend | El nivel de detalle continúa decidido por el backend |
| Ciclo 8 — frontend React | Experiencia del asegurado autenticado |

## Archivos

- `frontend/src/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/App.tsx`
- `frontend/src/styles.css`

## Validación esperada en Cloud Shell

```bash
cd "$HOME/DMCPROJECTOS"
git switch agent/ciclo-8-linea-tiempo
git pull --ff-only

cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
npm ci
npm run typecheck
npm run build
```

La fusión requiere autorización explícita del Product Owner.
