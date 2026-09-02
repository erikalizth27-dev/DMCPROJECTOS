from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from siniestro_facil.application.assistance_contracts import AssistanceRecord


class ProviderIntegrationDisabled(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProviderDispatch:
    assistance_id: int
    provider_id: int
    idempotency_key: str
    payload: dict[str, object]


class ProviderAdapter(Protocol):
    def dispatch(self, request: ProviderDispatch) -> str: ...


class DisabledProviderAdapter:
    """Impide llamadas externas hasta que S3-DEC-01 sea aprobada."""

    def dispatch(self, request: ProviderDispatch) -> str:
        del request
        raise ProviderIntegrationDisabled(
            "La integración con proveedores no está habilitada"
        )


def dispatch_assistance(
    adapter: ProviderAdapter,
    assistance: AssistanceRecord,
    *,
    idempotency_key: str,
) -> str:
    return adapter.dispatch(
        ProviderDispatch(
            assistance_id=assistance.id,
            provider_id=assistance.provider_id,
            idempotency_key=idempotency_key,
            payload={
                "claim_id": assistance.claim_id,
                "assistance_type": assistance.assistance_type,
                "attempt": assistance.attempt,
            },
        )
    )
