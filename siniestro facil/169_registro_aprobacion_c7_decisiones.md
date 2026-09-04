# Registro de aprobación — Decisiones Ciclo 7

## Aprobación del Product Owner

Fecha: 2026-09-04.

El Product Owner aprueba C7-DEC-01 a C7-DEC-06:

- **C7-DEC-01:** región `us-central1` y servicio `siniestro-facil-backend-piloto`.
- **C7-DEC-02:** Cloud Run privado con invocación autenticada durante el piloto.
- **C7-DEC-03:** un único ambiente piloto inicialmente.
- **C7-DEC-04:** identidades separadas para runtime y migración, con secretos en Secret Manager y privilegio mínimo.
- **C7-DEC-05:** Artifact Registry y Cloud Build, con migración Alembic ejecutada de forma exclusiva antes del despliegue.
- **C7-DEC-06:** no fijar escalado, SLO ni umbrales de alertas sin datos y aprobación posterior.

## Efecto

- Quedan habilitados la validación de línea base y C7-PLAT-01.
- Se autoriza preparar los recursos definidos para el ambiente piloto cuando su incremento lo requiera.
- La exposición pública continúa fuera de alcance.
- Los parámetros de capacidad y alertas permanecen como decisiones futuras.
- La fusión a `main` requiere autorización explícita independiente.
