from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.app.iam.domain.model.valueobjects import UserId
from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class IamRefreshToken:
    token_id: str
    user_id: UserId
    token_hash: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None
    replaced_by_token_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "token_id", validate_uuid_string(self.token_id, "token_id"))

        if not self.token_hash.strip():
            raise ValidationError("token_hash cannot be empty")

        if self.expires_at.tzinfo is None:
            raise ValidationError("expires_at must be timezone-aware")

        if self.created_at.tzinfo is None:
            raise ValidationError("created_at must be timezone-aware")

        if self.revoked_at is not None and self.revoked_at.tzinfo is None:
            raise ValidationError("revoked_at must be timezone-aware")

        if self.replaced_by_token_id is not None:
            object.__setattr__(
                self,
                "replaced_by_token_id",
                validate_uuid_string(self.replaced_by_token_id, "replaced_by_token_id"),
            )
