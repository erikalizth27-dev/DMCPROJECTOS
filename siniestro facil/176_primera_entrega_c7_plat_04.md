# Primera entrega — C7-PLAT-04 CI/CD

## Resultado

Se incorporó una definición controlada de Cloud Build para probar, construir, migrar, desplegar y validar el backend.

## Artefactos

- `backend/cloudbuild.yaml`.
- `backend/scripts/29_submit_platform_build.sh`.
- `backend/tests/test_cloudbuild_contract.py`.

## Secuencia

1. Instalar dependencias y ejecutar compilación y pruebas.
2. Construir imagen etiquetada por commit.
3. Publicar imagen en Artifact Registry.
4. Actualizar el Cloud Run Job migrador.
5. Ejecutar `alembic upgrade head` mediante el job exclusivo.
6. Actualizar Cloud Run solamente después de una migración exitosa.
7. Ejecutar smoke tests privados de liveness y readiness.

## Seguridad

- El pipeline exige una cuenta de despliegue dedicada.
- Runtime y migración conservan sus identidades y secretos separados.
- Cloud Build no recibe directamente credenciales PostgreSQL.
- Los logs se envían a Cloud Logging.
- La imagen se registra como resultado del build.

## Estado

Implementación inicial completada. Pendiente:

- Validar YAML y suite ampliada.
- Crear la identidad de despliegue y aplicar permisos mínimos.
- Ejecutar el pipeline real.
- Verificar migración, despliegue y smoke tests.
