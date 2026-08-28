from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.register_claim import (
    ClaimRegistrationError,
    RegisterClaimCommand,
    RegisteredClaim,
    StoredRequest,
)
from siniestro_facil.infrastructure.policy_adapter import PolicySnapshot
from siniestro_facil.persistence.models import (
    EventoLineaTiempo,
    Poliza,
    Reportante,
    Siniestro,
    SolicitudIdempotente,
    Vehiculo,
)


class PostgreSQLClaimRepository:
    """Persiste el siniestro, la auditoría y la idempotencia en una transacción."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _result_from_row(row: SolicitudIdempotente) -> RegisteredClaim:
        payload = row.respuesta
        return RegisteredClaim(
            id=int(payload["id"]),
            estado_actual=str(payload["estado_actual"]),
            fecha_evento=datetime.fromisoformat(str(payload["fecha_evento"])),
            tipo_evento=str(payload["tipo_evento"]),
            siguiente_paso=str(payload["siguiente_paso"]),
        )

    def find_request(self, idempotency_key: str) -> StoredRequest | None:
        with self._factory() as session:
            row = session.get(SolicitudIdempotente, idempotency_key)
            if row is None:
                return None
            return StoredRequest(row.huella, self._result_from_row(row))

    def create(
        self,
        command: RegisterClaimCommand,
        policy: PolicySnapshot,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> RegisteredClaim:
        try:
            with self._factory() as session, session.begin():
                policy_row = session.execute(
                    select(Poliza).where(Poliza.numero_poliza == policy.numero_poliza)
                ).scalar_one_or_none()
                if policy_row is None:
                    raise ClaimRegistrationError(
                        "POLICY-NOT-PERSISTED",
                        "La póliza validada no existe en la base de datos local",
                        422,
                    )

                vehicle = session.execute(
                    select(Vehiculo).where(
                        Vehiculo.id_poliza == policy_row.id_poliza,
                        Vehiculo.placa == command.placa.strip().upper(),
                    )
                ).scalar_one_or_none()
                if vehicle is None:
                    raise ClaimRegistrationError(
                        "VEHICLE-NOT-PERSISTED",
                        "El vehículo validado no existe en la base de datos local",
                        422,
                    )

                reporter = session.execute(
                    select(Reportante)
                    .where(
                        Reportante.id_asegurado == policy_row.id_asegurado,
                        Reportante.es_titular.is_(True),
                    )
                    .order_by(Reportante.id_reportante)
                    .limit(1)
                ).scalar_one_or_none()
                if reporter is None:
                    reporter = Reportante(
                        id_asegurado=policy_row.id_asegurado,
                        es_titular=True,
                        medio_contacto=command.medio_contacto,
                        relacion_asegurado=None,
                    )
                    session.add(reporter)
                    session.flush()

                now = datetime.now(timezone.utc)
                claim = Siniestro(
                    id_poliza=policy_row.id_poliza,
                    id_vehiculo=vehicle.id_vehiculo,
                    id_reportante=reporter.id_reportante,
                    fecha_evento=command.fecha_evento,
                    ubicacion_evento=command.ubicacion_evento,
                    tipo_evento=command.tipo_evento,
                    estado_actual="reportado",
                    canal_origen="api",
                    creado_en=now,
                    version=0,
                )
                session.add(claim)
                session.flush()

                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim.id_siniestro,
                        id_usuario=None,
                        tipo_evento="siniestro_reportado",
                        fecha=now,
                        detalle={"canal": "api"},
                    )
                )

                result = RegisteredClaim(
                    id=claim.id_siniestro,
                    estado_actual="reportado",
                    fecha_evento=command.fecha_evento,
                    tipo_evento=command.tipo_evento,
                    siguiente_paso="validar_cobertura",
                )
                session.add(
                    SolicitudIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_siniestro=claim.id_siniestro,
                        respuesta={
                            "id": result.id,
                            "estado_actual": result.estado_actual,
                            "fecha_evento": result.fecha_evento.isoformat(),
                            "tipo_evento": result.tipo_evento,
                            "siguiente_paso": result.siguiente_paso,
                        },
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise ClaimRegistrationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise
