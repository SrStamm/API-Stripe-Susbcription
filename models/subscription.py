from datetime import datetime as dt, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from schemas.enums import SubscriptionTier
from .user import Users
from .plan import Plans


class Subscriptions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    plan_id: int = Field(foreign_key="plans.id")
    stripe_subscription_id: str
    tier: SubscriptionTier = Field(default=SubscriptionTier.free)
    status: str
    current_period_end: dt

    created_at: dt = Field(default_factory=lambda: dt.now(timezone.utc))
    updated_at: dt = Field(default_factory=lambda: dt.now(timezone.utc))
    canceled_at: Optional[dt] = None

    is_active: bool = Field(default=False)
    user: Users = Relationship(back_populates="subscriptions")
    plan: Plans = Relationship()
