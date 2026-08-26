from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Protocol


@dataclass(frozen=True, slots=True)
class PolicySnapshot:
    numero_poliza: str
    numero_documento: str
    placa: str
    vigente_desde: date
    vigente_hasta: date
    deducible: Decimal
    cobertura_activa: bool = True

    def is_active_on(self, event_date: date) -> bool:
        return self.cobertura_activa and self.vigente_desde <= event_date <= self.vigente_hasta


class PolicyLookup(Protocol):
    def find(
        self,
        *,
        numero_poliza: str | None = None,
        numero_documento: str | None = None,
    ) -> PolicySnapshot | None: ...


class InMemoryPolicyAdapter:
    """Adaptador temporal S1-DEC-01; sólo acepta datos sintéticos inyectados."""

    def __init__(self, policies: Iterable[PolicySnapshot]) -> None:
        self._by_policy: dict[str, PolicySnapshot] = {}
        self._by_document: dict[str, PolicySnapshot] = {}
        for policy in policies:
            policy_key = self._normalize(policy.numero_poliza)
            document_key = self._normalize(policy.numero_documento)
            if policy_key in self._by_policy:
                raise ValueError(f"Póliza sintética duplicada: {policy.numero_poliza}")
            if document_key in self._by_document:
                raise ValueError(f"Documento sintético duplicado: {policy.numero_documento}")
            self._by_policy[policy_key] = policy
            self._by_document[document_key] = policy

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("El identificador de consulta no puede estar vacío")
        return normalized

    def find(
        self,
        *,
        numero_poliza: str | None = None,
        numero_documento: str | None = None,
    ) -> PolicySnapshot | None:
        if numero_poliza is None and numero_documento is None:
            raise ValueError("Debe indicar numero_poliza o numero_documento")

        by_policy = (
            self._by_policy.get(self._normalize(numero_poliza))
            if numero_poliza is not None
            else None
        )
        by_document = (
            self._by_document.get(self._normalize(numero_documento))
            if numero_documento is not None
            else None
        )

        if numero_poliza is not None and numero_documento is not None:
            return by_policy if by_policy is not None and by_policy == by_document else None
        return by_policy if numero_poliza is not None else by_document
