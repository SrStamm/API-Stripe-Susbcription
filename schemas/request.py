from datetime import datetime
from pydantic import BaseModel, field_validator

from schemas.enums import SubscriptionTier


class PlanCreate(BaseModel):
    name: str
    description: str
    amount: int
    money: str


class PlanRead(BaseModel):
    id: int
    stripe_price_id: str
    name: str
    description: str | None = None
    price_cents: int
    interval: str


class PlanUpdate(BaseModel):
    id: str
    amount: int | None = None
    money: str | None = None
    name: str | None = None
    description: str | None = None

    @field_validator("id")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        required_prefix = "price_"
        if not v.startswith(required_prefix):
            raise ValueError(f"El ID debe comenzar con el prefijo: {required_prefix}")
        return v


class PlanID(BaseModel):
    id: str

    @field_validator("id")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        required_prefix = "price_"
        if not v.startswith(required_prefix):
            raise ValueError(f"El ID debe comenzar con el prefijo: {required_prefix}")
        return v


class SubID(BaseModel):
    id: str

    @field_validator("id")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        required_prefix = "sub_"
        if not v.startswith(required_prefix):
            raise ValueError(f"El ID debe comenzar con el prefijo: {required_prefix}")
        return v


class SubscriptionCreate(BaseModel):
    tier: SubscriptionTier
    current_period_end: datetime
