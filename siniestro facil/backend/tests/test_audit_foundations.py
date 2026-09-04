from siniestro_facil.domain.audit import (
    AuditDetailLevel,
    TimelineEvent,
    audit_detail_level,
    project_timeline_event,
)
from siniestro_facil.domain.authorization import PrincipalRole


def sensitive_event() -> TimelineEvent:
    return TimelineEvent(
        event_id=1,
        claim_id=4,
        event_type="alerta_fraude_revisada",
        actor_id=3,
        detail={"explicacion": "Detalle reservado"},
        sensitive=True,
    )


def test_supervisor_receives_complete_audit() -> None:
    view = project_timeline_event(
        sensitive_event(),
        PrincipalRole.SUPERVISOR,
    )
    assert view.detail_level is AuditDetailLevel.COMPLETO
    assert view.detail["explicacion"] == "Detalle reservado"


def test_investigator_receives_sensitive_investigation_detail() -> None:
    view = project_timeline_event(
        sensitive_event(),
        PrincipalRole.INVESTIGADOR_FRAUDE,
    )
    assert view.detail_level is AuditDetailLevel.INVESTIGACION
    assert view.detail["explicacion"] == "Detalle reservado"


def test_operator_receives_redacted_sensitive_event() -> None:
    view = project_timeline_event(
        sensitive_event(),
        PrincipalRole.OPERADOR,
    )
    assert view.detail_level is AuditDetailLevel.OPERATIVO
    assert view.detail == {"resumen": "Información sensible restringida"}


def test_insured_receives_limited_audit_level() -> None:
    assert (
        audit_detail_level(PrincipalRole.ASEGURADO)
        is AuditDetailLevel.LIMITADO
    )


def test_non_sensitive_event_remains_visible_to_operator() -> None:
    event = TimelineEvent(
        event_id=2,
        claim_id=4,
        event_type="evidencia_registrada",
        actor_id=3,
        detail={"tipo": "foto"},
    )
    view = project_timeline_event(event, PrincipalRole.OPERADOR)
    assert view.detail == {"tipo": "foto"}
