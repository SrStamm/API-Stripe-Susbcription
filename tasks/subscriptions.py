from pydantic import BaseModel, ValidationError

from core.logger import logger
from parsers.subscription import (
    SubscriptionPayload,
    parse_customer_subscription_created,
    parse_customer_subscription_updated,
    parse_customer_subscription_deleted,
    parse_customer_subscription_paused,
)
from helpers.context import get_subscription_service
from tasks.app import celery_app


class CustomerSubBasicPayload(BaseModel):
    id: str


@celery_app.task
def customer_sub_basic(payload: dict):
    """Create free trial subscription for user."""
    # Validate payload structure
    try:
        data = CustomerSubBasicPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer_sub_basic payload: {e}")
        return  # No retry for validation errors

    # Execute service
    with get_subscription_service() as service:
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
    try:
        data = SubscriptionPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.subscription.created payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_subscription_created(data)

    # Execute service
    with get_subscription_service() as service:
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
    try:
        data = SubscriptionPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.subscription.updated payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_subscription_updated(data)

    # Execute service
    with get_subscription_service() as service:
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
    try:
        data = SubscriptionPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.subscription.deleted payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_subscription_deleted(data)

    # Execute service
    with get_subscription_service() as service:
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
    try:
        data = SubscriptionPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.subscription.paused payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_subscription_paused(data)

    # Execute service
    with get_subscription_service() as service:
        service.handle_customer_subscription_paused(info)