# Propuesta para aprobación — Identidad y claims

## Estado

`PROPUESTA PARA APROBACIÓN`. Este documento define arquitectura y contrato de
identidad. No habilita, configura ni despliega servicios en GCP.

## Recomendación ID-01 — Proveedor de identidad humano

Usar **Identity Platform** como autoridad de autenticación de los usuarios de la
aplicación durante el piloto.

- Asegurado/reportante: inicio de sesión administrado por Identity Platform.
- Operador, ajustador, investigador y supervisor: federación del proveedor
  corporativo mediante OIDC/SAML; si aún no existe, proveedor Google del piloto.
- Taller/proveedor: cuenta propia sólo cuando el flujo requiera acceso directo;
  durante el piloto conserva alcance asociado a una orden válida.

Motivo: mantiene una única validación JWT en el backend, permite federación y
cumple la restricción de desarrollar la solución sobre Google Cloud.

## Recomendación ID-02 — Identidad entre servicios

Usar cuentas de servicio de Google Cloud e IAM para comunicación entre cargas.
Los tokens de cuentas de servicio no representan usuarios humanos y no deben
recibir roles funcionales como `supervisor` o `ajustador`.

## Recomendación ID-03 — Claims mínimos

| Claim | Origen | Uso |
|---|---|---|
| `iss` | Identity Platform | Validar emisor |
| `aud` | Identity Platform | Validar audiencia del backend |
| `sub` | Identity Platform | Identificador estable del principal |
| `iat` | Identity Platform | Momento de emisión |
| `exp` | Identity Platform | Expiración obligatoria |
| `auth_time` | Identity Platform | Evaluar autenticación reciente en acciones sensibles |
| `actor_type` | Claim controlado | `externo`, `interno` o `proveedor` |
| `role` | Claim controlado | Rol funcional aprobado por RBAC |
| `tenant_id` | Claim controlado | Organización o dominio lógico del principal |

Roles permitidos:

```text
asegurado
operador
ajustador
taller
investigador_fraude
supervisor
```

## Recomendación ID-04 — Alcance fuera del token

El JWT no debe contener listas de siniestros, pólizas, talleres, asignaciones ni
permisos individuales. El backend obtiene el alcance vigente desde PostgreSQL:

- caso propio del asegurado;
- asignación activa del operador/ajustador;
- orden válida del taller;
- autorización de investigación;
- acceso transversal auditado del supervisor.

Esto evita tokens grandes y autorizaciones obsoletas después de una reasignación.

## Recomendación ID-05 — Controles del backend

En cada petición protegida, el backend debe:

1. Verificar firma, emisor, audiencia, emisión y expiración.
2. Rechazar roles desconocidos mediante denegación por defecto.
3. Resolver el usuario interno o actor externo usando `sub` y `tenant_id`.
4. Aplicar permiso del rol y alcance del recurso.
5. Registrar decisiones sensibles con `sub`, acción, recurso, resultado y
   `correlationId`, sin almacenar el token.
6. Exigir un usuario supervisor diferente del preparador para autorizar pagos.

## Recomendación ID-06 — Datos que no deben registrarse

- JWT completo.
- Credenciales, códigos temporales o secretos.
- Claims no necesarios para auditoría.
- Documentos completos o evidencia binaria.
- Datos personales en mensajes de error.

## Respuestas HTTP

| Situación | HTTP |
|---|---:|
| Token ausente, inválido, vencido o con audiencia incorrecta | 401 |
| Rol autenticado sin permiso | 403 |
| Recurso fuera de alcance y cuya existencia debe ocultarse | 404 |
| Separación de funciones o regla de negocio incumplida | 422 |

## Fuera de alcance actual

- Configuración real de Identity Platform.
- Creación de tenants, proveedores OIDC/SAML y cuentas.
- Gestión operativa de IAM.
- CI/CD, observabilidad y despliegue en Cloud Run.

## Criterios de aprobación

La propuesta queda aprobada cuando el Product Owner confirma ID-01 a ID-06. La
aprobación autoriza actualizar SPEC, OpenAPI, configuración y pruebas locales;
no autoriza habilitar ni configurar servicios en GCP.
