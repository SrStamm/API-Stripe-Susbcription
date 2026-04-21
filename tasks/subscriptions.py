from typing import Optional

from pydantic import BaseModel, ValidationError

from core.logger import logger
from core.correlation import set_correlation_id, clear_correlation_id
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


def _setup_correlation_context(correlation_id: Optional[str] = None):
    """Setup correlation ID context for logging."""
    if correlation_id:
        set_correlation_id(correlation_id)


def _cleanup_correlation_context():
    """Cleanup correlation ID context."""
    clear_correlation_id()


@celery_app.task
def customer_sub_basic(payload: dict, correlation_id: Optional[str] = None):
    """Create free trial subscription for user."""
    _setup_correlation_context(correlation_id)
    try:
        # Validate payload structure
        try:
            data = CustomerSubBasicPayload(**payload)
        except ValidationError as e:
            logger.warning(f"Invalid customer_sub_basic payload: {e}")
            return  # No retry for validation errors

        # Execute service
        with get_subscription_service() as service:
            service.handle_customer_sub_basic(data.id)
    finally:
        _cleanup_correlation_context()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_created(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.subscription.created webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_updated(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.subscription.updated webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_deleted(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.subscription.deleted webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_paused(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.subscription.paused webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()