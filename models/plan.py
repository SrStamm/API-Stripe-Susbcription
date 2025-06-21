from typing import Optional
from sqlmodel import SQLModel, Field


class Plans(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stripe_price_id: str
    name: str
    description: Optional[str]
    price_cents: int
    interval: str
