# Evidencia — Paginación de línea de tiempo en React

## Objetivo

Permitir que el asegurado continúe consultando movimientos anteriores del siniestro cuando la primera página no contiene todo el historial visible.

## Alcance

- Uso de los parámetros existentes `despuesDe` y `cantidad`.
- Primera página limitada a 20 eventos.
- Acción accesible **Cargar más movimientos** cuando el backend devuelve `siguienteCursor`.
- Acumulación de páginas sin eliminar los eventos ya mostrados.
- Eliminación defensiva de duplicados por identificador de evento.
- Estado de carga independiente de la consulta principal.
- Error localizado: un fallo al paginar no elimina el resumen ni el historial cargado.
- Sin cambios en autenticación, RBAC, backend o infraestructura.

## Trazabilidad

| Contrato existente | Implementación |
|---|---|
| `GET /siniestros/{id}/linea-tiempo` | Cliente React tipado |
| Consulta `despuesDe` | Cursor de la siguiente página |
| Consulta `cantidad` | Tamaño de página de 20 |
| Respuesta `siguienteCursor` | Visibilidad del control de continuación |
| RBAC y redacción del backend | El frontend presenta únicamente la respuesta autorizada |

## Archivos modificados

- `frontend/src/api/client.ts`
- `frontend/src/App.tsx`
- `frontend/src/styles.css`

## Validación esperada

```bash
cd "$HOME/DMCPROJECTOS"
git switch agent/ciclo-8-linea-tiempo-paginacion
git pull --ff-only

cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
npm ci
npm run typecheck
npm run build
```

La fusión requiere autorización explícita del Product Owner.
