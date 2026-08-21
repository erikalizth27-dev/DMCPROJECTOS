\set ON_ERROR_STOP on

BEGIN;
SET LOCAL search_path TO siniestro_facil, public;

DO $seed$
DECLARE
    v_lote constant text := 'SYN-20260820';
    v_total constant integer := 10;
    i integer;
    v_asegurado bigint;
    v_reportante bigint;
    v_poliza bigint;
    v_vehiculo bigint;
    v_siniestro bigint;
    v_siniestro_anterior bigint;
    v_evidencia bigint;
    v_taller bigint;
    v_grua bigint;
    v_presupuesto bigint;
    v_usuario bigint;
    v_autorizacion bigint;
    v_politica bigint;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM asegurado
        WHERE numero_documento LIKE v_lote || '-%'
    ) THEN
        RAISE EXCEPTION
            'El lote % ya existe. No se insertaron duplicados.', v_lote;
    END IF;

    INSERT INTO politica_alerta (version, regla_bloqueo, vigente_desde)
    VALUES (
        v_lote,
        '{"origen":"datos_sinteticos","bloqueo":"revision_manual"}'::jsonb,
        DATE '2026-01-01'
    )
    RETURNING id_politica_alerta INTO v_politica;

    FOR i IN 1..v_total LOOP
        INSERT INTO asegurado (
            numero_documento, tipo_documento, medio_contacto, nombre
        )
        VALUES (
            v_lote || '-' || lpad(i::text, 4, '0'),
            'documento_sintetico',
            'synthetic+' || i || '@example.invalid',
            'Asegurado Sintetico ' || i
        )
        RETURNING id_asegurado INTO v_asegurado;

        INSERT INTO reportante (id_asegurado, es_titular, medio_contacto)
        VALUES (v_asegurado, true, 'synthetic+' || i || '@example.invalid')
        RETURNING id_reportante INTO v_reportante;

        INSERT INTO poliza (
            numero_poliza, id_asegurado, vigente_desde, vigente_hasta
        )
        VALUES (
            v_lote || '-POL-' || lpad(i::text, 4, '0'),
            v_asegurado,
            DATE '2026-01-01',
            DATE '2026-12-31'
        )
        RETURNING id_poliza INTO v_poliza;

        INSERT INTO vehiculo (placa, id_poliza)
        VALUES ('SYN' || lpad(i::text, 4, '0'), v_poliza)
        RETURNING id_vehiculo INTO v_vehiculo;

        INSERT INTO cobertura (id_poliza, deducible, estado_validacion)
        VALUES (v_poliza, 500.00 + (i * 25), 'validada');

        INSERT INTO siniestro (
            id_poliza, id_vehiculo, id_reportante, fecha_evento,
            ubicacion_evento, tipo_evento, descripcion, danos_aparentes,
            estado_actual, canal_origen
        )
        VALUES (
            v_poliza,
            v_vehiculo,
            v_reportante,
            timestamptz '2026-08-01 10:00:00-04' + (i || ' hours')::interval,
            'Ubicacion sintetica ' || i,
            CASE WHEN i % 2 = 0 THEN 'colision' ELSE 'dano_estacionado' END,
            'Caso sintetico para validacion tecnica; no representa un siniestro real.',
            'Danos sinteticos de prueba ' || i,
            CASE WHEN i % 3 = 0 THEN 'en_evaluacion' ELSE 'reportado' END,
            'carga_sintetica'
        )
        RETURNING id_siniestro INTO v_siniestro;

        INSERT INTO participante (
            id_siniestro, rol, nombre_declarado, nombre_normalizado
        ) VALUES (
            v_siniestro, 'conductor',
            'Participante Sintetico ' || i,
            'PARTICIPANTE SINTETICO ' || i
        );

        INSERT INTO evidencia (
            id_siniestro, tipo_evidencia, contenido_original_uri, hash,
            metadatos, fecha_captura, fuente, ubicacion_captura,
            dispositivo_captura
        ) VALUES (
            v_siniestro,
            'fotografia',
            'gs://synthetic-invalid/' || v_lote || '/caso-' || i || '/original.jpg',
            md5(v_lote || '-evidencia-' || i),
            jsonb_build_object('synthetic', true, 'lote', v_lote, 'caso', i),
            timestamptz '2026-08-01 10:05:00-04' + (i || ' hours')::interval,
            'generador_sintetico',
            'Ubicacion sintetica ' || i,
            'Dispositivo sintetico'
        )
        RETURNING id_evidencia INTO v_evidencia;

        INSERT INTO evidencia (
            id_siniestro, tipo_evidencia, contenido_original_uri, hash,
            metadatos, fecha_captura, fuente, version_derivada_de
        ) VALUES (
            v_siniestro,
            'fotografia_derivada',
            'gs://synthetic-invalid/' || v_lote || '/caso-' || i || '/derivada.jpg',
            md5(v_lote || '-derivada-' || i),
            jsonb_build_object('synthetic', true, 'transformacion', 'miniatura'),
            timestamptz '2026-08-01 10:06:00-04' + (i || ' hours')::interval,
            'generador_sintetico',
            v_evidencia
        );

        INSERT INTO proveedor (tipo_proveedor, nombre)
        VALUES ('taller', 'Taller Sintetico ' || i)
        RETURNING id_proveedor INTO v_taller;

        INSERT INTO proveedor (tipo_proveedor, nombre)
        VALUES ('grua', 'Grua Sintetica ' || i)
        RETURNING id_proveedor INTO v_grua;

        INSERT INTO asistencia (
            id_siniestro, id_proveedor, estado_solicitud, numero_intento
        ) VALUES (v_siniestro, v_grua, 'aceptada', 1);

        INSERT INTO inspeccion (id_siniestro, fecha_programada)
        VALUES (
            v_siniestro,
            timestamptz '2026-08-03 09:00:00-04' + (i || ' days')::interval
        );

        INSERT INTO presupuesto (
            id_siniestro, id_proveedor, diagnostico,
            vigencia_desde, vigencia_hasta, estado
        ) VALUES (
            v_siniestro,
            v_taller,
            'Diagnostico sintetico ' || i,
            DATE '2026-08-05',
            DATE '2026-09-05',
            'autorizado'
        )
        RETURNING id_presupuesto INTO v_presupuesto;

        INSERT INTO usuario_interno (rol)
        VALUES (CASE WHEN i % 2 = 0 THEN 'ajustador' ELSE 'operador' END)
        RETURNING id_usuario INTO v_usuario;

        INSERT INTO autorizacion (
            id_usuario_autoriza, objeto_autorizado
        ) VALUES (v_usuario, 'presupuesto_y_pago_sintetico_' || i)
        RETURNING id_autorizacion INTO v_autorizacion;

        INSERT INTO cambio_presupuesto (
            id_presupuesto, tipo_cambio, id_autorizacion
        ) VALUES (v_presupuesto, 'observacion', v_autorizacion);

        INSERT INTO alerta (
            id_siniestro, tipo, severidad, explicacion, datos_origen,
            modelo_o_regla, id_politica_alerta, estado_revision
        ) VALUES (
            v_siniestro,
            'alerta_sintetica',
            CASE WHEN i % 2 = 0 THEN 'media' ELSE 'baja' END,
            'Alerta creada exclusivamente para pruebas.',
            jsonb_build_object('synthetic', true, 'caso', i),
            'regla_sintetica_v1',
            v_politica,
            'pendiente'
        );

        INSERT INTO senal_riesgo (id_siniestro, tipo_senal, origen)
        VALUES (
            v_siniestro,
            CASE WHEN i % 2 = 0 THEN 'monto_atipico' ELSE 'poliza_reciente' END,
            CASE WHEN i % 2 = 0 THEN 'modelo' ELSE 'deterministica' END
        );

        INSERT INTO pago (id_siniestro, id_autorizacion, monto, estado)
        VALUES (v_siniestro, v_autorizacion, 1000.00 + (i * 100), 'emitido');

        INSERT INTO comunicacion (id_siniestro, contenido)
        VALUES (
            v_siniestro,
            'Comunicacion sintetica del caso ' || i || '. Sin destinatario real.'
        );

        INSERT INTO evento_linea_tiempo (
            id_siniestro, id_usuario, tipo_evento, detalle
        ) VALUES (
            v_siniestro,
            v_usuario,
            'carga_sintetica',
            jsonb_build_object('lote', v_lote, 'caso', i)
        );

        IF v_siniestro_anterior IS NOT NULL THEN
            INSERT INTO relacion_casos (
                id_siniestro_a, id_siniestro_b, criterio_relacion
            ) VALUES (
                LEAST(v_siniestro_anterior, v_siniestro),
                GREATEST(v_siniestro_anterior, v_siniestro),
                'taller'
            );
        END IF;

        v_siniestro_anterior := v_siniestro;
    END LOOP;

    RAISE NOTICE 'OK: lote % insertado con % siniestros sinteticos.',
        v_lote, v_total;
