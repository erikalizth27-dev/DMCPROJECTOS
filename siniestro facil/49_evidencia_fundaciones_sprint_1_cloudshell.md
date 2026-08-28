# Evidencia de fundaciones — Sprint 1 en Cloud Shell

## Ejecución

- Entorno: Google Cloud Shell.
- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Rama: `agent/sprint-1-backend`.
- Python: 3.12.3.
- Pytest: 8.4.2.

## Validaciones

```bash
python -m compileall -q src tests alembic
python -m pytest -v
```

## Resultado

- Compilación: correcta.
- Pruebas recopiladas: 63.
- Pruebas aprobadas: 63.
- Fallos: 0.
- Duración reportada: 1.02 segundos.

Las diez pruebas agregadas validan:

- búsqueda de póliza por número y documento;
- normalización de identificadores;
- consistencia cuando se proporcionan ambos identificadores;
- rechazo de datos sintéticos duplicados;
- vigencia de cobertura para la fecha del evento;
- mapeo SQLAlchemy al esquema `siniestro_facil`;
- columna de versión optimista;
- commit de una unidad de trabajo exitosa;
- rollback ante una excepción.

## Conclusión

Las fundaciones compartidas del Sprint 1 están aprobadas técnicamente. El avance acumulado alcanza 15% y puede comenzar S1-BE-01.
