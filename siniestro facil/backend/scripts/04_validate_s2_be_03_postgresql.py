from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.register_evidence import (
    EvidenceRegistrationError,
    RegisterEvidenceCommand,
    RegisterEvidenceService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.evidence_storage import APPROVED_BUCKET
from siniestro_facil.persistence.evidence_repository import (
    PostgreSQLEvidenceRepository,
)
from siniestro_facil.persistence.models import (
    Evidencia,
    EventoLineaTiempo,
    IdentidadActor,
    Siniestro,
    SolicitudEvidenciaIdempotente,
    UsuarioInterno,
)


SUBJECT = "s2-be-03-supervisor-synthetic"
TENANT = "s2-be-03-tenant-synthetic"
IDEMPOTENCY_KEY = "evidence-idem-postgresql-0001"
DIGEST = (
    "b6dbe9f697df728fabc178b3e952fcd8"
    "cb4e509c5455cc6316f879fd5e10fb43"
)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no configurada")

    engine = create_engine(database_url, pool_pre_ping=True)
    claim_id: int | None = None
    original_evidence_count: int | None = None
    original_event_count: int | None = None
    original_request_count: int | None = None

    with engine.connect() as connection:
        outer = connection.begin()
        try:
            claim_id = connection.execute(
                select(Siniestro.id_siniestro)
                .order_by(Siniestro.id_siniestro)
                .limit(1)
            ).scalar_one_or_none()
            if claim_id is None:
                raise RuntimeError(
                    "No existe un siniestro para ejecutar la prueba"
                )

            original_evidence_count = connection.execute(
                select(func.count())
                .select_from(Evidencia)
                .where(Evidencia.id_siniestro == claim_id)
            ).scalar_one()
            original_event_count = connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one()
            original_request_count = connection.execute(
                select(func.count())
                .select_from(SolicitudEvidenciaIdempotente)
            ).scalar_one()

            user_id = connection.execute(
                UsuarioInterno.__table__
                .insert()
                .values(rol="supervisor")
                .returning(UsuarioInterno.id_usuario)
            ).scalar_one()
            connection.execute(
                IdentidadActor.__table__.insert().values(
                    subject=SUBJECT,
                    tenant_id=TENANT,
                    actor_type="interno",
                    id_usuario=user_id,
                )
            )

            factory = sessionmaker(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )
            service = RegisterEvidenceService(
                PostgreSQLEvidenceRepository(factory)
            )
            now = datetime.now(timezone.utc)
            principal = AuthenticatedPrincipal(
                subject=SUBJECT,
                role=PrincipalRole.SUPERVISOR,
                actor_type=ActorType.INTERNO,
                tenant_id=TENANT,
                issued_at=now - timedelta(minutes=1),
                expires_at=now + timedelta(hours=1),
                authenticated_at=now - timedelta(minutes=1),
            )
            uri = (
                f"gs://{APPROVED_BUCKET}/siniestros/{claim_id}/"
                "originales/evidencia-postgresql-sintetica.txt"
            )
            command = RegisterEvidenceCommand(
                claim_id=claim_id,
                evidence_type="documento_sintetico",
                original_uri=uri,
                sha256_hex=DIGEST,
                captured_at=None,
                source="prueba_s2_be_03",
                derived_from_id=None,
                metadata={
                    "generation": "synthetic-1",
                    "bucket_versioning": True,
                },
            )
            payload = {
                "tipoEvidencia": command.evidence_type,
                "contenidoOriginalUri": command.original_uri,
                "hash": command.sha256_hex,
                "fuente": command.source,
                "metadatos": command.metadata,
            }

            first = service.execute(
                command,
                principal,
                idempotency_key=IDEMPOTENCY_KEY,
                request_payload=payload,
            )
            evidence_id = first.id

            persisted = connection.execute(
                select(
                    Evidencia.id_siniestro,
                    Evidencia.contenido_original_uri,
                    Evidencia.hash,
                    Evidencia.metadatos,
                ).where(Evidencia.id_evidencia == evidence_id)
            ).one()
            assert persisted.id_siniestro == claim_id
            assert persisted.contenido_original_uri == uri
            assert persisted.hash == DIGEST
            assert persisted.metadatos["bucket_versioning"] is True

            assert connection.execute(
                select(func.count())
                .select_from(Evidencia)
                .where(Evidencia.id_siniestro == claim_id)
            ).scalar_one() == original_evidence_count + 1
            assert connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one() == original_event_count + 1
            assert connection.execute(
                select(func.count())
                .select_from(SolicitudEvidenciaIdempotente)
            ).scalar_one() == original_request_count + 1

            replay = service.execute(
                command,
                principal,
                idempotency_key=IDEMPOTENCY_KEY,
                request_payload=payload,
            )
            assert replay == first
            assert connection.execute(
                select(func.count())
                .select_from(Evidencia)
                .where(Evidencia.id_siniestro == claim_id)
            ).scalar_one() == original_evidence_count + 1

            print(f"Siniestro probado: {claim_id}")
            print(f"Evidencia registrada: {evidence_id}")
            print("URI y SHA-256 persistidos: OK")
            print("Auditoría atómica: OK")
            print("Repetición idempotente: OK")

            try:
                service.execute(
                    command,
                    principal,
                    idempotency_key=IDEMPOTENCY_KEY,
                    request_payload={
                        **payload,
                        "tipoEvidencia": "contenido_modificado",
                    },
                )
            except EvidenceRegistrationError as error:
                assert error.code == "IDEMPOTENCY-CONFLICT"
                assert error.status_code == 409
                print("Conflicto idempotente: HTTP 409 — OK")
            else:
                raise AssertionError(
                    "No se produjo el conflicto idempotente"
                )

            try:
                with connection.begin_nested():
                    connection.execute(
                        update(Evidencia)
                        .where(Evidencia.id_evidencia == evidence_id)
                        .values(
                            contenido_original_uri=uri + ".modificado"
                        )
                    )
            except DBAPIError:
                print("Inmutabilidad PostgreSQL: OK")
            else:
                raise AssertionError(
                    "El trigger permitió modificar el original"
                )

            print("S2-BE-03 PostgreSQL: OK")
        finally:
            outer.rollback()
            print("ROLLBACK ejecutado")

    if claim_id is not None:
        with engine.connect() as connection:
            restored_evidence_count = connection.execute(
                select(func.count())
                .select_from(Evidencia)
                .where(Evidencia.id_siniestro == claim_id)
            ).scalar_one()
            restored_event_count = connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one()
            restored_request_count = connection.execute(
                select(func.count())
                .select_from(SolicitudEvidenciaIdempotente)
            ).scalar_one()
            identity_count = connection.execute(
                select(func.count())
                .select_from(IdentidadActor)
                .where(
                    IdentidadActor.subject == SUBJECT,
                    IdentidadActor.tenant_id == TENANT,
                )
            ).scalar_one()

        assert restored_evidence_count == original_evidence_count
        assert restored_event_count == original_event_count
        assert restored_request_count == original_request_count
        assert identity_count == 0
        print("Evidencia sintética eliminada: OK")
        print("Auditoría sintética eliminada: OK")
        print("Idempotencia sintética eliminada: OK")
        print("Identidad sintética eliminada: OK")
        print("Limpieza validada: sin registros residuales")

    engine.dispose()
    print("VALIDACIÓN FINAL S2-BE-03 COMPLETADA")


if __name__ == "__main__":
    main()
