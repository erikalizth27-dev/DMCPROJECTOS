# Evidencia — Renovación automática de sesión React

## Objetivo

Evitar que una sesión autenticada deje de funcionar cuando vence el ID token de Identity Platform durante el uso del frontend.

## Alcance

- Consumo de `securetoken.googleapis.com/v1/token` mediante el `refreshToken` emitido al iniciar sesión.
- Renovación programada cinco minutos antes de `expiresAt`.
- Sustitución del ID token, refresh token y nueva fecha de expiración.
- Conservación de la identidad visible del usuario.
- Cancelación del temporizador al cerrar sesión o reemplazar la sesión.
- Cierre seguro de sesión cuando Identity Platform rechaza la renovación.
- Tokens únicamente en memoria; sin impresión, almacenamiento local ni incorporación al repositorio.
- Sin cambios en RBAC, BFF, backend o infraestructura.

## Trazabilidad

| Riesgo | Control |
|---|---|
| ID token vencido durante una operación | Renovación anticipada |
| Rotación del refresh token | Se conserva el valor más reciente de la respuesta |
| Temporizador obsoleto | Limpieza en el ciclo de vida de React |
| Renovación rechazada | Sesión eliminada y retorno al inicio de sesión |
| Exposición de credenciales | Estado exclusivamente en memoria |

## Archivos modificados

- `frontend/src/auth/identityPlatform.ts`
- `frontend/src/auth/AuthContext.tsx`

## Validación esperada

```bash
cd "$HOME/DMCPROJECTOS"
git switch agent/ciclo-8-renovacion-sesion
git pull --ff-only

cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
npm ci
npm run typecheck
npm run build
```

La fusión requiere autorización explícita del Product Owner.
