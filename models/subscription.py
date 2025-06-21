from datetime import datetime as dt
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .user import Users
from .plan import Plans


class Subscriptions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    plan_id: int = Field(foreign_key="plans.id")
    stripe_subscription_id: str
    status: str
    current_period_end: dt

    user: Users = Relationship(back_populates="subscriptions")
    plan: Plans = Relationship()
