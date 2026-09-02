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
    """Impide llamadas externas cuando el adaptador no está habilitado."""

    def dispatch(self, request: ProviderDispatch) -> str:
        del request
        raise ProviderIntegrationDisabled(
            "La integración con proveedores no está habilitada"
        )


class SimulatedProviderAdapter:
    """Adaptador determinista aprobado por S3-DEC-01 para el piloto."""

    def __init__(self) -> None:
        self._dispatches: dict[str, ProviderDispatch] = {}

    def dispatch(self, request: ProviderDispatch) -> str:
        previous = self._dispatches.get(request.idempotency_key)
        if previous is not None and previous != request:
            raise ValueError(
                "La clave del proveedor ya fue usada con otro contenido"
            )
        self._dispatches[request.idempotency_key] = request
        return f"SIM-{request.assistance_id:08d}"

    @property
    def dispatches(self) -> tuple[ProviderDispatch, ...]:
        return tuple(self._dispatches.values())


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
