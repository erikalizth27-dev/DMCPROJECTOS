# Evidencia — Adaptador Identity Platform del backend

Fecha: 2026-09-04  
Estado: implementación pendiente de validación

## Hallazgo productivo

La autenticación de Identity Platform y el BFF funcionaron, pero una petición
autenticada devolvió `AUTHENTICATION-REQUIRED`. La causa estaba en
`get_authenticated_principal`: era una dependencia temporal que rechazaba todas
las solicitudes hasta que existiera un adaptador criptográfico.

## Corrección

- Extraer exclusivamente credenciales `Bearer`.
- Verificar la firma Firebase/Identity Platform mediante `google-auth`.
- Validar audiencia contra el ID del proyecto.
- Validar emisor, tiempos y claims funcionales mediante el contrato de dominio.
- Convertir el token verificado en `AuthenticatedPrincipal`.
- Responder 401 sin filtrar detalles criptográficos.
- Responder 503 cuando la identidad productiva no está configurada.

## Configuración productiva

```text
IDENTITY_AUDIENCE=project-77c17016-86bc-4fc4-a97
IDENTITY_ISSUER=https://securetoken.google.com/project-77c17016-86bc-4fc4-a97
```

## Criterio de cierre

La suite completa debe pasar y una solicitud con token real debe atravesar
React, BFF y backend sin devolver `AUTHENTICATION-REQUIRED`.
