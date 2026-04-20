from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class SubscriptionItem(BaseModel):
    current_period_end: Optional[int] = None


class SubscriptionItems(BaseModel):
    data: List[SubscriptionItem] = []


# Validation schema - validates payload structure
# Make fields optional - validation logic is in the parser
class SubscriptionPayload(BaseModel):
    id: Optional[str] = None
    customer: Optional[str] = None
    status: Optional[str] = None
    items: Optional[SubscriptionItems] = None


# Parsed info returned to service
class SubscriptionCreatedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class SubscriptionUpdatedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str
    is_active: bool


class SubscriptionDeletedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class SubscriptionPausedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    status: str


def _extract_current_period_end(payload: SubscriptionPayload) -> datetime:
    """Extract current_period_end from subscription items."""
    items = payload.items.data
    if not items:
        raise ValueError("No subscription items found in payload")
    return datetime.fromtimestamp(items[0].current_period_end)


def parse_customer_subscription_created(payload: SubscriptionPayload) -> SubscriptionCreatedInfo:
    """Parse customer.subscription.created webhook payload."""
    return SubscriptionCreatedInfo(
        subscription_id=payload.id,
        customer_id=payload.customer,
        current_period_end=_extract_current_period_end(payload),
        status=payload.status,
    )


def parse_customer_subscription_updated(payload: SubscriptionPayload) -> SubscriptionUpdatedInfo:
    """Parse customer.subscription.updated webhook payload."""
    # Statuses that mean subscription is not active
    inactive_statuses = ["paused", "incomplete"]

    return SubscriptionUpdatedInfo(
        subscription_id=payload.id,
        customer_id=payload.customer,
        current_period_end=_extract_current_period_end(payload),
        status=payload.status,
        is_active=payload.status not in inactive_statuses,
    )


def parse_customer_subscription_deleted(payload: SubscriptionPayload) -> SubscriptionDeletedInfo:
    """Parse customer.subscription.deleted webhook payload."""
    return SubscriptionDeletedInfo(
        subscription_id=payload.id,
        customer_id=payload.customer,
        current_period_end=_extract_current_period_end(payload),
        status=payload.status,
    )


def parse_customer_subscription_paused(payload: SubscriptionPayload) -> SubscriptionPausedInfo:
    """Parse customer.subscription.paused webhook payload."""
    return SubscriptionPausedInfo(
        subscription_id=payload.id,
        customer_id=payload.customer,
        status=payload.status,
    )