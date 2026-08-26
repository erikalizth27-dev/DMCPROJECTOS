\set ON_ERROR_STOP on
BEGIN;
SET search_path TO siniestro_facil, public;

CREATE OR REPLACE FUNCTION pg_temp.assert_sqlstate(test_name text, expected_state text, statement text)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    BEGIN
        EXECUTE statement;
    EXCEPTION WHEN OTHERS THEN
        IF SQLSTATE = expected_state THEN
            RAISE NOTICE 'OK: % (SQLSTATE %)', test_name, SQLSTATE;
            RETURN;
        END IF;
        RAISE EXCEPTION 'FALLO: %, esperaba SQLSTATE %, obtuvo %: %', test_name, expected_state, SQLSTATE, SQLERRM;
    END;
    RAISE EXCEPTION 'FALLO: %, la sentencia fue aceptada', test_name;
END;
$$;

INSERT INTO asegurado (numero_documento, tipo_documento, medio_contacto, nombre)
VALUES ('DOC-1','DNI','correo@ejemplo.test','Asegurado Uno'),
       ('DOC-2','DNI','otro@ejemplo.test','Asegurado Dos');

INSERT INTO reportante (id_asegurado, es_titular, medio_contacto)
VALUES (1,true,'correo@ejemplo.test');

INSERT INTO poliza (numero_poliza,id_asegurado,vigente_desde,vigente_hasta)
VALUES ('POL-1',1,'2026-01-01','2026-12-31'),
       ('POL-2',2,'2026-01-01','2026-12-31');

INSERT INTO vehiculo (placa,id_poliza) VALUES ('ABC123',1),('XYZ789',2);
INSERT INTO proveedor(tipo_proveedor,nombre) VALUES ('taller','Taller de prueba');

INSERT INTO siniestro (id_poliza,id_vehiculo,id_reportante,fecha_evento,ubicacion_evento,tipo_evento)
VALUES (1,1,1,'2026-06-01 10:00:00+00','Lima','colision'),
       (1,1,1,'2026-06-02 10:00:00+00','Lima','colision');

SELECT pg_temp.assert_sqlstate('NOT NULL de documento','23502',
    $$INSERT INTO asegurado(numero_documento,medio_contacto) VALUES (NULL,'x')$$);
SELECT pg_temp.assert_sqlstate('unicidad de numero de poliza','23505',
    $$INSERT INTO poliza(numero_poliza,id_asegurado,vigente_desde,vigente_hasta) VALUES ('POL-1',1,'2026-01-01','2026-12-31')$$);
SELECT pg_temp.assert_sqlstate('vigencia de poliza','23514',
    $$INSERT INTO poliza(numero_poliza,id_asegurado,vigente_desde,vigente_hasta) VALUES ('POL-X',1,'2026-12-31','2026-01-01')$$);
SELECT pg_temp.assert_sqlstate('titular debe referenciar asegurado','23514',
    $$INSERT INTO reportante(es_titular,medio_contacto) VALUES (true,'x')$$);
SELECT pg_temp.assert_sqlstate('FK de poliza','23503',
    $$INSERT INTO vehiculo(placa,id_poliza) VALUES ('BAD',999999)$$);
SELECT pg_temp.assert_sqlstate('vehiculo pertenece a la poliza del siniestro','23503',
    $$INSERT INTO siniestro(id_poliza,id_vehiculo,id_reportante,fecha_evento,ubicacion_evento,tipo_evento) VALUES (1,2,1,'2026-06-01','Lima','colision')$$);
SELECT pg_temp.assert_sqlstate('estado de siniestro valido','23514',
    $$UPDATE siniestro SET estado_actual='inventado' WHERE id_siniestro=1$$);
SELECT pg_temp.assert_sqlstate('deducible no negativo','23514',
    $$INSERT INTO cobertura(id_poliza,deducible) VALUES (1,-0.01)$$);
SELECT pg_temp.assert_sqlstate('numero de intento positivo','23514',
    $$INSERT INTO asistencia(id_siniestro,estado_solicitud,numero_intento) VALUES (1,'sin_respuesta',0)$$);
SELECT pg_temp.assert_sqlstate('presupuesto con vigencia coherente','23514',
    $$INSERT INTO presupuesto(id_siniestro,id_proveedor,vigencia_desde,vigencia_hasta) VALUES (1,1,'2026-12-31','2026-01-01')$$);

INSERT INTO evidencia(id_siniestro,tipo_evidencia,contenido_original_uri,hash,fecha_captura,fecha_recepcion)
VALUES (1,'foto_dano','s3://evidencias/original-1','sha256:uno','2026-06-01','2026-06-01 10:01+00');
SELECT pg_temp.assert_sqlstate('evidencia original inmutable','23000',
    $$UPDATE evidencia SET hash='sha256:alterado' WHERE id_evidencia=1$$);

SELECT pg_temp.assert_sqlstate('relacion sin autorrelacion','23514',
    $$INSERT INTO relacion_casos(id_siniestro_a,id_siniestro_b,criterio_relacion) VALUES (1,1,'accidente')$$);
INSERT INTO relacion_casos(id_siniestro_a,id_siniestro_b,criterio_relacion) VALUES (1,2,'accidente');
SELECT pg_temp.assert_sqlstate('relacion canonica y no invertida','23514',
    $$INSERT INTO relacion_casos(id_siniestro_a,id_siniestro_b,criterio_relacion) VALUES (2,1,'accidente')$$);

SELECT pg_temp.assert_sqlstate('pago positivo','23514',
    $$INSERT INTO pago(id_siniestro,monto,estado) VALUES (1,0,'bloqueado')$$);
SELECT pg_temp.assert_sqlstate('pago emitido requiere autorizacion','23514',
    $$INSERT INTO pago(id_siniestro,monto,estado) VALUES (1,100,'emitido')$$);

DO $$ BEGIN RAISE NOTICE 'OK: todas las pruebas de constraints finalizaron'; END $$;
ROLLBACK;
