from __future__ import annotations

from uuid import UUID

from src.app.shared.exceptions import ValidationError

UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


def validate_uuid_string(value: str, field_name: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise ValidationError(f"{field_name} cannot be empty")

    try:
        UUID(normalized)
    except ValueError as error:
        raise ValidationError(f"{field_name} must be a valid UUID") from error

    return normalized
