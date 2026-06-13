from __future__ import annotations

import httpx

from src.app.identity.domain.model.results import DniLookupResult
from src.app.identity.domain.model.valueobjects import PeruvianDni
from src.app.identity.domain.services import DniLookupQueryService
from src.app.shared.exceptions import ValidationError


class DecolectaDniLookupService(DniLookupQueryService):
    def __init__(self, api_key: str, base_url: str, http_client: httpx.AsyncClient) -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._http_client = http_client

    async def handle_lookup_dni(self, dni: PeruvianDni) -> DniLookupResult | None:
        if not self._api_key:
            raise ValidationError("DECOLECTA API key is required")

        url = f"{self._base_url}/v1/reniec/dni"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            response = await self._http_client.get(
                url,
                params={"numero": dni.value},
                headers=headers,
                timeout=15.0,
            )
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        document_number = str(payload.get("document_number", "")).strip()
        first_name = str(payload.get("first_name", "")).strip()
        first_last_name = str(payload.get("first_last_name", "")).strip()
        second_last_name = str(payload.get("second_last_name", "")).strip()
        full_name = str(payload.get("full_name", "")).strip()

        if not document_number or not first_name or not first_last_name:
            return None

        return DniLookupResult(
            document_number=document_number,
            first_name=first_name,
            first_last_name=first_last_name,
            second_last_name=second_last_name,
            full_name=full_name,
        )
