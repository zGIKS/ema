from __future__ import annotations

import httpx

from src.app.shared.exceptions import ExternalServiceError


class CloudinaryImageUploadService:
    def __init__(
        self,
        *,
        api_key: str,
        api_secret: str,
        cloud_name: str,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._api_key = api_key.strip()
        self._api_secret = api_secret.strip()
        self._cloud_name = cloud_name.strip()
        self._http_client = http_client

    async def upload_image(
        self,
        *,
        image_bytes: bytes,
        public_id: str,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> str:
        if not image_bytes:
            raise ExternalServiceError("Image payload is empty")
        if not public_id.strip():
            raise ExternalServiceError("Cloudinary public_id is required")

        safe_filename = filename.strip() if filename and filename.strip() else "image"
        safe_content_type = (
            content_type.strip() if content_type and content_type.strip() else "application/octet-stream"
        )

        url = f"https://api.cloudinary.com/v1_1/{self._cloud_name}/image/upload"

        try:
            response = await self._http_client.post(
                url,
                data={"public_id": public_id, "overwrite": "true"},
                files={"file": (safe_filename, image_bytes, safe_content_type)},
                auth=(self._api_key, self._api_secret),
                timeout=30.0,
            )
        except httpx.HTTPError as error:
            raise ExternalServiceError(f"Cloudinary upload failed: {error}") from error

        if response.status_code >= 400:
            detail = response.text.strip() or response.reason_phrase
            raise ExternalServiceError(f"Cloudinary upload failed: {detail}")

        try:
            payload = response.json()
        except ValueError as error:
            raise ExternalServiceError("Cloudinary upload returned invalid JSON") from error

        secure_url = payload.get("secure_url")
        if not isinstance(secure_url, str) or not secure_url.strip():
            raise ExternalServiceError("Cloudinary upload did not return secure_url")

        return secure_url
