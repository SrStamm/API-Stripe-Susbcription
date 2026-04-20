from pydantic import BaseModel

from db.session import get_session
from repositories.plan_repositories import PlanRepository
from repositories.subscription_repositories import SubscriptionRepository
from repositories.user_repositories import UserRepository
from services.subscription_service import SubscriptionService
from parsers.subscription import (
    SubscriptionPayload,
    parse_customer_subscription_created,
    parse_customer_subscription_updated,
    parse_customer_subscription_deleted,
    parse_customer_subscription_paused,
)
from schemas.enums import SubscriptionTier, SubscriptionStatus
from tasks.app import celery_app
from datetime import datetime


class CustomerSubBasicPayload(BaseModel):
    id: str


def _get_subscription_service() -> SubscriptionService:
    """Create SubscriptionService instance for Celery tasks."""
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)
    user_repo = UserRepository(session)
    plan_repo = PlanRepository(session)
    return SubscriptionService(subs_repo, user_repo, plan_repo)


@celery_app.task
def customer_sub_basic(payload: dict):
    """Create free trial subscription for user."""
    # Validate payload structure
    data = CustomerSubBasicPayload(**payload)

    # Execute service
    service = _get_subscription_service()
    service.handle_customer_sub_basic(data.id)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_created(self, payload: dict):
    """Handle customer.subscription.created webhook."""
    # Validate payload structure
    data = SubscriptionPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_subscription_created(data)

    # Execute service
    service = _get_subscription_service()
    service.handle_customer_subscription_created(info)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_updated(self, payload: dict):
    """Handle customer.subscription.updated webhook."""
    # Validate payload structure
    data = SubscriptionPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_subscription_updated(data)

    # Execute service
    service = _get_subscription_service()
    service.handle_customer_subscription_updated(info)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_deleted(self, payload: dict):
    """Handle customer.subscription.deleted webhook."""
    # Validate payload structure
    data = SubscriptionPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_subscription_deleted(data)

    # Execute service
    service = _get_subscription_service()
    service.handle_customer_subscription_deleted(info)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_paused(self, payload: dict):
    """Handle customer.subscription.paused webhook."""
    # Validate payload structure
    data = SubscriptionPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_subscription_paused(data)

    # Execute service
    service = _get_subscription_service()
    service.handle_customer_subscription_paused(info)