from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.detect_case_relations import (
    CaseRelationCandidate,
    CaseRelationError,
    CaseRelationResult,
    StoredRelationRequest,
)
from siniestro_facil.domain.fraud import RelationCriterion
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    EventoLineaTiempo,
    IdentidadActor,
    RelacionCasos,
    Siniestro,
    SolicitudRelacionCasosIdempotente,
)


class PostgreSQLCaseRelationRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _serialize(result: CaseRelationResult) -> dict[str, object]:
        return {
            "claim_id": result.claim_id,
            "relations": [
                {
                    "id": item.id,
                    "claim_a": item.claim_a,
                    "claim_b": item.claim_b,
                    "criterion": item.criterion.value,
                    "normalized_value": item.normalized_value,
                    "review_status": item.review_status,
                }
                for item in result.relations
            ],
        }

    @staticmethod
    def _deserialize(payload: dict[str, object]) -> CaseRelationResult:
        rows = payload.get("relations", [])
        relations = tuple(
            CaseRelationCandidate(
                id=int(row["id"]),
                claim_a=int(row["claim_a"]),
                claim_b=int(row["claim_b"]),
                criterion=RelationCriterion(str(row["criterion"])),
                normalized_value=str(row["normalized_value"]),
                review_status=str(row["review_status"]),
            )
            for row in rows
            if isinstance(row, dict)
        )
        return CaseRelationResult(int(payload["claim_id"]), relations)

    def find_request(
        self, idempotency_key: str
    ) -> StoredRelationRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudRelacionCasosIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            return StoredRelationRequest(
                row.huella,
                self._deserialize(row.respuesta),
            )

    def create(
        self,
        claim_id: int,
        matches: tuple[
            tuple[int, int, RelationCriterion, str], ...
        ],
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> CaseRelationResult:
        try:
            with self._factory() as session, session.begin():
                existing_request = session.get(
                    SolicitudRelacionCasosIdempotente,
                    idempotency_key,
                    with_for_update=True,
                )
                if existing_request is not None:
                    if existing_request.huella == fingerprint:
                        return self._deserialize(existing_request.respuesta)
                    raise CaseRelationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                identity = session.get(
                    IdentidadActor,
                    (principal.subject, principal.tenant_id),
                )
                if identity is None or identity.id_usuario is None:
                    raise CaseRelationError(
                        "CASE-RELATION-FORBIDDEN",
                        "Identidad interna no vinculada",
                        403,
                    )
                claim_ids = {claim_id}
                for claim_a, claim_b, _, _ in matches:
                    claim_ids.update((claim_a, claim_b))
                existing_claims = set(
                    session.execute(
                        select(Siniestro.id_siniestro).where(
                            Siniestro.id_siniestro.in_(claim_ids)
                        )
                    ).scalars()
                )
                if existing_claims != claim_ids:
                    raise CaseRelationError(
                        "CLAIM-NOT-FOUND",
                        "Uno o más siniestros candidatos no existen",
                        404,
                    )

                created: list[CaseRelationCandidate] = []
                for claim_a, claim_b, criterion, value in matches:
                    relation = session.execute(
                        select(RelacionCasos)
                        .where(
                            RelacionCasos.id_siniestro_a == claim_a,
                            RelacionCasos.id_siniestro_b == claim_b,
                            RelacionCasos.criterio_relacion
                            == criterion.value,
                        )
                        .with_for_update()
                    ).scalar_one_or_none()
                    if relation is None:
                        relation = RelacionCasos(
                            id_siniestro_a=claim_a,
                            id_siniestro_b=claim_b,
                            criterio_relacion=criterion.value,
                            valor_normalizado=value,
                            estado_revision="pendiente_revision",
                        )
                        session.add(relation)
                        session.flush()
                    created.append(
                        CaseRelationCandidate(
                            id=relation.id_relacion,
                            claim_a=relation.id_siniestro_a,
                            claim_b=relation.id_siniestro_b,
                            criterion=RelationCriterion(
                                relation.criterio_relacion
                            ),
                            normalized_value=(
                                relation.valor_normalizado or value
                            ),
                            review_status=relation.estado_revision,
                        )
                    )
                result = CaseRelationResult(claim_id, tuple(created))
                now = datetime.now(timezone.utc)
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim_id,
                        id_usuario=identity.id_usuario,
                        tipo_evento="relaciones_casos_detectadas",
                        fecha=now,
                        detalle={
                            "relaciones_generadas": len(created),
                            "id_relaciones": [item.id for item in created],
                            "fusion_automatica": False,
                        },
                    )
                )
                session.add(
                    SolicitudRelacionCasosIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_siniestro=claim_id,
                        respuesta=self._serialize(result),
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise CaseRelationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise
