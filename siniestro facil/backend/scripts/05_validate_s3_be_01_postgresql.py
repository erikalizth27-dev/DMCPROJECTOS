from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.request_assistance import (
    AssistanceRequestError,
    RequestAssistanceCommand,
    RequestAssistanceService,
)
from siniestro_facil.domain.assistance import AssistanceStatus
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.provider_adapter import (
    SimulatedProviderAdapter,
)
from siniestro_facil.persistence.assistance_repository import (
    PostgreSQLAssistanceRepository,
)
from siniestro_facil.persistence.models import (
    Asistencia,
    EventoLineaTiempo,
    IdentidadActor,
    Proveedor,
    Siniestro,
    SolicitudAsistenciaIdempotente,
    UsuarioInterno,
)


SUBJECT = "s3-be-01-supervisor-synthetic"
TENANT = "s3-be-01-tenant-synthetic"
IDEMPOTENCY_KEY = "assistance-idem-postgresql-0001"


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no configurada")

    engine = create_engine(database_url, pool_pre_ping=True)
    claim_id: int | None = None
    assistance_id: int | None = None
    original_assistance_count: int | None = None
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
            provider_id = connection.execute(
                select(Proveedor.id_proveedor)
                .order_by(Proveedor.id_proveedor)
                .limit(1)
            ).scalar_one_or_none()
            if claim_id is None:
                raise RuntimeError(
                    "No existe un siniestro para ejecutar la prueba"
                )
            if provider_id is None:
                raise RuntimeError(
                    "No existe un proveedor para ejecutar la prueba"
                )

            original_assistance_count = connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one()
            original_event_count = connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one()
            original_request_count = connection.execute(
                select(func.count())
                .select_from(SolicitudAsistenciaIdempotente)
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
            provider = SimulatedProviderAdapter()
            service = RequestAssistanceService(
                PostgreSQLAssistanceRepository(factory),
                provider,
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
            command = RequestAssistanceCommand(
                claim_id=claim_id,
                provider_id=provider_id,
                assistance_type="grua",
                reason="Validación PostgreSQL sintética S3-BE-01",
            )
            payload = {
                "proveedorId": provider_id,
                "tipoAsistencia": "grua",
                "motivo": command.reason,
            }

            first = service.execute(
                command,
                principal,
                idempotency_key=IDEMPOTENCY_KEY,
                request_payload=payload,
            )
            assistance_id = first.id
            assert first.status is AssistanceStatus.SENT
            assert first.attempt == 1
            assert len(provider.dispatches) == 1

            persisted = connection.execute(
                select(
                    Asistencia.id_siniestro,
                    Asistencia.id_proveedor,
                    Asistencia.estado_solicitud,
                    Asistencia.numero_intento,
                    Asistencia.tipo_asistencia,
                    Asistencia.motivo,
                    Asistencia.referencia_externa,
                ).where(
                    Asistencia.id_asistencia == assistance_id
                )
            ).one()
            assert persisted.id_siniestro == claim_id
            assert persisted.id_proveedor == provider_id
            assert persisted.estado_solicitud == "enviada"
            assert persisted.numero_intento == 1
            assert persisted.tipo_asistencia == "grua"
            assert persisted.motivo == command.reason
            assert persisted.referencia_externa == (
                f"SIM-{assistance_id:08d}"
            )

            assert connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one() == original_assistance_count + 1
            assert connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one() == original_event_count + 2
            assert connection.execute(
                select(func.count())
                .select_from(SolicitudAsistenciaIdempotente)
            ).scalar_one() == original_request_count + 1

            replay = service.execute(
                command,
                principal,
                idempotency_key=IDEMPOTENCY_KEY,
                request_payload=payload,
            )
            assert replay == first
            assert len(provider.dispatches) == 1
            assert connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one() == original_assistance_count + 1

            print(f"Siniestro probado: {claim_id}")
            print(f"Proveedor probado: {provider_id}")
            print(f"Asistencia registrada: {assistance_id}")
            print("Persistencia y referencia externa: OK")
            print("Auditoría atómica: OK")
            print("Repetición idempotente: OK")
            print("Despacho simulado único: OK")

            try:
                service.execute(
                    RequestAssistanceCommand(
                        claim_id=claim_id,
                        provider_id=provider_id,
                        assistance_type="grua",
                        reason="Contenido diferente",
                    ),
                    principal,
                    idempotency_key=IDEMPOTENCY_KEY,
                    request_payload={
                        **payload,
                        "motivo": "Contenido diferente",
                    },
                )
            except AssistanceRequestError as error:
                assert error.code == "IDEMPOTENCY-CONFLICT"
                assert error.status_code == 409
                print("Conflicto idempotente: HTTP 409 — OK")
            else:
                raise AssertionError(
                    "No se produjo el conflicto idempotente"
                )

            print("S3-BE-01 PostgreSQL: OK")
        finally:
            outer.rollback()
            print("ROLLBACK ejecutado")

    if claim_id is not None:
        with engine.connect() as connection:
            restored_assistance_count = connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one()
            restored_event_count = connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one()
            restored_request_count = connection.execute(
                select(func.count())
                .select_from(SolicitudAsistenciaIdempotente)
            ).scalar_one()
            identity_count = connection.execute(
                select(func.count())
                .select_from(IdentidadActor)
                .where(
                    IdentidadActor.subject == SUBJECT,
                    IdentidadActor.tenant_id == TENANT,
                )
            ).scalar_one()

        assert restored_assistance_count == original_assistance_count
        assert restored_event_count == original_event_count
        assert restored_request_count == original_request_count
        assert identity_count == 0
        print("Asistencia sintética eliminada: OK")
        print("Auditoría sintética eliminada: OK")
        print("Idempotencia sintética eliminada: OK")
        print("Identidad sintética eliminada: OK")
        print("Limpieza validada: sin registros residuales")

    engine.dispose()
    print("VALIDACIÓN FINAL S3-BE-01 COMPLETADA")


if __name__ == "__main__":
    main()
