from pydantic import BaseModel


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
    amount: int
    money: str
