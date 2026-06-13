from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class GetUsageLogsQuery:
    requester_user_id: str
    requester_role: str
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page <= 0:
            raise ValidationError("page must be greater than zero")

        if not 1 <= self.page_size <= 100:
            raise ValidationError("page_size must be between 1 and 100")

        if not self.requester_role.strip():
            raise ValidationError("requester_role cannot be empty")

        object.__setattr__(self, "requester_user_id", validate_uuid_string(self.requester_user_id, "requester_user_id"))
