from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.manage_assistance import (
    AssistanceManagementError,
    ReassignAssistanceCommand,
    ReassignAssistanceService,
    RegisterProviderReplyCommand,
    RegisterProviderReplyService,
)
from siniestro_facil.application.request_assistance import (
    RequestAssistanceCommand,
    RequestAssistanceService,
)
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    ProviderResult,
)
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


SUBJECT = "s3-be-02-supervisor-synthetic"
TENANT = "s3-be-02-tenant-synthetic"
IDEMPOTENCY_KEY = "assistance-management-postgresql-0001"


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no configurada")

    engine = create_engine(database_url, pool_pre_ping=True)
    claim_id: int | None = None
    original_assistance_count: int | None = None
    original_event_count: int | None = None
    original_request_count: int | None = None
    original_provider_count: int | None = None

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
            original_provider_count = connection.execute(
                select(func.count()).select_from(Proveedor)
            ).scalar_one()

            provider_one = connection.execute(
                Proveedor.__table__
                .insert()
                .values(
                    tipo_proveedor="grua",
                    nombre="Proveedor sintético S3-BE-02 A",
                )
                .returning(Proveedor.id_proveedor)
            ).scalar_one()
            provider_two = connection.execute(
                Proveedor.__table__
                .insert()
                .values(
                    tipo_proveedor="grua",
                    nombre="Proveedor sintético S3-BE-02 B",
                )
                .returning(Proveedor.id_proveedor)
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
            repository = PostgreSQLAssistanceRepository(factory)
            request_service = RequestAssistanceService(
                repository,
                SimulatedProviderAdapter(),
            )
            reply_service = RegisterProviderReplyService(repository)
            reassign_service = ReassignAssistanceService(repository)

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
            request_command = RequestAssistanceCommand(
                claim_id=claim_id,
                provider_id=provider_one,
                assistance_type="grua",
                reason="Solicitud sintética S3-BE-02",
            )
            request_payload = {
                "proveedorId": provider_one,
                "tipoAsistencia": "grua",
                "motivo": request_command.reason,
            }
            first = request_service.execute(
                request_command,
                principal,
                idempotency_key=IDEMPOTENCY_KEY,
                request_payload=request_payload,
            )
            assert first.status is AssistanceStatus.SENT

            replied = reply_service.execute(
                RegisterProviderReplyCommand(
                    claim_id=claim_id,
                    assistance_id=first.id,
                    result=ProviderResult.NO_RESPONSE,
                    expected_attempt=1,
                    external_reference=f"SIM-{first.id:08d}",
                ),
                principal,
            )
            assert replied.status is AssistanceStatus.NO_RESPONSE

            try:
                reply_service.execute(
                    RegisterProviderReplyCommand(
                        claim_id=claim_id,
                        assistance_id=first.id,
                        result=ProviderResult.ACCEPTED,
                        expected_attempt=2,
                    ),
                    principal,
                )
            except AssistanceManagementError as error:
                assert error.code == "ASSISTANCE-VERSION-CONFLICT"
                assert error.status_code == 409
                print("Conflicto de intento: HTTP 409 — OK")
            else:
                raise AssertionError(
                    "No se produjo el conflicto de intento"
                )

            replacement = reassign_service.execute(
                ReassignAssistanceCommand(
                    claim_id=claim_id,
                    assistance_id=first.id,
                    new_provider_id=provider_two,
                    expected_attempt=1,
                    reason="Proveedor sin respuesta",
                ),
                principal,
            )
            assert replacement.status is AssistanceStatus.PENDING
            assert replacement.attempt == 2
            assert replacement.provider_id == provider_two

            rows = connection.execute(
                select(
                    Asistencia.id_asistencia,
                    Asistencia.id_proveedor,
                    Asistencia.estado_solicitud,
                    Asistencia.numero_intento,
                )
                .where(
                    Asistencia.id_asistencia.in_(
                        [first.id, replacement.id]
                    )
                )
                .order_by(Asistencia.numero_intento)
            ).all()
            assert len(rows) == 2
            assert rows[0].estado_solicitud == "sin_respuesta"
            assert rows[0].numero_intento == 1
            assert rows[1].estado_solicitud == "pendiente"
            assert rows[1].numero_intento == 2

            assert connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one() == original_assistance_count + 2
            assert connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one() == original_event_count + 4
            assert connection.execute(
                select(func.count())
                .select_from(SolicitudAsistenciaIdempotente)
            ).scalar_one() == original_request_count + 1

            print(f"Siniestro probado: {claim_id}")
            print(f"Proveedor inicial: {provider_one}")
            print(f"Proveedor nuevo: {provider_two}")
            print(f"Asistencia inicial: {first.id}")
            print(f"Asistencia reasignada: {replacement.id}")
            print("Respuesta sin_respuesta persistida: OK")
            print("Historial de dos intentos preservado: OK")
            print("Auditoría atómica de respuesta: OK")
            print("Auditoría atómica de reasignación: OK")
            print("S3-BE-02 PostgreSQL: OK")
        finally:
            outer.rollback()
            print("ROLLBACK ejecutado")

    if claim_id is not None:
        with engine.connect() as connection:
            assert connection.execute(
                select(func.count()).select_from(Asistencia)
            ).scalar_one() == original_assistance_count
            assert connection.execute(
                select(func.count())
                .select_from(EventoLineaTiempo)
                .where(EventoLineaTiempo.id_siniestro == claim_id)
            ).scalar_one() == original_event_count
            assert connection.execute(
                select(func.count())
                .select_from(SolicitudAsistenciaIdempotente)
            ).scalar_one() == original_request_count
            assert connection.execute(
                select(func.count()).select_from(Proveedor)
            ).scalar_one() == original_provider_count
            identity_count = connection.execute(
                select(func.count())
                .select_from(IdentidadActor)
                .where(
                    IdentidadActor.subject == SUBJECT,
                    IdentidadActor.tenant_id == TENANT,
                )
            ).scalar_one()
            assert identity_count == 0

        print("Asistencias sintéticas eliminadas: OK")
        print("Auditoría sintética eliminada: OK")
        print("Idempotencia sintética eliminada: OK")
        print("Proveedores sintéticos eliminados: OK")
        print("Identidad sintética eliminada: OK")
        print("Limpieza validada: sin registros residuales")

    engine.dispose()
    print("VALIDACIÓN FINAL S3-BE-02 COMPLETADA")


if __name__ == "__main__":
    main()
