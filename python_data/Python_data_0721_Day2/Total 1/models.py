from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: float = Field(gt=0)

    @field_validator("category")
    @classmethod
    def lower_category(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("category는 비어 있을 수 없습니다.")
        return value
