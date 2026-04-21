from typing import Optional

from pydantic import ValidationError

from core.logger import logger
from core.correlation import set_correlation_id, clear_correlation_id
from parsers.customer import (
    CustomerPayload,
    parse_customer_created,
    parse_customer_deleted,
)
from helpers.context import get_customer_service
from tasks.app import celery_app


def _setup_correlation_context(correlation_id: Optional[str] = None):
    """Setup correlation ID context for logging."""
    if correlation_id:
        set_correlation_id(correlation_id)


def _cleanup_correlation_context():
    """Cleanup correlation ID context."""
    clear_correlation_id()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_created(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.created webhook."""
    _setup_correlation_context(correlation_id)
    try:
        # Validate payload structure
        try:
            data = CustomerPayload(**payload)
        except ValidationError as e:
            logger.warning(f"Invalid customer.created payload: {e}")
            return  # No retry for validation errors

        # Parse to extract needed info
        info = parse_customer_created(data)

        # Execute service
        with get_customer_service() as service:
            service.handle_customer_created(info)
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
def customer_deleted(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle customer.deleted webhook."""
    _setup_correlation_context(correlation_id)
    try:
        # Validate payload structure
        try:
            data = CustomerPayload(**payload)
        except ValidationError as e:
            logger.warning(f"Invalid customer.deleted payload: {e}")
            return  # No retry for validation errors

        # Parse to extract needed info
        info = parse_customer_deleted(data)

        # Execute service
        with get_customer_service() as service:
            service.handle_customer_deleted(info)
    finally:
        _cleanup_correlation_context()