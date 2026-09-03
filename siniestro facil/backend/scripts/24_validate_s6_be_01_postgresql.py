from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.manage_payment import (
    AuthorizePaymentCommand,
    AuthorizePaymentService,
    PaymentOperationError,
    PreparePaymentCommand,
    PreparePaymentService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.domain.payment import PaymentStatus
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)
from siniestro_facil.persistence.models import (
    Alerta,
    AsignacionSiniestro,
    Autorizacion,
    EventoLineaTiempo,
    IdentidadActor,
    Pago,
    PoliticaAlerta,
    Siniestro,
    SolicitudAutorizacionPagoIdempotente,
    SolicitudPreparacionPagoIdempotente,
    UsuarioInterno,
)
from siniestro_facil.persistence.payment_repository import (
    PostgreSQLPaymentRepository,
)


TENANT = "tenant-s6-payment-validation"
MARKER = "Validación sintética S6-BE-01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def principal(
    *,
    subject: str,
    role: PrincipalRole,
    now: datetime,
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        subject=subject,
        tenant_id=TENANT,
        actor_type=ActorType.INTERNO,
        role=role,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
token = uuid4().hex
prepare_key = f"s6-payment-prepare-{token}"
authorize_key = f"s6-payment-authorize-{token}"
blocked_key = f"s6-payment-blocked-{token}"
subjects: list[str] = []
created: dict[str, list[int]] = {
    "users": [],
    "assignments": [],
    "payments": [],
    "authorizations": [],
    "alerts": [],
    "policies": [],
    "audits": [],
}
claim_id: int | None = None

