# Evidencia — Autenticación inicial del frontend

## Resultado

La primera implementación de autenticación React quedó validada técnicamente.

## Alcance

- Inicio de sesión con correo y contraseña mediante Identity Platform.
- Sesión conservada únicamente en memoria.
- Pantallas de reporte y consulta protegidas.
- Token humano inyectado en el cliente HTTP.
- Ninguna credencial de cuenta de servicio incluida en React.
- Preparación para integración posterior mediante BFF en Cloud Run.

## Validación Cloud Shell

- `npm run typecheck`: aprobado.
- `npm run build`: aprobado.
- Vite: 33 módulos transformados.
- HTML: 0.54 kB.
- CSS: 7.54 kB.
- JavaScript: 202.65 kB.
- Árbol Git: limpio después de la compilación.

## Pendientes

- Configurar correo/contraseña en Identity Platform.
- Crear una API key web restringida.
- Asignar claims funcionales aprobados.
- Implementar y desplegar el BFF.
- Ejecutar la integración autenticada de extremo a extremo.
