# Evidencia segunda entrega S2-BE-01 — Cloud Shell

## Contexto

- Fecha: 28 de agosto de 2026.
- Rama: `agent/sprint-2-backend`.
- Incremento: `S2-BE-01`.
- Entrega: persistencia, auditoría y API de cobertura.

## Resultado automatizado

```text
110 passed, 1 warning in 1.34s
20260828_02 (head)
```

Las seis pruebas nuevas cubren el contrato HTTP y las garantías estructurales del repositorio PostgreSQL. Las 104 pruebas anteriores permanecen aprobadas.

## Controles incluidos

- Bloqueo de la fila del siniestro.
- Revalidación de la versión antes de persistir.
- Persistencia de deducible y estado de validación.
- Transición a `validando_cobertura`.
- Incremento de versión.
- Evento `cobertura_verificada`.
- Revisión humana cuando la cobertura no está activa.
- Uso explícito del adaptador simulado aprobado.

## Pendiente

Ejecutar el escenario controlado contra PostgreSQL con rollback y confirmar cero registros residuales.
