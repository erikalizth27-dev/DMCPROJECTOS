# Decisión — Autenticación y BFF del frontend

## Estado

Aprobada por el Product Owner durante el Ciclo 8.

## Decisiones

- Autenticación humana: Identity Platform.
- Método inicial: correo electrónico y contraseña.
- Integración: BFF desplegado en Cloud Run.
- Backend productivo: permanece privado.
- El BFF utilizará una cuenta de servicio propia para invocar el backend.
- El token humano se enviará en `Authorization`.
- El token de servicio se enviará en `X-Serverless-Authorization`.
- React no incluirá credenciales GCP ni claves de cuentas de servicio.
- La sesión inicial se mantiene únicamente en memoria.

## Primera implementación

- Formulario de acceso accesible.
- Cliente REST de Identity Platform.
- Contexto React para sesión en memoria.
- Token disponible para el cliente HTTP después de autenticar.
- Mensajes de error sin revelar detalles del proveedor.

## Pendientes

- Configurar correo/contraseña en Identity Platform.
- Obtener la API key pública restringida para la aplicación web.
- Implementar y desplegar el BFF.
- Asignar claims aprobados: `role`, `actor_type` y `tenant_id`.
