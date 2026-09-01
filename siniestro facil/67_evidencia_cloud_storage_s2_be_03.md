# Evidencia Cloud Storage S2-BE-03

## Contexto

- Fecha: 1 de septiembre de 2026.
- Bucket: `project-77c17016-86bc-4fc4-a97-siniestro-evidencias`.
- Región: `US-CENTRAL1`.
- Incremento: `S2-BE-03`.

## Escenario

Se cargaron dos contenidos sintéticos sobre la misma clave para comprobar el versionado del bucket. Luego se descargó la generación vigente, se calculó SHA-256 y se eliminaron todas las generaciones.

## Resultado de integridad

```text
SHA esperado:    b6dbe9f697df728fabc178b3e952fcd8cb4e509c5455cc6316f879fd5e10fb43
SHA descargado:  b6dbe9f697df728fabc178b3e952fcd8cb4e509c5455cc6316f879fd5e10fb43
SHA-256 VALIDADO: OK
```

## Resultado de versionado y limpieza

```text
Removing evidencia-sintetica.txt#1788233554020739
Removing evidencia-sintetica.txt#1788233568504121
Completed 2/2
One or more URLs matched no objects.
LIMPIEZA CLOUD STORAGE: OK
```

El mensaje de ausencia de objetos posterior a la eliminación confirma que no quedaron generaciones sintéticas.

## Controles confirmados

- Carga de objeto.
- Creación de dos generaciones distintas.
- Descarga de la generación vigente.
- SHA-256 idéntico al contenido esperado.
- Eliminación explícita de todas las generaciones.
- Cero objetos residuales bajo la clave sintética.

## Conclusión

La infraestructura real de Cloud Storage satisface la configuración aprobada y preserva generaciones. La aplicación continuará prohibiendo la sobrescritura de originales aunque el bucket mantenga versionado como defensa adicional.
