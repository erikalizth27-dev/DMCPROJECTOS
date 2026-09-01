# Registro de aprobación S2-DEC-01

## Decisión

- ID: `S2-DEC-01`.
- Fecha: 28 de agosto de 2026.
- Responsable: Product Owner.
- Estado: **APROBADA**.

## Texto aprobado

> Continuar temporalmente con el adaptador simulado de pólizas durante Sprint 2.

## Alcance

- `S2-BE-01` utilizará únicamente pólizas sintéticas inyectadas.
- No se realizará integración con una API externa de pólizas.
- El resultado permitirá consultar cobertura y deducible.
- Una cobertura no activa no producirá un rechazo automático.
- Toda decisión sensible seguirá requiriendo revisión humana y auditoría.
- La sustitución por una API real queda condicionada a que el proveedor y contrato sean definidos.

## Impacto

La decisión elimina el bloqueo de Definition of Ready de `S2-BE-01`. `S2-DEC-02`, relacionada con Cloud Storage, región y retención de evidencias, permanece pendiente.