with engine.connect() as connection:
    outer = connection.begin()
    try:
        claim_id = connection.execute(
            select(Siniestro.id_siniestro)
            .order_by(Siniestro.id_siniestro)
            .limit(1)
        ).scalar_one_or_none()
        require(claim_id is not None, "No existe siniestro para validar")
        now = datetime.now(timezone.utc)

        principals: dict[PrincipalRole, AuthenticatedPrincipal] = {}
        for role in (PrincipalRole.OPERADOR, PrincipalRole.SUPERVISOR):
            user_id = connection.execute(
                insert(UsuarioInterno)
                .values(rol=role.value)
                .returning(UsuarioInterno.id_usuario)
            ).scalar_one()
            created["users"].append(user_id)
            subject = f"s6-payment-{role.value}-{token}"
            subjects.append(subject)
            connection.execute(
                insert(IdentidadActor).values(
                    subject=subject,
                    tenant_id=TENANT,
                    actor_type=ActorType.INTERNO.value,
                    id_usuario=user_id,
                )
            )
            if role is PrincipalRole.OPERADOR:
                assignment_id = connection.execute(
                    insert(AsignacionSiniestro)
                    .values(
                        id_siniestro=claim_id,
                        id_usuario=user_id,
                        motivo=MARKER,
                        asignado_en=now,
                    )
                    .returning(AsignacionSiniestro.id_asignacion)
                ).scalar_one()
                created["assignments"].append(assignment_id)
            principals[role] = principal(
                subject=subject,
                role=role,
                now=now,
            )

        max_audit = connection.execute(
            select(func.coalesce(func.max(EventoLineaTiempo.id_evento), 0))
        ).scalar_one()
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        repository = PostgreSQLPaymentRepository(factory)
        prepare_service = PreparePaymentService(repository)
        authorize_service = AuthorizePaymentService(
            repository,
            DeterministicPaymentAdapter(version="s6-pilot-validation-1"),
        )

        prepare_payload = {"monto": "1250.00"}
        prepared = prepare_service.execute(
            PreparePaymentCommand(
                claim_id=claim_id,
                amount=Decimal("1250.00"),
            ),
            principals[PrincipalRole.OPERADOR],
            idempotency_key=prepare_key,
            request_payload=prepare_payload,
        )
        created["payments"].append(prepared.id)
        require(prepared.status is PaymentStatus.BLOQUEADO, "Estado inicial")
        require(prepared.version == 0, "Versión inicial")
        require(prepared.simulated, "El pago no quedó marcado como simulado")
        require(not prepared.money_transferred, "Se indicó transferencia real")
        print(f"Siniestro probado: {claim_id}")
        print(f"Pago preparado: {prepared.id}")
        print("Preparación con alcance e identidad: OK")
        print("Pago simulado sin transferencia monetaria: OK")

        repeated_prepare = prepare_service.execute(
            PreparePaymentCommand(
                claim_id=claim_id,
                amount=Decimal("1250.00"),
            ),
            principals[PrincipalRole.OPERADOR],
            idempotency_key=prepare_key,
            request_payload=prepare_payload,
        )
        require(repeated_prepare == prepared, "Preparación no idempotente")
        require(
            connection.execute(
                select(func.count(Pago.id_pago)).where(
                    Pago.id_pago == prepared.id
                )
            ).scalar_one() == 1,
            "La repetición duplicó el pago",
        )
        print("Repetición idempotente de preparación: OK")

        try:
            prepare_service.execute(
                PreparePaymentCommand(
                    claim_id=claim_id,
                    amount=Decimal("1300.00"),
                ),
                principals[PrincipalRole.OPERADOR],
                idempotency_key=prepare_key,
                request_payload={"monto": "1300.00"},
            )
        except PaymentOperationError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto idempotente de preparación: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        try:
            authorize_service.execute(
                AuthorizePaymentCommand(
                    claim_id=claim_id,
                    payment_id=prepared.id,
                    expected_version=0,
                ),
                principals[PrincipalRole.OPERADOR],
                idempotency_key=f"s6-payment-operator-{token}",
                request_payload={"version": 0},
            )
        except PaymentOperationError as exc:
            require(
                exc.code == "PAYMENT-AUTHORIZE-FORBIDDEN",
                "Código RBAC inesperado",
            )
            require(exc.status_code == 403, "HTTP RBAC inesperado")
            print("Operador no puede autorizar: HTTP 403 — OK")
        else:
            raise AssertionError("El operador autorizó un pago")

        authorize_payload = {"version": 0}
        authorized = authorize_service.execute(
            AuthorizePaymentCommand(
                claim_id=claim_id,
                payment_id=prepared.id,
                expected_version=0,
            ),
            principals[PrincipalRole.SUPERVISOR],
            idempotency_key=authorize_key,
            request_payload=authorize_payload,
        )
        require(authorized.status is PaymentStatus.EMITIDO, "Estado autorizado")
        require(authorized.version == 1, "Versión autorizada")
        require(
            authorized.preparer_subject
            == principals[PrincipalRole.OPERADOR].subject,
            "Preparador incorrecto",
        )
        require(
            authorized.authorizer_subject
            == principals[PrincipalRole.SUPERVISOR].subject,
            "Autorizador incorrecto",
        )
        require(not authorized.money_transferred, "Se indicó transferencia real")
        print("Supervisor distinto autorizó el pago: OK")
        print("Segregación de funciones: OK")
        print("Versión: 0 -> 1")

        repeated_authorize = authorize_service.execute(
            AuthorizePaymentCommand(
                claim_id=claim_id,
                payment_id=prepared.id,
                expected_version=0,
            ),
            principals[PrincipalRole.SUPERVISOR],
            idempotency_key=authorize_key,
            request_payload=authorize_payload,
        )
        require(repeated_authorize == authorized, "Autorización no idempotente")
        print("Repetición idempotente de autorización: OK")

        stored_payment = connection.execute(
            select(
                Pago.estado,
                Pago.version,
                Pago.id_usuario_prepara,
                Pago.id_autorizacion,
            ).where(Pago.id_pago == prepared.id)
        ).one()
        require(stored_payment.estado == "emitido", "Pago no persistido")
        require(stored_payment.version == 1, "Versión no persistida")
        require(
            stored_payment.id_usuario_prepara == created["users"][0],
            "Preparador no persistido",
        )
        require(
            stored_payment.id_autorizacion is not None,
            "Autorización formal no persistida",
        )
        created["authorizations"].append(stored_payment.id_autorizacion)
        print("Autorización formal persistida: OK")

        blocked = prepare_service.execute(
            PreparePaymentCommand(
                claim_id=claim_id,
                amount=Decimal("750.00"),
            ),
            principals[PrincipalRole.OPERADOR],
            idempotency_key=blocked_key,
            request_payload={"monto": "750.00"},
        )
        created["payments"].append(blocked.id)

        policy_id = connection.execute(
            insert(PoliticaAlerta)
            .values(
                version=f"s6val-{token[:8]}",
                regla_bloqueo={
                    "critica": "bloquear_pago_hasta_revision",
                    "declaracion_automatica_fraude": False,
                },
                vigente_desde=date.today(),
            )
            .returning(PoliticaAlerta.id_politica_alerta)
        ).scalar_one()
        created["policies"].append(policy_id)
        alert_id = connection.execute(
            insert(Alerta)
            .values(
                id_siniestro=claim_id,
                tipo="validacion_pago",
                severidad="critica",
                explicacion=MARKER,
                datos_origen={"sintetico": True},
                fecha=now,
                modelo_o_regla="s6-payment-validation:1",
                id_politica_alerta=policy_id,
                estado_revision="pendiente",
                version=0,
            )
            .returning(Alerta.id_alerta)
        ).scalar_one()
        created["alerts"].append(alert_id)

        try:
            authorize_service.execute(
                AuthorizePaymentCommand(
                    claim_id=claim_id,
                    payment_id=blocked.id,
                    expected_version=0,
                ),
                principals[PrincipalRole.SUPERVISOR],
                idempotency_key=f"s6-payment-critical-{token}",
                request_payload={"version": 0},
            )
        except PaymentOperationError as exc:
            require(
                exc.code == "PAYMENT-BLOCKED-BY-CRITICAL-ALERT",
                "Código de bloqueo inesperado",
            )
            require(exc.status_code == 409, "HTTP de bloqueo inesperado")
            print("Alerta crítica pendiente bloqueó el pago: HTTP 409 — OK")
        else:
            raise AssertionError("La alerta crítica no bloqueó el pago")

        blocked_row = connection.execute(
            select(Pago.estado, Pago.version).where(Pago.id_pago == blocked.id)
        ).one()
        require(blocked_row.estado == "bloqueado", "Pago crítico fue emitido")
        require(blocked_row.version == 0, "Pago crítico cambió de versión")

        created["audits"] = list(
            connection.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento > max_audit,
                    EventoLineaTiempo.id_siniestro == claim_id,
                    EventoLineaTiempo.tipo_evento.in_(
                        ("pago_preparado", "pago_autorizado")
                    ),
                )
            ).scalars()
        )
        require(len(created["audits"]) == 3, "Auditoría atómica incompleta")
        require(
            connection.execute(
                select(
                    func.count(
                        SolicitudPreparacionPagoIdempotente.clave
                    )
                ).where(
                    SolicitudPreparacionPagoIdempotente.clave.in_(
                        (prepare_key, blocked_key)
                    )
                )
            ).scalar_one() == 2,
            "Idempotencia de preparación incompleta",
        )
        require(
            connection.execute(
                select(
                    func.count(
                        SolicitudAutorizacionPagoIdempotente.clave
                    )
                ).where(
                    SolicitudAutorizacionPagoIdempotente.clave
                    == authorize_key
                )
            ).scalar_one() == 1,
            "Idempotencia de autorización incompleta",
        )
        print("Auditoría atómica: OK")
        print("Idempotencia persistente: OK")
        print("S6-BE-01 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

require(claim_id is not None, "No se seleccionó siniestro")
with engine.connect() as verification:
    checks = [
        (Pago.id_pago, created["payments"]),
        (Autorizacion.id_autorizacion, created["authorizations"]),
        (Alerta.id_alerta, created["alerts"]),
        (PoliticaAlerta.id_politica_alerta, created["policies"]),
        (EventoLineaTiempo.id_evento, created["audits"]),
        (AsignacionSiniestro.id_asignacion, created["assignments"]),
        (UsuarioInterno.id_usuario, created["users"]),
    ]
    for column, values in checks:
        if values:
            require(
                not verification.execute(
                    select(column).where(column.in_(values))
                ).scalars().all(),
                f"Residuo detectado en {column}",
            )
    require(
        not verification.execute(
            select(SolicitudPreparacionPagoIdempotente.clave).where(
                SolicitudPreparacionPagoIdempotente.clave.in_(
                    (prepare_key, blocked_key)
                )
            )
        ).scalars().all(),
        "Idempotencia de preparación residual",
    )
    require(
        not verification.execute(
            select(SolicitudAutorizacionPagoIdempotente.clave).where(
                SolicitudAutorizacionPagoIdempotente.clave == authorize_key
            )
        ).scalars().all(),
        "Idempotencia de autorización residual",
    )
    require(
        not verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject.in_(subjects)
            )
        ).scalars().all(),
        "Identidad residual",
    )

print("Pagos y autorización sintéticos eliminados: OK")
print("Alerta y política sintéticas eliminadas: OK")
print("Auditoría e idempotencia eliminadas: OK")
print("Identidades, usuarios y asignación eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S6-BE-01 COMPLETADA")
engine.dispose()