END;
$seed$;

DO $validate$
DECLARE
    v_lote constant text := 'SYN-20260820';
    v_siniestros integer;
    v_evidencias integer;
    v_relaciones integer;
BEGIN
    SELECT count(*)
      INTO v_siniestros
      FROM siniestro s
      JOIN poliza p ON p.id_poliza = s.id_poliza
     WHERE p.numero_poliza LIKE v_lote || '-POL-%';

    SELECT count(*)
      INTO v_evidencias
      FROM evidencia e
      JOIN siniestro s ON s.id_siniestro = e.id_siniestro
      JOIN poliza p ON p.id_poliza = s.id_poliza
     WHERE p.numero_poliza LIKE v_lote || '-POL-%';

    SELECT count(*)
      INTO v_relaciones
      FROM relacion_casos r
      JOIN siniestro s ON s.id_siniestro = r.id_siniestro_a
      JOIN poliza p ON p.id_poliza = s.id_poliza
     WHERE p.numero_poliza LIKE v_lote || '-POL-%';

    IF v_siniestros <> 10 OR v_evidencias <> 20 OR v_relaciones <> 9 THEN
        RAISE EXCEPTION
            'Validacion fallida: siniestros=%, evidencias=%, relaciones=%',
            v_siniestros, v_evidencias, v_relaciones;
    END IF;

    RAISE NOTICE
        'OK: integridad del lote validada: % siniestros, % evidencias, % relaciones.',
        v_siniestros, v_evidencias, v_relaciones;
END;
$validate$;

COMMIT;

SELECT
    'SYN-20260820' AS lote,
    count(*) AS siniestros_creados
FROM siniestro_facil.siniestro s
JOIN siniestro_facil.poliza p ON p.id_poliza = s.id_poliza
WHERE p.numero_poliza LIKE 'SYN-20260820-POL-%';
