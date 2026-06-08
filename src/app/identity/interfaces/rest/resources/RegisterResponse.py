from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegisterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(
        min_length=1,
        description="Registered first name",
        examples=["Jose Luis"],
    )
    last_name: str = Field(
        min_length=1,
        description="Registered last name",
        examples=["Quispe Nunez"],
    )
    dni: str = Field(
        min_length=8,
        max_length=8,
        description="Registered Peruvian DNI, exactly 8 digits",
        examples=["12345678"],
    )
    enrolled: bool = Field(
        description="True when all submitted face samples were enrolled",
        examples=[True],
    )
