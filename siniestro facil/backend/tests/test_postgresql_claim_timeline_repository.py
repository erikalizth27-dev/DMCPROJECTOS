import inspect

from siniestro_facil.persistence.claim_timeline_repository import (
    PostgreSQLClaimTimelineRepository,
)


def list_source() -> str:
    return inspect.getsource(
        PostgreSQLClaimTimelineRepository.list_visible
    )


def access_source() -> str:
    return inspect.getsource(
        PostgreSQLClaimTimelineRepository.record_sensitive_access
    )


def test_timeline_validates_persisted_identity() -> None:
    source = list_source()
    assert "self._identity(session, principal)" in source
    assert "return None" in source


def test_timeline_applies_private_scope() -> None:
    source = inspect.getsource(
        PostgreSQLClaimTimelineRepository._visible_claim
    )
    assert "Poliza.id_asegurado" in source
    assert "AsignacionSiniestro.finalizado_en.is_(None)" in source
    assert "PrincipalRole.SUPERVISOR" in source


def test_timeline_is_ordered_by_stable_cursor() -> None:
    source = list_source()
    assert "EventoLineaTiempo.id_evento > after_event_id" in source
    assert ".order_by(EventoLineaTiempo.id_evento)" in source


def test_timeline_fetches_one_extra_row_for_pagination() -> None:
    source = list_source()
    assert "statement.limit(page_size + 1)" in source
    assert "rows[:page_size]" in source


def test_timeline_projects_actor_date_and_detail() -> None:
    source = list_source()
    assert "actor_id=row.id_usuario" in source
    assert "occurred_at=row.fecha" in source
    assert "detail=dict(row.detalle or {})" in source


def test_sensitive_event_types_are_classified() -> None:
    source = inspect.getsource(
        PostgreSQLClaimTimelineRepository._sensitive
    )
    assert "SENSITIVE_EVENT_PREFIXES" in source
    assert "startswith" in source


def test_sensitive_access_is_persistently_audited() -> None:
    source = access_source()
    assert 'tipo_evento="consulta_auditoria_sensible"' in source
    assert '"eventos_consultados": list(event_ids)' in source
    assert "with self._factory() as session, session.begin()" in source
