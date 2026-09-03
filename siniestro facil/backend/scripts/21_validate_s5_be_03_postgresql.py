from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from itertools import combinations
from uuid import uuid4

from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.detect_case_relations import (
    CandidateCaseFacts,
    CaseRelationError,
    DetectCaseRelationsCommand,
    DetectCaseRelationsService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import RelationCriterion
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.persistence.case_relation_repository import (
    PostgreSQLCaseRelationRepository,
)
from siniestro_facil.persistence.models import (
    EventoLineaTiempo,
    IdentidadActor,
    RelacionCasos,
    Siniestro,
    SolicitudRelacionCasosIdempotente,
    UsuarioInterno,
)


TENANT = "tenant-s5-relations-validation"
KEY = "s5-case-relations-validation-0001"
SECOND_KEY = "s5-case-relations-validation-0002"
CRITERION = RelationCriterion.CUENTA_BANCARIA
RAW_VALUE = "  Cuenta   Piloto  001  "
NORMALIZED = "CUENTA PILOTO 001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
claim_a: int | None = None
claim_b: int | None = None
user_id: int | None = None
relation_id: int | None = None
audit_ids: list[int] = []
subject = f"s5-relations-validation-{uuid4().hex}"

with engine.connect() as connection:
    outer = connection.begin()
    try:
        claim_ids = list(
            connection.execute(
                select(Siniestro.id_siniestro)
                .order_by(Siniestro.id_siniestro)
                .limit(100)
            ).scalars()
        )
        require(len(claim_ids) >= 2, "Se requieren dos siniestros")
        occupied = {
            (row.id_siniestro_a, row.id_siniestro_b)
            for row in connection.execute(
                select(
                    RelacionCasos.id_siniestro_a,
                    RelacionCasos.id_siniestro_b,
                ).where(
                    RelacionCasos.criterio_relacion == CRITERION.value
                )
            )
        }
        pair = next(
            (
                (left, right)
                for left, right in combinations(claim_ids, 2)
                if (left, right) not in occupied
            ),
            None,
        )
        require(pair is not None, "No existe par libre para validar")
        claim_a, claim_b = pair
        now = datetime.now(timezone.utc)

        user_id = connection.execute(
            insert(UsuarioInterno)
            .values(rol=PrincipalRole.INVESTIGADOR_FRAUDE.value)
            .returning(UsuarioInterno.id_usuario)
        ).scalar_one()
        connection.execute(
            insert(IdentidadActor).values(
                subject=subject,
                tenant_id=TENANT,
                actor_type=ActorType.INTERNO.value,
                id_usuario=user_id,
            )
        )
        max_audit = connection.execute(
            select(func.coalesce(func.max(EventoLineaTiempo.id_evento), 0))
        ).scalar_one()
        principal = AuthenticatedPrincipal(
            subject=subject,
            role=PrincipalRole.INVESTIGADOR_FRAUDE,
            actor_type=ActorType.INTERNO,
            tenant_id=TENANT,
            issued_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(hours=1),
            authenticated_at=now - timedelta(minutes=1),
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        service = DetectCaseRelationsService(
            PostgreSQLCaseRelationRepository(factory)
        )
        own = {CRITERION: RAW_VALUE}
        candidate = {CRITERION: "cuenta piloto 001"}
        payload = {
            "valores": {CRITERION.value: RAW_VALUE},
            "candidatos": [
                {
                    "siniestroId": claim_b,
                    "valores": {
                        CRITERION.value: "cuenta piloto 001"
                    },
                }
            ],
        }
        command = DetectCaseRelationsCommand(
            claim_id=claim_a,
            own_values=own,
            candidates=(CandidateCaseFacts(claim_b, candidate),),
        )

        result = service.execute(
            command,
            principal,
            idempotency_key=KEY,
            request_payload=payload,
        )
        require(len(result.relations) == 1, "Relación no generada")
        relation = result.relations[0]
        relation_id = relation.id
        require(
            (relation.claim_a, relation.claim_b) == (claim_a, claim_b),
            "Par no canónico",
        )
        require(
            relation.normalized_value == NORMALIZED,
            "Valor normalizado incorrecto",
        )
        require(
            relation.review_status == "pendiente_revision",
            "Estado de revisión incorrecto",
        )
        stored = connection.execute(
            select(
                RelacionCasos.valor_normalizado,
                RelacionCasos.estado_revision,
            ).where(RelacionCasos.id_relacion == relation_id)
        ).one_or_none()
        require(stored is not None, "Relación no persistida")
        require(stored.valor_normalizado == NORMALIZED, "Valor no persistido")
        require(
            stored.estado_revision == "pendiente_revision",
            "Estado no persistido",
        )
        print(f"Siniestros relacionados: {claim_a} y {claim_b}")
        print(f"Relación candidata: {relation_id}")
        print("Valor exacto normalizado persistido: OK")
        print("Estado pendiente de revisión: OK")

        repeated = service.execute(
            command,
            principal,
            idempotency_key=KEY,
            request_payload=payload,
        )
        require(repeated == result, "Repetición no idempotente")
        print("Repetición idempotente: OK")

        try:
            changed = {
                **payload,
                "candidatos": [
                    {
                        "siniestroId": claim_b,
                        "valores": {
                            CRITERION.value: "cuenta diferente"
                        },
                    }
                ],
            }
            service.execute(
                DetectCaseRelationsCommand(
                    claim_a,
                    own,
                    (
                        CandidateCaseFacts(
                            claim_b,
                            {CRITERION: "cuenta diferente"},
                        ),
                    ),
                ),
                principal,
                idempotency_key=KEY,
                request_payload=changed,
            )
        except CaseRelationError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto idempotente: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        duplicate = service.execute(
            command,
            principal,
            idempotency_key=SECOND_KEY,
            request_payload=payload,
        )
        require(
            duplicate.relations[0].id == relation_id,
            "Se duplicó la relación existente",
        )
        count = connection.execute(
            select(func.count(RelacionCasos.id_relacion)).where(
                RelacionCasos.id_siniestro_a == claim_a,
                RelacionCasos.id_siniestro_b == claim_b,
                RelacionCasos.criterio_relacion == CRITERION.value,
            )
        ).scalar_one()
        require(count == 1, "Existe relación duplicada")
        print("Unicidad por par y criterio: OK")
        print("Expedientes conservados sin fusión: OK")

        audit_ids = list(
            connection.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento > max_audit,
                    EventoLineaTiempo.id_siniestro == claim_a,
                    EventoLineaTiempo.tipo_evento
                    == "relaciones_casos_detectadas",
                )
            ).scalars()
        )
        require(len(audit_ids) == 2, "Auditoría incompleta")
        keys = set(
            connection.execute(
                select(SolicitudRelacionCasosIdempotente.clave).where(
                    SolicitudRelacionCasosIdempotente.clave.in_(
                        (KEY, SECOND_KEY)
                    )
                )
            ).scalars()
        )
        require(keys == {KEY, SECOND_KEY}, "Idempotencia incompleta")
        print("Auditoría atómica: OK")
        print("S5-BE-03 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

with engine.connect() as verification:
    if relation_id is not None:
        require(
            verification.execute(
                select(RelacionCasos.id_relacion).where(
                    RelacionCasos.id_relacion == relation_id
                )
            ).scalar_one_or_none() is None,
            "Relación residual",
        )
    if audit_ids:
        require(
            not verification.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento.in_(audit_ids)
                )
            ).scalars().all(),
            "Auditoría residual",
        )
    require(
        not verification.execute(
            select(SolicitudRelacionCasosIdempotente.clave).where(
                SolicitudRelacionCasosIdempotente.clave.in_(
                    (KEY, SECOND_KEY)
                )
            )
        ).scalars().all(),
        "Idempotencia residual",
    )
    require(
        verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject == subject
            )
        ).scalar_one_or_none() is None,
        "Identidad residual",
    )
    if user_id is not None:
        require(
            verification.execute(
                select(UsuarioInterno.id_usuario).where(
                    UsuarioInterno.id_usuario == user_id
                )
            ).scalar_one_or_none() is None,
            "Usuario residual",
        )

print("Relación candidata eliminada: OK")
print("Auditoría e idempotencia eliminadas: OK")
print("Identidad y usuario sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S5-BE-03 COMPLETADA")
engine.dispose()
